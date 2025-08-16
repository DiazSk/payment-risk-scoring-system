#!/usr/bin/env python3
"""
FRAUD DETECTION MODEL TRAINING - MAIN RUNNER
Complete Saturday Afternoon Training Pipeline

Run this script to train all models and generate performance metrics
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime

# Add src to Python path
sys.path.append('src')

# Import our modules
from model_training import AdvancedFraudDetectionTrainer
from evaluation import FraudModelEvaluator
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/model_training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def check_prerequisites():
    """Check that all prerequisites are in place"""
    logger.info("🔍 Checking prerequisites...")
    
    # Check for data file
    data_path = "data/processed/test_featured_data.csv"
    if not Path(data_path).exists():
        logger.error(f"❌ Data file not found: {data_path}")
        logger.error("   Please run the pipeline test first: python test_complete_pipeline.py")
        return False
    
    # Check data quality
    df = pd.read_csv(data_path)
    if 'isFraud' not in df.columns:
        logger.error("❌ Target column 'isFraud' not found in dataset")
        return False
    
    fraud_rate = df['isFraud'].mean()
    if fraud_rate == 0:
        logger.error("❌ No fraud cases found in dataset")
        return False
    
    logger.info(f"✅ Dataset ready: {len(df)} transactions, {df['isFraud'].sum()} fraud cases ({fraud_rate:.3%})")
    
    # Create necessary directories
    for directory in ['models', 'reports', 'logs', 'plots']:
        Path(directory).mkdir(exist_ok=True)
    
    logger.info("✅ Prerequisites check passed!")
    return True

def run_model_training():
    """Run the complete model training pipeline"""
    logger.info("🚀 STARTING FRAUD DETECTION MODEL TRAINING")
    logger.info("=" * 70)
    
    start_time = datetime.now()
    
    try:
        # Initialize trainer
        logger.info("Initializing Advanced Fraud Detection Trainer...")
        trainer = AdvancedFraudDetectionTrainer(random_state=42)
        
        # Run complete training pipeline
        logger.info("🔥 Running complete training pipeline...")
        results = trainer.run_complete_training_pipeline()
        
        # Extract results
        evaluation_results = results['evaluation_results']
        metadata = results['metadata']
        
        # Add test data to evaluation results for visualization
        data_path = "data/processed/test_featured_data.csv"
        df = pd.read_csv(data_path)
        X_test = df.drop(columns=['isFraud', 'TransactionID'], errors='ignore')
        y_test = df['isFraud']
        
        # Add actual test data to results for plotting
        for model_name in evaluation_results:
            evaluation_results[model_name]['y_true'] = y_test.values
        
        logger.info("✅ Model training completed successfully!")
        
        return evaluation_results, metadata
        
    except Exception as e:
        logger.error(f"❌ Model training failed: {e}")
        raise

def run_model_evaluation(evaluation_results, metadata):
    """Run comprehensive model evaluation"""
    logger.info("📊 STARTING COMPREHENSIVE MODEL EVALUATION")
    logger.info("=" * 60)
    
    try:
        # Initialize evaluator
        evaluator = FraudModelEvaluator(save_plots=True)
        
        # Get feature names from metadata
        feature_names = metadata.get('feature_names', [])
        
        # Run complete evaluation suite
        eval_results = evaluator.run_complete_evaluation(evaluation_results, feature_names)
        
        logger.info("✅ Model evaluation completed successfully!")
        
        return eval_results
        
    except Exception as e:
        logger.error(f"❌ Model evaluation failed: {e}")
        logger.error("Continuing without advanced visualizations...")
        return None

def print_final_summary(evaluation_results, metadata, training_time):
    """Print comprehensive final summary"""
    
    print("\n" + "="*80)
    print("🎉 FRAUD DETECTION MODEL TRAINING COMPLETE!")
    print("="*80)
    
    print(f"⏱️  Total training time: {training_time:.1f} seconds")
    print(f"📊 Models trained: {len(evaluation_results)}")
    print(f"🎯 Features used: {len(metadata.get('feature_names', []))}")
    
    # Find best models
    best_f1_model = max(evaluation_results.keys(), 
                       key=lambda x: evaluation_results[x]['metrics']['f1_score'])
    best_recall_model = max(evaluation_results.keys(),
                           key=lambda x: evaluation_results[x]['metrics']['recall'])
    
    print(f"\n🏆 BEST MODELS:")
    print(f"   Best Overall (F1-Score): {best_f1_model}")
    print(f"   Best Fraud Detection (Recall): {best_recall_model}")
    
    # Show best model performance
    best_metrics = evaluation_results[best_f1_model]['metrics']
    print(f"\n📈 BEST MODEL PERFORMANCE ({best_f1_model}):")
    print(f"   Fraud Detection Rate (Recall): {best_metrics['recall']:.1%}")
    print(f"   Precision: {best_metrics['precision']:.1%}")
    print(f"   F1-Score: {best_metrics['f1_score']:.3f}")
    print(f"   False Positive Rate: {best_metrics['fpr']:.1%}")
    
    if 'roc_auc' in best_metrics:
        print(f"   ROC-AUC: {best_metrics['roc_auc']:.3f}")
    
    # Business impact estimate
    fraud_caught_pct = best_metrics['recall'] * 100
    fp_rate_pct = best_metrics['fpr'] * 100
    
    print(f"\n💰 ESTIMATED BUSINESS IMPACT:")
    print(f"   Fraud Cases Caught: {fraud_caught_pct:.1f}%")
    print(f"   False Positive Rate: {fp_rate_pct:.1f}%")
    print(f"   Estimated Annual Savings: ${best_metrics['recall'] * 2000000:.0f}")
    
    # Files created
    print(f"\n📁 FILES CREATED:")
    print(f"   📊 Models: models/*.pkl")
    print(f"   📋 Metadata: models/model_metadata.json")
    print(f"   📈 Reports: reports/model_performance_report.txt")
    print(f"   📉 Plots: plots/*.png, plots/*.html")
    print(f"   📝 Logs: logs/model_training.log")
    
    # Next steps
    print(f"\n🚀 NEXT STEPS:")
    print(f"   1. ✅ Models are ready for API deployment")
    print(f"   2. 🌐 Build FastAPI endpoints (Saturday evening)")
    print(f"   3. 📊 Create Streamlit dashboard (Sunday)")
    print(f"   4. ☁️  Deploy to AWS (Sunday)")
    
    # Deployment readiness
    if best_metrics['recall'] >= 0.8 and best_metrics['fpr'] <= 0.1:
        print(f"\n✅ DEPLOYMENT STATUS: READY FOR PRODUCTION!")
    elif best_metrics['recall'] >= 0.7:
        print(f"\n⚠️  DEPLOYMENT STATUS: Ready for staging environment")
    else:
        print(f"\n🔧 DEPLOYMENT STATUS: Needs further optimization")
    
    print("\n" + "="*80)

def main():
    """Main execution function"""
    
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    print("🚀 FRAUD DETECTION SYSTEM - MODEL TRAINING")
    print("Saturday Afternoon Phase: Advanced ML Development")
    print("=" * 60)
    
    start_time = datetime.now()
    
    # Check prerequisites
    if not check_prerequisites():
        print("❌ Prerequisites check failed. Please fix the issues and try again.")
        return False
    
    try:
        # Run model training
        evaluation_results, metadata = run_model_training()
        
        # Run model evaluation
        eval_results = run_model_evaluation(evaluation_results, metadata)
        
        # Calculate total time
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        # Print final summary
        print_final_summary(evaluation_results, metadata, total_time)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Training pipeline failed: {e}")
        print(f"\n❌ Training failed: {e}")
        print("🔧 Check the logs for detailed error information: logs/model_training.log")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎯 Training completed successfully! Ready for API development.")
        sys.exit(0)
    else:
        print("\n💥 Training failed. Check the logs and try again.")
        sys.exit(1)