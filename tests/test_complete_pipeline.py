#!/usr/bin/env python3
"""
Complete Pipeline Test Script
Tests the entire data pipeline and feature engineering process
Run this to verify everything is working before proceeding to model training
"""

import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# Add src to path
sys.path.append('src')

# Import our modules
from data_pipeline import FraudDataPipeline
from feature_engineering import FraudFeatureEngineer
from utils import DataUtils, MetricsUtils, VisualizationUtils, setup_project_logging

# Setup logging
setup_project_logging()
logger = logging.getLogger(__name__)

def test_project_structure():
    """Test that all required directories and files exist"""
    logger.info("🔍 Testing project structure...")
    
    required_dirs = [
        'src', 'data', 'data/raw', 'data/processed', 
        'models', 'config', 'app', 'dashboard'
    ]
    
    required_files = [
        'requirements.txt', 'src/data_pipeline.py', 
        'src/feature_engineering.py', 'src/utils.py'
    ]
    
    missing_dirs = []
    missing_files = []
    
    for directory in required_dirs:
        if not Path(directory).exists():
            missing_dirs.append(directory)
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_dirs or missing_files:
        logger.error(f"❌ Missing directories: {missing_dirs}")
        logger.error(f"❌ Missing files: {missing_files}")
        return False
    
    logger.info("✅ Project structure looks good!")
    return True

def test_data_pipeline():
    """Test the data pipeline functionality"""
    logger.info("🔍 Testing data pipeline...")
    
    try:
        # Initialize pipeline
        pipeline = FraudDataPipeline()
        
        # Generate sample data
        df = pipeline.generate_sample_data(n_samples=10000)  # Smaller for testing
        
        # Verify data structure
        assert len(df) == 10000, f"Expected 10000 rows, got {len(df)}"
        assert 'isFraud' in df.columns, "Missing target column 'isFraud'"
        assert df['isFraud'].sum() > 0, "No fraudulent transactions generated"
        
        fraud_rate = df['isFraud'].mean()
        assert 0.001 <= fraud_rate <= 0.005, f"Fraud rate {fraud_rate:.4f} outside expected range"
        
        # Test data cleaning
        df_clean = pipeline.clean_data(df)
        assert len(df_clean) <= len(df), "Data cleaning should not increase rows"
        
        # Save test data
        pipeline.save_processed_data(df_clean, "test_processed_data.csv")
        
        logger.info(f"✅ Data pipeline test passed! Generated {len(df_clean)} clean transactions")
        return df_clean
        
    except Exception as e:
        logger.error(f"❌ Data pipeline test failed: {e}")
        return None

def test_feature_engineering(df):
    """Test feature engineering functionality"""
    logger.info("🔍 Testing feature engineering...")
    
    try:
        # Initialize feature engineer
        feature_engineer = FraudFeatureEngineer()
        
        # Run feature engineering
        df_features, feature_list = feature_engineer.run_feature_engineering(df)
        
        # Verify features were created
        assert len(feature_list) >= 20, f"Expected at least 20 features, got {len(feature_list)}"
        assert df_features.shape[1] > df.shape[1], "No new features were created"
        
        # Check for key feature categories
        temporal_features = [f for f in feature_list if 'transaction_' in f or 'hour' in f or 'day' in f]
        velocity_features = [f for f in feature_list if 'txn_count' in f or 'velocity' in f]
        amount_features = [f for f in feature_list if 'amount' in f]
        
        assert len(temporal_features) > 0, "No temporal features created"
        assert len(velocity_features) > 0, "No velocity features created"
        assert len(amount_features) > 0, "No amount features created"
        
        # Check for missing values in key features
        key_features = feature_list[:10]  # Check first 10 features
        for feature in key_features:
            if feature in df_features.columns:
                missing_pct = df_features[feature].isnull().mean()
                assert missing_pct < 0.1, f"Feature {feature} has {missing_pct:.2%} missing values"
        
        # Save featured data
        output_path = "data/processed/test_featured_data.csv"
        df_features.to_csv(output_path, index=False)
        
        logger.info(f"✅ Feature engineering test passed! Created {len(feature_list)} features")
        logger.info(f"📊 Final dataset shape: {df_features.shape}")
        
        return df_features, feature_list
        
    except Exception as e:
        logger.error(f"❌ Feature engineering test failed: {e}")
        return None, None

