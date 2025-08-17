"""
Model Evaluation Notebook for Fraud Detection System
Comprehensive evaluation of trained models with visualizations
"""

import logging
import os
import re
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import warnings
warnings.filterwarnings('ignore')

# Add project root to path
sys.path.append('..')
sys.path.append('../src')
sys.path.append('../app')

# Configure plotting
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Machine Learning imports
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, precision_recall_curve,
    confusion_matrix, classification_report
)
from sklearn.preprocessing import StandardScaler
import joblib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionSimulator:
    """Generate test transactions for evaluation"""
    def __init__(self):
        self.rng = np.random.RandomState(42)
        
    def generate_test_batch(self, n_transactions: int = 100, fraud_rate: float = 0.02) -> List[Dict[str, Any]]:
        """Generate batch of test transactions with realistic patterns"""
        transactions = []
        n_fraud = int(n_transactions * fraud_rate)
        
        for i in range(n_transactions):
            is_fraud = i < n_fraud
            
            # Generate more realistic transaction features
            if is_fraud:
                # Fraud patterns: high amounts, unusual times, high risk scores
                amount = self.rng.lognormal(6, 1.5)  # Higher amounts
                hour = self.rng.choice([2, 3, 4, 22, 23])  # Unusual hours
                merchant_risk = self.rng.beta(5, 2)  # Higher risk
                amount_zscore = self.rng.normal(3, 1)  # Outlier amounts
            else:
                # Normal patterns
                amount = self.rng.lognormal(4, 1)  # Normal amounts
                hour = self.rng.choice(range(7, 22))  # Business hours
                merchant_risk = self.rng.beta(2, 8)  # Lower risk
                amount_zscore = self.rng.normal(0, 0.5)  # Normal z-scores
            
            card_mean = self.rng.normal(75, 20)
            
            transaction = {
                'transaction_amount': float(amount),
                'transaction_hour': int(hour),
                'transaction_day': self.rng.randint(1, 31),
                'transaction_weekend': int(hour % 7 in [0, 6]),
                'is_business_hours': int(9 <= hour <= 17),
                'card_amount_mean': float(card_mean),
                'card_txn_count_recent': self.rng.poisson(3) + 1,
                'time_since_last_txn': float(self.rng.exponential(3600)),
                'merchant_risk_score': float(merchant_risk),
                'amount_zscore': float(amount_zscore),
                'is_amount_outlier': int(abs(amount_zscore) > 2),
                'actual_fraud': is_fraud
            }
            transactions.append(transaction)
        
        # Shuffle transactions
        self.rng.shuffle(transactions)
        return transactions

