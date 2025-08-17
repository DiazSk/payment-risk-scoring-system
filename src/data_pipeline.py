"""
Data Pipeline for Fraud Detection System
Basic implementation for import compatibility
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Optional

class DataPipeline:
    """Basic data pipeline for fraud detection"""
    
    def __init__(self):
        self.sample_data_cache = None
    
    def generate_sample_data(self, n_samples: int = 10000, fraud_rate: float = 0.0017) -> pd.DataFrame:
        """Generate sample fraud detection data"""
        
        np.random.seed(42)
        
        n_fraud = int(n_samples * fraud_rate)
        n_normal = n_samples - n_fraud
        
        # Generate normal transactions
        normal_data = {
            'transaction_amount': np.random.lognormal(3.5, 0.8, n_normal),
            'transaction_hour': np.random.choice(range(24), n_normal),
            'transaction_day': np.random.randint(1, 32, n_normal),
            'transaction_weekend': np.random.choice([0, 1], n_normal, p=[0.7, 0.3]),
            'is_business_hours': np.random.choice([0, 1], n_normal, p=[0.4, 0.6]),
            'card_amount_mean': np.random.normal(75, 25, n_normal),
            'card_txn_count_recent': np.random.poisson(3, n_normal) + 1,
            'time_since_last_txn': np.random.exponential(3600, n_normal),
            'merchant_risk_score': np.random.beta(2, 8, n_normal),
            'amount_zscore': np.random.normal(0, 1, n_normal),
            'is_amount_outlier': np.zeros(n_normal, dtype=int),
            'is_fraud': np.zeros(n_normal, dtype=int)
        }
        
        # Generate fraud transactions
        fraud_data = {
            'transaction_amount': np.random.lognormal(4.2, 1.2, n_fraud),
            'transaction_hour': np.random.choice(range(24), n_fraud),
            'transaction_day': np.random.randint(1, 32, n_fraud),
            'transaction_weekend': np.random.choice([0, 1], n_fraud),
            'is_business_hours': np.random.choice([0, 1], n_fraud, p=[0.3, 0.7]),
            'card_amount_mean': np.random.normal(65, 30, n_fraud),
            'card_txn_count_recent': np.random.poisson(1, n_fraud) + 1,
            'time_since_last_txn': np.random.exponential(1800, n_fraud),
            'merchant_risk_score': np.random.beta(5, 3, n_fraud),
            'amount_zscore': np.random.normal(2.5, 1.5, n_fraud),
            'is_amount_outlier': np.ones(n_fraud, dtype=int),
            'is_fraud': np.ones(n_fraud, dtype=int)
        }
        
        # Combine all data
        all_data = {}
        for key in normal_data.keys():
            all_data[key] = np.concatenate([normal_data[key], fraud_data[key]])
        
        # Create DataFrame
        df = pd.DataFrame(all_data)
        
        # Add additional padding features to reach 82 total
        current_features = len(df.columns)
        for i in range(current_features, 82):
            df[f'feature_{i}'] = np.random.normal(0, 0.1, len(df))
        
        # Shuffle data
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        return df