def test_data_analysis(df, feature_list):
    """Test data analysis utilities"""
    logger.info("🔍 Testing data analysis utilities...")
    
    try:
        # Test class imbalance analysis
        y = df['isFraud']
        class_analysis = DataUtils.analyze_class_imbalance(y)
        
        assert 'imbalance_ratio' in class_analysis, "Missing imbalance ratio"
        assert class_analysis['minority_class'] == 1, "Fraud should be minority class"
        
        # Test feature-target split
        X, y = DataUtils.split_features_target(df)
        assert len(X.columns) == len(df.columns) - 1, "Incorrect feature split"
        assert len(y) == len(df), "Incorrect target split"
        
        # Test numeric/categorical feature detection
        numeric_features = DataUtils.get_numeric_features(df)
        categorical_features = DataUtils.get_categorical_features(df)
        
        assert len(numeric_features) > 0, "No numeric features detected"
        assert 'TransactionAmt' in numeric_features, "TransactionAmt should be numeric"
        
        logger.info(f"✅ Data analysis test passed!")
        logger.info(f"   - Imbalance ratio: {class_analysis['imbalance_ratio']:.1f}:1")
        logger.info(f"   - Numeric features: {len(numeric_features)}")
        logger.info(f"   - Categorical features: {len(categorical_features)}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Data analysis test failed: {e}")
        return False

def generate_summary_report(df, feature_list):
    """Generate a summary report of the pipeline test"""
    logger.info("📋 Generating summary report...")
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'dataset_info': {
            'total_transactions': len(df),
            'fraudulent_transactions': int(df['isFraud'].sum()),
            'fraud_rate': df['isFraud'].mean(),
            'dataset_shape': df.shape
        },
        'feature_info': {
            'total_features': len(feature_list),
            'original_features': len(df.columns) - len(feature_list),
            'engineered_features': len(feature_list),
            'feature_categories': {
                'temporal': len([f for f in feature_list if any(word in f for word in ['hour', 'day', 'weekend', 'holiday'])]),
                'velocity': len([f for f in feature_list if 'txn_count' in f]),
                'amount': len([f for f in feature_list if 'amount' in f]),
                'risk': len([f for f in feature_list if 'fraud_rate' in f or 'risk' in f])
            }
        },
        'data_quality': {
            'missing_values_pct': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
            'duplicate_transactions': 0,  # After cleaning
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024**2)
        }
    }
    
    # Save report
    report_path = "data/processed/pipeline_test_report.txt"
    with open(report_path, 'w') as f:
        f.write("FRAUD DETECTION PIPELINE TEST REPORT\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Test Date: {report['timestamp']}\n\n")
        
        f.write("DATASET SUMMARY:\n")
        f.write(f"  Total Transactions: {report['dataset_info']['total_transactions']:,}\n")
        f.write(f"  Fraudulent: {report['dataset_info']['fraudulent_transactions']:,}\n")
        f.write(f"  Fraud Rate: {report['dataset_info']['fraud_rate']:.4%}\n")
        f.write(f"  Shape: {report['dataset_info']['dataset_shape']}\n\n")
        
        f.write("FEATURE ENGINEERING:\n")
        f.write(f"  Total Features: {report['feature_info']['total_features']}\n")
        f.write(f"  Engineered Features: {report['feature_info']['engineered_features']}\n")
        f.write("  Feature Categories:\n")
        for category, count in report['feature_info']['feature_categories'].items():
            f.write(f"    - {category.capitalize()}: {count}\n")
        f.write("\n")
        
        f.write("DATA QUALITY:\n")
        f.write(f"  Missing Values: {report['data_quality']['missing_values_pct']:.2f}%\n")
        f.write(f"  Memory Usage: {report['data_quality']['memory_usage_mb']:.2f} MB\n\n")
        
        f.write("CREATED FEATURES:\n")
        for i, feature in enumerate(feature_list, 1):
            f.write(f"  {i:2d}. {feature}\n")
    
    logger.info(f"📊 Summary report saved to {report_path}")
    
    return report

def main():
    """Run complete pipeline test"""
    print("🚀 FRAUD DETECTION PIPELINE TEST")
    print("=" * 50)
    
    start_time = datetime.now()
    
    # Test 1: Project Structure
    if not test_project_structure():
        print("❌ Project structure test failed. Please run setup_project.py first.")
        return False
    
    # Test 2: Data Pipeline
    df = test_data_pipeline()
    if df is None:
        print("❌ Data pipeline test failed. Cannot continue.")
        return False
    
    # Test 3: Feature Engineering
    df_features, feature_list = test_feature_engineering(df)
    if df_features is None:
        print("❌ Feature engineering test failed. Cannot continue.")
        return False
    
    # Test 4: Data Analysis
    if not test_data_analysis(df_features, feature_list):
        print("❌ Data analysis test failed.")
        return False
    
    # Generate summary report
    report = generate_summary_report(df_features, feature_list)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 50)
    print(f"⏱️  Total time: {duration:.1f} seconds")
    print(f"📊 Dataset: {len(df_features):,} transactions with {len(feature_list)} features")
    print(f"🎯 Fraud rate: {df_features['isFraud'].mean():.4%}")
    print(f"💾 Memory usage: {report['data_quality']['memory_usage_mb']:.1f} MB")
    print("\n📁 Files created:")
    print("   - data/processed/test_processed_data.csv")
    print("   - data/processed/test_featured_data.csv")
    print("   - data/processed/pipeline_test_report.txt")
    print("\n🎯 Ready for model training phase!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)