class ModelEvaluator:
    """Comprehensive model evaluation system"""
    
    def __init__(self, models_dir: str = "models"):  # Fixed path
        self.models_dir = Path(models_dir)
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        self.results: Dict[str, Dict[str, Any]] = {}
        self.test_data: Optional[pd.DataFrame] = None
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
    def load_models(self) -> bool:
        """Load all trained models and scalers"""
        logger.info("📦 Loading models...")
        
        # Check if models directory exists
        if not self.models_dir.exists():
            print(f"❌ Models directory not found at {self.models_dir.absolute()}")
            return False
        
        # Load metadata
        metadata_path = self.models_dir / "model_metadata.json"
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
            print(f"✅ Loaded metadata for {len(self.metadata.get('models', {}))} models")
        else:
            print(f"⚠️ No metadata found at {metadata_path}")
        
        # Load scalers - CRITICAL FOR PROPER EVALUATION
        scalers_path = self.models_dir / "scalers.pkl"
        if scalers_path.exists():
            self.scalers = joblib.load(scalers_path)
            print(f"✅ Loaded scalers: {list(self.scalers.keys())}")
        else:
            print("⚠️ No scalers found - this may affect model performance")
        
        # Load model files
        model_files = list(self.models_dir.glob("*.pkl"))
        print(f"📁 Found {len(model_files)} .pkl files in {self.models_dir}")
        
        for model_file in model_files:
            if "scaler" not in model_file.stem.lower():
                model_name = model_file.stem.replace("_model", "")
                try:
                    self.models[model_name] = joblib.load(model_file)
                    print(f"✅ Loaded {model_name}")
                except Exception as e:
                    print(f"❌ Failed to load {model_name}: {e}")
        
        if len(self.models) == 0:
            print(f"❌ No models loaded from {self.models_dir.absolute()}")
            print("   Please ensure you have trained models in the 'models' directory")
            print("   Run: python train_fraud_models.py")
        
        return len(self.models) > 0
    
    def generate_test_data(self, n_samples: int = 1000) -> pd.DataFrame:
        """Generate test data for evaluation"""
        print(f"\n🎲 Generating {n_samples} test samples...")
        
        simulator = TransactionSimulator()
        transactions = simulator.generate_test_batch(n_samples, fraud_rate=0.02)
        
        self.test_data = pd.DataFrame(transactions)
        
        # Print data statistics
        fraud_count = self.test_data['actual_fraud'].sum()
        print(f"✅ Generated test data: {self.test_data.shape}")
        print(f"   Fraud samples: {fraud_count} ({fraud_count/len(self.test_data)*100:.1f}%)")
        print(f"   Normal samples: {len(self.test_data) - fraud_count}")
        
        return self.test_data
    
    def prepare_features(self, X: np.ndarray, model_name: str) -> np.ndarray:
        """Prepare features for a specific model (apply scaling if needed)"""
        
        # Check if model needs scaling from metadata
        model_info = self.metadata.get('models', {}).get(model_name, {})
        needs_scaling = model_info.get('scaled_features', False)
        
        # Apply scaling if needed
        if needs_scaling and 'standard' in self.scalers:
            print(f"   Applying StandardScaler for {model_name}")
            X_scaled = self.scalers['standard'].transform(X)
            return X_scaled
        
        return X
    
    def evaluate_model(self, model_name: str, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """Evaluate a single model with proper preprocessing"""
        if model_name not in self.models:
            return {"error": f"Model {model_name} not found"}
        
        model = self.models[model_name]
        
        try:
            # Prepare features (apply scaling if needed)
            X_test_prepared = self.prepare_features(X_test, model_name)
            
            # Special handling for Isolation Forest
            if model_name == 'isolation_forest':
                # Isolation Forest: -1 for anomalies (fraud), 1 for normal
                y_pred_raw = model.predict(X_test_prepared)
                y_pred = (y_pred_raw == -1).astype(int)  # Convert to 0/1
                
                # Get anomaly scores for ROC calculation
                scores = model.score_samples(X_test_prepared)
                # Convert to probability-like scores (lower score = more anomalous = higher fraud prob)
                y_pred_proba = 1 / (1 + np.exp(scores))
            else:
                # Standard classifiers
                if hasattr(model, 'predict_proba'):
                    y_pred_proba = model.predict_proba(X_test_prepared)[:, 1]
                    threshold = self.metadata.get('thresholds', {}).get(model_name, 0.5)
                    y_pred = (y_pred_proba >= threshold).astype(int)
                else:
                    y_pred = model.predict(X_test_prepared)
                    y_pred_proba = y_pred.astype(float)
            
            # Calculate metrics
            metrics = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, zero_division=0),
                'recall': recall_score(y_test, y_pred, zero_division=0),
                'f1_score': f1_score(y_test, y_pred, zero_division=0),
                'roc_auc': roc_auc_score(y_test, y_pred_proba) if len(np.unique(y_test)) > 1 else 0,
                'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
                'predictions': {
                    'y_true': y_test.tolist(),
                    'y_pred': y_pred.tolist(),
                    'y_proba': y_pred_proba.tolist()
                }
            }
            
            return metrics
            
        except Exception as e:
            print(f"   ⚠️ Error evaluating {model_name}: {e}")
            return {"error": str(e)}
    
    def evaluate_all_models(self) -> Dict[str, Dict[str, Any]]:
        """Evaluate all loaded models"""
        print("\n🔬 Evaluating all models...")
        
        if self.test_data is None:
            self.generate_test_data()
        
        # Type guard for type checker
        if self.test_data is None:
            print("❌ Failed to generate test data")
            return {}
        
        # Now test_data is guaranteed to be not None
        test_data = self.test_data
        
        # Prepare features and labels
        feature_cols = [col for col in test_data.columns if col != 'actual_fraud']
        X_test = test_data[feature_cols].values
        y_test = np.array(test_data['actual_fraud'].values)  # Convert to numpy array
        
        print(f"\n📐 Feature dimensions: {X_test.shape}")
        
        # Pad features to 82 if needed (standard feature count for trained models)
        if X_test.shape[1] < 82:
            padding = np.zeros((X_test.shape[0], 82 - X_test.shape[1]))
            X_test = np.hstack([X_test, padding])
            print(f"   Padded features to shape: {X_test.shape}")
        
        # Debug: Check feature statistics
        print(f"\n📊 Feature statistics:")
        print(f"   Mean of first 5 features: {X_test[:, :5].mean(axis=0)}")
        print(f"   Std of first 5 features: {X_test[:, :5].std(axis=0)}")
        
        # Evaluate each model
        for model_name in self.models.keys():
            print(f"\n📊 Evaluating {model_name}...")
            self.results[model_name] = self.evaluate_model(model_name, X_test, y_test)
            
            if 'error' not in self.results[model_name]:
                metrics = self.results[model_name]
                print(f"  ✅ Accuracy: {metrics['accuracy']:.3f}")
                print(f"  ✅ Precision: {metrics['precision']:.3f}")
                print(f"  ✅ Recall: {metrics['recall']:.3f}")
                print(f"  ✅ F1 Score: {metrics['f1_score']:.3f}")
                print(f"  ✅ ROC AUC: {metrics['roc_auc']:.3f}")
                
                # Show confusion matrix details
                cm = metrics['confusion_matrix']
                print(f"  📋 Confusion Matrix: TN={cm[0][0]}, FP={cm[0][1]}, FN={cm[1][0]}, TP={cm[1][1]}")
        
        return self.results
    
    def create_performance_comparison(self) -> pd.DataFrame:
        """Create performance comparison table"""
        comparison_data = []
        
        for model_name, metrics in self.results.items():
            if 'error' not in metrics:
                comparison_data.append({
                    'Model': model_name,
                    'Accuracy': metrics['accuracy'],
                    'Precision': metrics['precision'],
                    'Recall': metrics['recall'],
                    'F1 Score': metrics['f1_score'],
                    'ROC AUC': metrics['roc_auc']
                })
        
        df_comparison = pd.DataFrame(comparison_data)
        if not df_comparison.empty:
            df_comparison = df_comparison.sort_values('F1 Score', ascending=False)
        
        return df_comparison
    
    def calculate_business_metrics(self, cost_per_fraud: float = 100, cost_per_fp: float = 10) -> Dict[str, Dict[str, float]]:
        """Calculate business impact metrics"""
        business_metrics = {}
        
        for model_name, metrics in self.results.items():
            if 'error' in metrics or 'confusion_matrix' not in metrics:
                continue
                
            cm = metrics['confusion_matrix']
            tn, fp, fn, tp = cm[0][0], cm[0][1], cm[1][0], cm[1][1]
            
            # Calculate costs
            fraud_prevented = tp * cost_per_fraud
            fraud_missed = fn * cost_per_fraud
            false_positive_cost = fp * cost_per_fp
            
            # Net savings
            net_savings = fraud_prevented - false_positive_cost
            
            business_metrics[model_name] = {
                'fraud_prevented': fraud_prevented,
                'fraud_missed': fraud_missed,
                'false_positive_cost': false_positive_cost,
                'net_savings': net_savings,
                'roi': net_savings / (false_positive_cost + 1) if false_positive_cost > 0 else net_savings
            }
        
        return business_metrics
    
    def generate_evaluation_report(self) -> str:
        """Generate comprehensive evaluation report without emojis"""
        report = []
        report.append("=" * 60)
        report.append("MODEL EVALUATION REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Model performance summary
        df_comparison = self.create_performance_comparison()
        if not df_comparison.empty:
            report.append("PERFORMANCE SUMMARY:")
            report.append("-" * 40)
            report.append(df_comparison.to_string())
            
            # Best model (without emoji)
            best_model = df_comparison.iloc[0]
            if isinstance(best_model, pd.Series):
                report.append(f"\nBEST MODEL: {best_model['Model']}")
                report.append(f"  F1 Score: {best_model['F1 Score']:.3f}")
                report.append(f"  ROC AUC: {best_model['ROC AUC']:.3f}")
        
        # Business metrics
        business_metrics = self.calculate_business_metrics()
        if business_metrics:
            report.append("\nBUSINESS IMPACT (per 1000 transactions):")
            report.append("-" * 40)
            
            for model, metrics in business_metrics.items():
                report.append(f"\n{model}:")
                report.append(f"  Net Savings: ${metrics['net_savings']:.2f}")
                report.append(f"  ROI: {metrics['roi']:.2f}x")
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)

