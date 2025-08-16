"""
Advanced Model Training for E-Commerce Fraud Detection
XGBoost + Isolation Forest Ensemble with Professional Evaluation
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
import joblib
from datetime import datetime
from typing import Dict, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

# Core ML imports
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, 
    precision_recall_curve, roc_curve, average_precision_score,
    precision_score, recall_score, f1_score, accuracy_score
)

# Advanced ML models
import xgboost as xgb
from sklearn.ensemble import IsolationForest, RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression

# Handle class imbalance
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

# Plotting
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedFraudDetectionTrainer:
    """
    Advanced fraud detection model trainer with ensemble methods,
    hyperparameter tuning, and comprehensive evaluation
    """
    
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.models = {}
        self.scalers = {}
        self.performance_metrics = {}
        self.feature_importance = {}
        
        # Set up paths
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
        
        # Model configurations
        self.model_configs = self._get_model_configs()
    
    def _get_model_configs(self) -> Dict:
        """Get optimized model configurations"""
        return {
            'xgboost': {
                'model': xgb.XGBClassifier(
                    random_state=self.random_state,
                    eval_metric='aucpr',
                    early_stopping_rounds=10,
                    verbose=False
                ),
                'params': {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [4, 6, 8],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'subsample': [0.8, 0.9, 1.0],
                    'colsample_bytree': [0.8, 0.9, 1.0],
                    'scale_pos_weight': [10, 50, 100]  # Handle class imbalance
                }
            },
            'isolation_forest': {
                'model': IsolationForest(
                    random_state=self.random_state,
                    n_jobs=-1
                ),
                'params': {
                    'n_estimators': [100, 200],
                    'contamination': [0.001, 0.002, 0.005],  # Expected fraud rate
                    'max_features': [0.8, 1.0]
                }
            },
            'random_forest': {
                'model': RandomForestClassifier(
                    random_state=self.random_state,
                    n_jobs=-1,
                    class_weight='balanced'
                ),
                'params': {
                    'n_estimators': [100, 200],
                    'max_depth': [10, 20, None],
                    'min_samples_split': [2, 5],
                    'min_samples_leaf': [1, 2]
                }
            },
            'logistic_regression': {
                'model': LogisticRegression(
                    random_state=self.random_state,
                    max_iter=1000,
                    class_weight='balanced'
                ),
                'params': {
                    'C': [0.1, 1.0, 10.0],
                    'penalty': ['l1', 'l2'],
                    'solver': ['liblinear']
                }
            }
        }
    
    def load_and_prepare_data(self, data_path: str = "data/processed/test_featured_data.csv") -> Tuple[np.array, np.array]:
        """Load and prepare data for training"""
        logger.info(f"Loading data from {data_path}")
        
        # Load data
        df = pd.read_csv(data_path)
        logger.info(f"Loaded {len(df)} transactions with {df.columns.size} features")
        
        # Separate features and target
        if 'isFraud' not in df.columns:
            raise ValueError("Target column 'isFraud' not found in dataset")
        
        X = df.drop(columns=['isFraud', 'TransactionID'], errors='ignore')
        y = df['isFraud']
        
        # Handle any remaining categorical columns
        for col in X.select_dtypes(include=['object']).columns:
            X[col] = pd.Categorical(X[col]).codes
        
        # Handle missing values
        X = X.fillna(X.median())
        
        logger.info(f"Prepared dataset: {X.shape} features, {y.value_counts().to_dict()} class distribution")
        
        return X.values, y.values
    
    def create_train_test_split(self, X: np.array, y: np.array) -> Tuple:
        """Create stratified train/test split"""
        logger.info("Creating train/test split...")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=0.2, 
            random_state=self.random_state, 
            stratify=y
        )
        
        logger.info(f"Training set: {X_train.shape} - Fraud rate: {y_train.mean():.4f}")
        logger.info(f"Test set: {X_test.shape} - Fraud rate: {y_test.mean():.4f}")
        
        return X_train, X_test, y_train, y_test
    
    def apply_smote_resampling(self, X_train: np.array, y_train: np.array) -> Tuple[np.array, np.array]:
        """Apply SMOTE for handling class imbalance"""
        logger.info("Applying SMOTE resampling...")
        
        # Calculate appropriate sampling strategy
        fraud_count = np.sum(y_train == 1)
        normal_count = np.sum(y_train == 0)
        
        # Don't oversample too much - aim for 1:10 ratio instead of 1:500+
        target_fraud_count = min(normal_count // 10, fraud_count * 5)
        sampling_strategy = {1: target_fraud_count}
        
        smote = SMOTE(random_state=self.random_state, sampling_strategy=sampling_strategy)
        X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
        
        logger.info(f"After SMOTE - Fraud cases: {np.sum(y_train_resampled == 1)}, "
                   f"Normal cases: {np.sum(y_train_resampled == 0)}")
        logger.info(f"New fraud rate: {y_train_resampled.mean():.4f}")
        
        return X_train_resampled, y_train_resampled
    
    def train_individual_models(self, X_train: np.array, y_train: np.array, 
                               X_val: np.array, y_val: np.array) -> Dict:
        """Train individual models with hyperparameter tuning"""
        logger.info("🚀 Training individual models with hyperparameter tuning...")
        
        trained_models = {}
        
        # Scale features for models that need it
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        self.scalers['standard'] = scaler
        
        for model_name, config in self.model_configs.items():
            logger.info(f"Training {model_name.replace('_', ' ').title()}...")
            
            try:
                if model_name == 'isolation_forest':
                    # Isolation Forest is unsupervised, handle differently
                    model = self._train_isolation_forest(X_train_scaled, y_train, config)
                else:
                    # Use appropriate data (scaled or not)
                    train_X = X_train_scaled if model_name in ['logistic_regression'] else X_train
                    val_X = X_val_scaled if model_name in ['logistic_regression'] else X_val
                    
                    # Grid search with cross-validation
                    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=self.random_state)
                    
                    grid_search = GridSearchCV(
                        config['model'],
                        config['params'],
                        cv=cv,
                        scoring='recall',  # Focus on catching fraud
                        n_jobs=-1,
                        verbose=1
                    )
                    
                    grid_search.fit(train_X, y_train)
                    model = grid_search.best_estimator_
                    
                    logger.info(f"Best params for {model_name}: {grid_search.best_params_}")
                    logger.info(f"Best CV score: {grid_search.best_score_:.4f}")
                
                trained_models[model_name] = model
                
                # Evaluate on validation set
                val_X_eval = X_val_scaled if model_name in ['logistic_regression'] else X_val
                self._evaluate_individual_model(model, val_X_eval, y_val, model_name)
                
            except Exception as e:
                logger.error(f"Failed to train {model_name}: {e}")
                continue
        
        logger.info(f"✅ Trained {len(trained_models)} models successfully")
        return trained_models
    
    def _train_isolation_forest(self, X_train: np.array, y_train: np.array, config: Dict):
        """Train Isolation Forest with proper contamination setting"""
        contamination = y_train.mean() * 2  # Set contamination based on actual fraud rate
        
        model = IsolationForest(
            contamination=contamination,
            random_state=self.random_state,
            n_estimators=200,
            n_jobs=-1
        )
        
        model.fit(X_train)
        return model
    
    def _evaluate_individual_model(self, model, X_val: np.array, y_val: np.array, model_name: str):
        """Evaluate individual model performance"""
        try:
            if hasattr(model, 'predict_proba'):
                y_pred_proba = model.predict_proba(X_val)[:, 1]
                y_pred = (y_pred_proba > 0.5).astype(int)
            elif hasattr(model, 'decision_function'):
                scores = model.decision_function(X_val)
                y_pred = (scores < 0).astype(int) if 'isolation' in model_name else (scores > 0).astype(int)
                y_pred_proba = None
            else:
                y_pred = model.predict(X_val)
                y_pred_proba = None
            
            # Calculate metrics
            metrics = {
                'accuracy': accuracy_score(y_val, y_pred),
                'precision': precision_score(y_val, y_pred, zero_division=0),
                'recall': recall_score(y_val, y_pred),
                'f1_score': f1_score(y_val, y_pred, zero_division=0)
            }
            
            if y_pred_proba is not None:
                metrics['roc_auc'] = roc_auc_score(y_val, y_pred_proba)
                metrics['pr_auc'] = average_precision_score(y_val, y_pred_proba)
            
            self.performance_metrics[model_name] = metrics
            
            logger.info(f"{model_name} - Recall: {metrics['recall']:.4f}, "
                       f"Precision: {metrics['precision']:.4f}, F1: {metrics['f1_score']:.4f}")
            
        except Exception as e:
            logger.warning(f"Could not evaluate {model_name}: {e}")
    
    def create_ensemble_model(self, trained_models: Dict, X_train: np.array, y_train: np.array) -> Any:
        """Create ensemble model combining XGBoost and other top performers"""
        logger.info("🔧 Creating ensemble model...")
        
        # Select best models for ensemble (excluding isolation forest for voting)
        voting_models = []
        for name, model in trained_models.items():
            if name != 'isolation_forest' and hasattr(model, 'predict_proba'):
                voting_models.append((name, model))
        
        if len(voting_models) < 2:
            logger.warning("Not enough models for ensemble, using best single model")
            return trained_models.get('xgboost', list(trained_models.values())[0])
        
        # Create voting classifier
        ensemble = VotingClassifier(
            estimators=voting_models,
            voting='soft',  # Use predicted probabilities
            n_jobs=-1
        )
        
        # Train ensemble
        train_X = self.scalers['standard'].transform(X_train)
        ensemble.fit(train_X, y_train)
        
        logger.info(f"✅ Ensemble created with {len(voting_models)} models")
        return ensemble
    
    def evaluate_models(self, models: Dict, X_test: np.array, y_test: np.array) -> Dict:
        """Comprehensive model evaluation"""
        logger.info("📊 Running comprehensive model evaluation...")
        
        evaluation_results = {}
        
        for model_name, model in models.items():
            logger.info(f"Evaluating {model_name}...")
            
            try:
                # Prepare test data
                if model_name in ['logistic_regression', 'ensemble']:
                    X_test_eval = self.scalers['standard'].transform(X_test)
                else:
                    X_test_eval = X_test
                
                # Make predictions
                if hasattr(model, 'predict_proba'):
                    y_pred_proba = model.predict_proba(X_test_eval)[:, 1]
                    
                    # Optimize threshold for best F1 score
                    thresholds = np.arange(0.1, 0.9, 0.1)
                    best_f1 = 0
                    best_threshold = 0.5
                    
                    for threshold in thresholds:
                        y_pred_thresh = (y_pred_proba >= threshold).astype(int)
                        f1 = f1_score(y_test, y_pred_thresh)
                        if f1 > best_f1:
                            best_f1 = f1
                            best_threshold = threshold
                    
                    y_pred = (y_pred_proba >= best_threshold).astype(int)
                    
                elif model_name == 'isolation_forest':
                    y_pred = model.predict(X_test_eval)
                    y_pred = (y_pred == -1).astype(int)  # Convert anomalies to fraud
                    y_pred_proba = model.score_samples(X_test_eval)  # Anomaly scores
                    best_threshold = 0
                else:
                    y_pred = model.predict(X_test_eval)
                    y_pred_proba = None
                    best_threshold = 0.5
                
                # Calculate comprehensive metrics
                metrics = self._calculate_comprehensive_metrics(
                    y_test, y_pred, y_pred_proba, best_threshold
                )
                
                evaluation_results[model_name] = {
                    'model': model,
                    'predictions': y_pred,
                    'probabilities': y_pred_proba,
                    'threshold': best_threshold,
                    'metrics': metrics
                }
                
                # Log key metrics
                logger.info(f"{model_name} Results:")
                logger.info(f"  Recall: {metrics['recall']:.4f}")
                logger.info(f"  Precision: {metrics['precision']:.4f}")
                logger.info(f"  F1-Score: {metrics['f1_score']:.4f}")
                logger.info(f"  False Positive Rate: {metrics['fpr']:.4f}")
                
            except Exception as e:
                logger.error(f"Failed to evaluate {model_name}: {e}")
                continue
        
        return evaluation_results
    
    def _calculate_comprehensive_metrics(self, y_true: np.array, y_pred: np.array, 
                                        y_pred_proba: np.array, threshold: float) -> Dict:
        """Calculate comprehensive evaluation metrics"""
        
        # Basic classification metrics
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
        
        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, zero_division=0),
            'recall': recall_score(y_true, y_pred),
            'f1_score': f1_score(y_true, y_pred, zero_division=0),
            'specificity': tn / (tn + fp) if (tn + fp) > 0 else 0,
            'fpr': fp / (fp + tn) if (fp + tn) > 0 else 0,
            'fnr': fn / (fn + tp) if (fn + tp) > 0 else 0,
            'true_positives': int(tp),
            'false_positives': int(fp),
            'true_negatives': int(tn),
            'false_negatives': int(fn),
            'threshold': threshold
        }
        
        # Add AUC metrics if probabilities available
        if y_pred_proba is not None and len(np.unique(y_true)) > 1:
            try:
                metrics['roc_auc'] = roc_auc_score(y_true, y_pred_proba)
                metrics['pr_auc'] = average_precision_score(y_true, y_pred_proba)
            except:
                pass
        
        return metrics
    
    def save_models_and_results(self, evaluation_results: Dict, feature_names: list):
        """Save trained models and evaluation results"""
        logger.info("💾 Saving models and results...")
        
        # Save individual models
        for model_name, results in evaluation_results.items():
            model_path = self.models_dir / f"{model_name}_model.pkl"
            joblib.dump(results['model'], model_path)
            logger.info(f"Saved {model_name} to {model_path}")
        
        # Save scalers
        if self.scalers:
            scaler_path = self.models_dir / "scalers.pkl"
            joblib.dump(self.scalers, scaler_path)
            logger.info(f"Saved scalers to {scaler_path}")
        
        # Create model metadata
        metadata = {
            'training_date': datetime.now().isoformat(),
            'feature_count': len(feature_names),
            'feature_names': feature_names,
            'models': {},
            'performance_summary': {}
        }
        
        # Add model information
        for model_name, results in evaluation_results.items():
            metadata['models'][model_name] = {
                'type': type(results['model']).__name__,
                'threshold': results['threshold'],
                'file_path': f"{model_name}_model.pkl"
            }
            
            metadata['performance_summary'][model_name] = results['metrics']
        
        # Save metadata
        metadata_path = self.models_dir / "model_metadata.json"
        import json
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        logger.info(f"Saved metadata to {metadata_path}")
        
        return metadata
    
    def generate_performance_report(self, evaluation_results: Dict) -> str:
        """Generate comprehensive performance report"""
        logger.info("📋 Generating performance report...")
        
        report = []
        report.append("# FRAUD DETECTION MODEL PERFORMANCE REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Model comparison table
        report.append("## MODEL COMPARISON")
        report.append("-" * 40)
        report.append(f"{'Model':<20} {'Recall':<8} {'Precision':<10} {'F1-Score':<8} {'FPR':<6}")
        report.append("-" * 40)
        
        for model_name, results in evaluation_results.items():
            metrics = results['metrics']
            report.append(
                f"{model_name:<20} "
                f"{metrics['recall']:<8.4f} "
                f"{metrics['precision']:<10.4f} "
                f"{metrics['f1_score']:<8.4f} "
                f"{metrics['fpr']:<6.4f}"
            )
        
        # Find best model
        best_model = max(evaluation_results.keys(), 
                        key=lambda x: evaluation_results[x]['metrics']['f1_score'])
        best_metrics = evaluation_results[best_model]['metrics']
        
        report.append("")
        report.append("## BEST MODEL DETAILS")
        report.append("-" * 30)
        report.append(f"Best Model: {best_model}")
        report.append(f"Recall (Fraud Detection): {best_metrics['recall']:.4f}")
        report.append(f"Precision: {best_metrics['precision']:.4f}")
        report.append(f"F1-Score: {best_metrics['f1_score']:.4f}")
        report.append(f"False Positive Rate: {best_metrics['fpr']:.4f}")
        report.append(f"True Positives: {best_metrics['true_positives']}")
        report.append(f"False Positives: {best_metrics['false_positives']}")
        report.append(f"False Negatives: {best_metrics['false_negatives']}")
        
        if 'roc_auc' in best_metrics:
            report.append(f"ROC-AUC: {best_metrics['roc_auc']:.4f}")
            report.append(f"PR-AUC: {best_metrics['pr_auc']:.4f}")
        
        # Business impact
        report.append("")
        report.append("## BUSINESS IMPACT ANALYSIS")
        report.append("-" * 35)
        
        fraud_caught = best_metrics['recall']
        false_positive_rate = best_metrics['fpr']
        
        report.append(f"Fraud Detection Rate: {fraud_caught:.1%}")
        report.append(f"False Positive Rate: {false_positive_rate:.1%}")
        report.append(f"Estimated Annual Savings: ${fraud_caught * 1000000:.0f}")
        report.append(f"Estimated False Positive Cost: ${false_positive_rate * 500000:.0f}")
        
        # Save report
        report_text = "\n".join(report)
        report_path = self.reports_dir / "model_performance_report.txt"
        with open(report_path, 'w') as f:
            f.write(report_text)
        
        logger.info(f"Performance report saved to {report_path}")
        return report_text
    
    def run_complete_training_pipeline(self, data_path: str = None) -> Dict:
        """Run the complete model training pipeline"""
        logger.info("🚀 STARTING COMPLETE MODEL TRAINING PIPELINE")
        logger.info("=" * 60)
        
        # Load and prepare data
        if data_path is None:
            data_path = "data/processed/test_featured_data.csv"
        
        X, y = self.load_and_prepare_data(data_path)
        
        # Create train/test split
        X_train, X_test, y_train, y_test = self.create_train_test_split(X, y)
        
        # Apply SMOTE resampling
        X_train_resampled, y_train_resampled = self.apply_smote_resampling(X_train, y_train)
        
        # Create validation split from resampled training data
        X_train_final, X_val, y_train_final, y_val = train_test_split(
            X_train_resampled, y_train_resampled, 
            test_size=0.2, random_state=self.random_state, stratify=y_train_resampled
        )
        
        # Train individual models
        trained_models = self.train_individual_models(
            X_train_final, y_train_final, X_val, y_val
        )
        
        # Create ensemble
        if len(trained_models) > 1:
            ensemble_model = self.create_ensemble_model(trained_models, X_train_final, y_train_final)
            trained_models['ensemble'] = ensemble_model
        
        # Evaluate all models on test set
        evaluation_results = self.evaluate_models(trained_models, X_test, y_test)
        
        # Generate feature names
        data_df = pd.read_csv(data_path)
        feature_names = [col for col in data_df.columns if col not in ['isFraud', 'TransactionID']]
        
        # Save models and results
        metadata = self.save_models_and_results(evaluation_results, feature_names)
        
        # Generate performance report
        report = self.generate_performance_report(evaluation_results)
        
        logger.info("✅ TRAINING PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info(f"🎯 Best Model: {max(evaluation_results.keys(), key=lambda x: evaluation_results[x]['metrics']['f1_score'])}")
        
        return {
            'evaluation_results': evaluation_results,
            'metadata': metadata,
            'performance_report': report
        }

def main():
    """Main training execution"""
    trainer = AdvancedFraudDetectionTrainer()
    results = trainer.run_complete_training_pipeline()
    
    print("\n🎉 MODEL TRAINING COMPLETE!")
    print("=" * 50)
    print("📁 Files created:")
    print("   - models/*.pkl (trained models)")
    print("   - models/model_metadata.json")
    print("   - reports/model_performance_report.txt")
    print("\n🚀 Ready for API development!")

if __name__ == "__main__":
    main()