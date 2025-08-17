"""
Configuration settings for E-Commerce Fraud Detection System
Centralized configuration management - Fixed version with proper typing
"""

import os
from pathlib import Path
from typing import Dict, Any, Union, List

# Base paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, LOGS_DIR]:
    directory.mkdir(exist_ok=True, parents=True)

class Config:
    """Main configuration class with proper typing"""
    
    # Data Configuration
    DATA_CONFIG: Dict[str, Union[str, float, int]] = {
        'raw_data_path': str(RAW_DATA_DIR),
        'processed_data_path': str(PROCESSED_DATA_DIR),
        'sample_data_file': 'sample_data.csv',
        'processed_data_file': 'processed_transactions.csv',
        'featured_data_file': 'featured_data.csv',
        'train_size': 0.8,
        'test_size': 0.2,
        'random_state': 42
    }
    
    # Model Configuration
    MODEL_CONFIG: Dict[str, Union[str, int]] = {
        'models_path': str(MODELS_DIR),
        'cv_folds': 5,
        'scoring': 'recall',  # Primary metric for fraud detection
        'random_state': 42,
        'n_jobs': -1  # Use all available cores
    }
    
    # XGBoost Configuration
    XGBOOST_CONFIG: Dict[str, Union[int, float, str]] = {
        'n_estimators': 100,
        'max_depth': 6,
        'learning_rate': 0.1,
        'subsample': 0.8,
        'colsample_bytree': 0.8,
        'scale_pos_weight': 100,  # Handle class imbalance
        'reg_alpha': 0.1,
        'reg_lambda': 1.0,
        'random_state': 42,
        'eval_metric': 'aucpr',
        'early_stopping_rounds': 10
    }
    
    # Isolation Forest Configuration
    ISOLATION_FOREST_CONFIG: Dict[str, Union[int, float]] = {
        'n_estimators': 100,
        'contamination': 0.002,  # Expected fraud rate
        'random_state': 42,
        'n_jobs': -1
    }
    
    # Feature Engineering Configuration
    FEATURE_CONFIG: Dict[str, Union[List[int], List[float], int]] = {
        'velocity_windows': [3600, 86400, 604800],  # 1h, 1d, 7d in seconds
        'amount_bins': [0, 10, 50, 100, 500, 1000, float('inf')],
        'outlier_threshold': 3,  # Z-score threshold
        'min_category_count': 10  # Minimum count for categorical encoding
    }
    
    # API Configuration
    API_CONFIG: Dict[str, Union[str, int]] = {
        'host': '0.0.0.0',
        'port': 8000,
        'workers': 1,
        'timeout': 30,
        'max_requests_per_minute': 1000,
        'model_cache_ttl': 3600  # Cache model for 1 hour
    }
    
    # Database Configuration
    DATABASE_CONFIG: Dict[str, Union[str, bool, int]] = {
        'url': os.getenv('DATABASE_URL', 'sqlite:///fraud_detection.db'),
        'echo': False,  # Set to True for SQL logging
        'pool_size': 5,
        'max_overflow': 10
    }
    
    # Redis Configuration (for caching)
    REDIS_CONFIG: Dict[str, Union[str, bool, int]] = {
        'url': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        'decode_responses': True,
        'socket_timeout': 5
    }
    
    # Logging Configuration
    LOGGING_CONFIG: Dict[str, Any] = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
            'detailed': {
                'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
            }
        },
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': str(LOGS_DIR / 'fraud_detection.log'),
                'formatter': 'detailed'
            }
        },
        'loggers': {
            '': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False
            }
        }
    }
    
    # Monitoring Configuration
    MONITORING_CONFIG: Dict[str, Union[float, Dict[str, str]]] = {
        'drift_threshold': 0.1,  # Threshold for drift detection
        'performance_threshold': 0.05,  # Alert if performance drops by 5%
        'model_retrain_threshold': 0.15,  # Retrain if drift > 15%
        'alert_endpoints': {
            'slack': os.getenv('SLACK_WEBHOOK_URL', ''),
            'email': os.getenv('ALERT_EMAIL', '')
        }
    }
    
    # MLFlow Configuration
    MLFLOW_CONFIG: Dict[str, str] = {
        'tracking_uri': os.getenv('MLFLOW_TRACKING_URI', 'http://localhost:5000'),
        'experiment_name': 'fraud_detection',
        'model_registry_name': 'fraud_detection_model'
    }
    
    # Deployment Configuration
    DEPLOYMENT_CONFIG: Dict[str, Union[str, bool]] = {
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'debug': os.getenv('DEBUG', 'False').lower() == 'true',
        'docker_image': 'fraud-detector:latest',
        'aws_region': os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
        's3_bucket': os.getenv('S3_BUCKET', 'fraud-detection-models')
    }

class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False
    
    # Override for development
    XGBOOST_CONFIG = Config.XGBOOST_CONFIG.copy()
    XGBOOST_CONFIG.update({
        'n_estimators': 50,  # Faster training for development
        'early_stopping_rounds': 5
    })

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    TESTING = False
    
    # Override for production
    XGBOOST_CONFIG = Config.XGBOOST_CONFIG.copy()
    XGBOOST_CONFIG.update({
        'n_estimators': 200,  # More estimators for better performance
        'early_stopping_rounds': 20
    })

class TestingConfig(Config):
    """Testing environment configuration"""
    DEBUG = True
    TESTING = True
    
    # Override for testing
    DATA_CONFIG = Config.DATA_CONFIG.copy()
    DATA_CONFIG.update({
        'sample_data_file': 'test_sample_data.csv'
    })
    
    XGBOOST_CONFIG = Config.XGBOOST_CONFIG.copy()
    XGBOOST_CONFIG.update({
        'n_estimators': 10,  # Very fast for testing
        'early_stopping_rounds': 3
    })

def get_config(environment: str = 'development') -> Config:
    """Get configuration based on environment"""
    if environment is None:
        environment = os.getenv('ENVIRONMENT', 'development')
    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    
    config_class = config_map.get(environment, DevelopmentConfig)
    return config_class()

# Convenience function for getting current config
def get_current_config() -> Config:
    """Get current configuration"""
    return get_config()

# Export commonly used paths
CURRENT_CONFIG = get_current_config()

if __name__ == "__main__":
    config = get_current_config()
    print("🔧 Configuration loaded successfully!")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"Debug mode: {getattr(config, 'DEBUG', False)}")
    print(f"Data path: {config.DATA_CONFIG['raw_data_path']}")
    print(f"Models path: {config.MODEL_CONFIG['models_path']}")