# Main execution
if __name__ == "__main__":
    print("🚀 Starting Model Evaluation...")
    print(f"📁 Current directory: {Path.cwd()}")
    
    # Initialize evaluator
    evaluator = ModelEvaluator()
    
    # Load models
    if evaluator.load_models():
        print(f"✅ Loaded {len(evaluator.models)} models")
    else:
        print("❌ Failed to load models")
        print("\n💡 Troubleshooting:")
        print("1. Ensure you're running from the project root directory")
        print("2. Check if 'models' directory exists and contains .pkl files")
        print("3. Run training script first: python train_fraud_models.py")
        exit(1)
    
    # Generate test data
    test_data = evaluator.generate_test_data(n_samples=2000)
    
    # Evaluate all models
    results = evaluator.evaluate_all_models()
    
    # Generate and save report
    report = evaluator.generate_evaluation_report()
    print("\n📄 Evaluation Report:")
    print(report)
    
    # Save report
    report_path = Path("reports/evaluation_report.txt")
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n💾 Report saved to {report_path}")
    
    # Save results to JSON
    results_path = Path("reports/evaluation_results.json")
    with open(results_path, 'w', encoding='utf-8') as f:
        # Convert numpy arrays to lists for JSON serialization
        json_results: Dict[str, Dict[str, Any]] = {}
        for model, metrics in results.items():
            json_results[model] = {}
            for key, value in metrics.items():
                if key != 'predictions':  # Skip large prediction arrays
                    json_results[model][key] = value
        json.dump(json_results, f, indent=2)
    print(f"💾 Results saved to {results_path}")