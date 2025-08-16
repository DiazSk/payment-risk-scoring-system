"""
Feature Engineering for E-Commerce Fraud Detection
Creates 25+ sophisticated features for fraud detection models
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from sklearn.preprocessing import StandardScaler, LabelEncoder
import warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FraudFeatureEngineer:
    """
    Advanced feature engineering for fraud detection
    Creates velocity, behavioral, temporal, and risk features
    """
    
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        self.feature_list = []
        
    def create_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create time-based features from transaction datetime"""
        logger.info("Creating temporal features...")
        
        # Ensure we have datetime column
        if 'TransactionDateTime' not in df.columns and 'TransactionDT' in df.columns:
            base_date = datetime(2019, 1, 1)
            df['TransactionDateTime'] = df['TransactionDT'].apply(
                lambda x: base_date + timedelta(seconds=x)
            )
        
        # Extract time components
        df['transaction_hour'] = df['TransactionDateTime'].dt.hour
        df['transaction_day'] = df['TransactionDateTime'].dt.day
        df['transaction_month'] = df['TransactionDateTime'].dt.month
        df['transaction_weekday'] = df['TransactionDateTime'].dt.weekday
        df['transaction_weekend'] = (df['transaction_weekday'] >= 5).astype(int)
        
        # Business hours (9 AM - 5 PM)
        df['is_business_hours'] = ((df['transaction_hour'] >= 9) & 
                                   (df['transaction_hour'] <= 17)).astype(int)
        
        # Late night transactions (11 PM - 6 AM)
        df['is_late_night'] = ((df['transaction_hour'] >= 23) | 
                               (df['transaction_hour'] <= 6)).astype(int)
        
        # Holiday indicator (simplified - major US holidays)
        df['transaction_date'] = df['TransactionDateTime'].dt.date
        holidays = [
            '2019-01-01', '2019-07-04', '2019-12-25',  # New Year, July 4th, Christmas
            '2019-11-28', '2019-12-26'  # Thanksgiving, Boxing Day
        ]
        df['is_holiday'] = df['transaction_date'].astype(str).isin(holidays).astype(int)
        
        # Time since first transaction for each user
        df['days_since_first_transaction'] = df.groupby('card1')['TransactionDT'].transform(
            lambda x: (x - x.min()) / (24 * 3600)  # Convert to days
        )
        
        temporal_features = [
            'transaction_hour', 'transaction_day', 'transaction_month', 
            'transaction_weekday', 'transaction_weekend', 'is_business_hours',
            'is_late_night', 'is_holiday', 'days_since_first_transaction'
        ]
        
        self.feature_list.extend(temporal_features)
        logger.info(f"Created {len(temporal_features)} temporal features")
        
        return df
    
    def create_velocity_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create velocity-based features (transaction frequency)"""
        logger.info("Creating velocity features...")
        
        # Sort by card and time for proper velocity calculation
        df_sorted = df.sort_values(['card1', 'TransactionDT'])
        
        # Simple transaction counting (cumulative and recent)
        df_sorted['card_txn_count_total'] = df_sorted.groupby('card1').cumcount() + 1
        
        # Transaction count in recent transactions (sliding window approach)
        df_sorted['card_txn_count_recent'] = df_sorted.groupby('card1')['TransactionDT'].transform(
            lambda x: x.rolling(window=10, min_periods=1).count()
        )
        
        # Amount aggregations by card
        df_sorted['card_amount_sum_recent'] = df_sorted.groupby('card1')['TransactionAmt'].transform(
            lambda x: x.rolling(window=5, min_periods=1).sum()
        )
        
        df_sorted['card_amount_mean_recent'] = df_sorted.groupby('card1')['TransactionAmt'].transform(
            lambda x: x.rolling(window=5, min_periods=1).mean()
        )
        
        # Email domain velocity (simple counting)
        for email_col in ['P_emaildomain', 'R_emaildomain']:
            if email_col in df_sorted.columns:
                df_sorted[f'{email_col}_txn_count'] = df_sorted.groupby(email_col).cumcount() + 1
        
        # Merchant/Product category velocity
        if 'ProductCD' in df_sorted.columns:
            df_sorted['product_txn_count'] = df_sorted.groupby('ProductCD').cumcount() + 1
        
        # Time between transactions for same card
        df_sorted['time_since_last_txn'] = df_sorted.groupby('card1')['TransactionDT'].diff()
        df_sorted['time_since_last_txn'] = df_sorted['time_since_last_txn'].fillna(0)
        
        # Transaction frequency (transactions per time unit)
        df_sorted['card_avg_time_between_txn'] = df_sorted.groupby('card1')['time_since_last_txn'].transform('mean')
        
        velocity_features = [
            'card_txn_count_total', 'card_txn_count_recent', 
            'card_amount_sum_recent', 'card_amount_mean_recent',
            'P_emaildomain_txn_count', 'R_emaildomain_txn_count',
            'product_txn_count', 'time_since_last_txn', 'card_avg_time_between_txn'
        ]
        
        # Only keep features that actually exist
        velocity_features = [f for f in velocity_features if f in df_sorted.columns]
        self.feature_list.extend(velocity_features)
        
        logger.info(f"Created {len(velocity_features)} velocity features")
        
        return df_sorted
    
    def create_amount_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create transaction amount-based features"""
        logger.info("Creating transaction amount features...")
        
        # Amount percentiles for user
        df['card_amount_mean'] = df.groupby('card1')['TransactionAmt'].transform('mean')
        df['card_amount_std'] = df.groupby('card1')['TransactionAmt'].transform('std')
        df['card_amount_median'] = df.groupby('card1')['TransactionAmt'].transform('median')
        
        # Amount relative to user's typical spending
        df['amount_vs_mean'] = df['TransactionAmt'] / (df['card_amount_mean'] + 1e-8)
        df['amount_vs_median'] = df['TransactionAmt'] / (df['card_amount_median'] + 1e-8)
        
        # Amount anomaly scores
        df['amount_zscore'] = (df['TransactionAmt'] - df['card_amount_mean']) / (df['card_amount_std'] + 1e-8)
        df['is_amount_outlier'] = (np.abs(df['amount_zscore']) > 3).astype(int)
        
        # Round number flags
        df['is_round_amount'] = (df['TransactionAmt'] % 1 == 0).astype(int)
        df['is_even_amount'] = (df['TransactionAmt'] % 2 == 0).astype(int)
        
        # Amount bins
        df['amount_bin'] = pd.cut(df['TransactionAmt'], 
                                  bins=[0, 10, 50, 100, 500, 1000, float('inf')],
                                  labels=['micro', 'small', 'medium', 'large', 'xlarge', 'huge'])
        
        # Product category amount patterns
        if 'ProductCD' in df.columns:
            df['product_amount_mean'] = df.groupby('ProductCD')['TransactionAmt'].transform('mean')
            df['amount_vs_product_mean'] = df['TransactionAmt'] / (df['product_amount_mean'] + 1e-8)
        
        amount_features = [
            'card_amount_mean', 'card_amount_std', 'card_amount_median',
            'amount_vs_mean', 'amount_vs_median', 'amount_zscore',
            'is_amount_outlier', 'is_round_amount', 'is_even_amount',
            'product_amount_mean', 'amount_vs_product_mean'
        ]
        
        # Only keep features that actually exist
        amount_features = [f for f in amount_features if f in df.columns]
        self.feature_list.extend(amount_features)
        
        logger.info(f"Created {len(amount_features)} amount features")
        
        return df
    
    def create_risk_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create risk scores based on historical patterns"""
        logger.info("Creating risk score features...")
        
        # Email domain risk (fraud rate by domain)
        for email_col in ['P_emaildomain', 'R_emaildomain']:
            if email_col in df.columns:
                email_fraud_rate = df.groupby(email_col)['isFraud'].mean()
                df[f'{email_col}_fraud_rate'] = df[email_col].map(email_fraud_rate)
        
        # Card type risk
        if 'card4' in df.columns:
            card_type_fraud_rate = df.groupby('card4')['isFraud'].mean()
            df['card_type_fraud_rate'] = df['card4'].map(card_type_fraud_rate)
        
        # Product category risk
        if 'ProductCD' in df.columns:
            product_fraud_rate = df.groupby('ProductCD')['isFraud'].mean()
            df['product_fraud_rate'] = df['ProductCD'].map(product_fraud_rate)
        
        # Device risk
        if 'DeviceType' in df.columns:
            device_fraud_rate = df.groupby('DeviceType')['isFraud'].mean()
            df['device_fraud_rate'] = df['DeviceType'].map(device_fraud_rate)
        
        # Address risk (based on addr1, addr2)
        if 'addr1' in df.columns and 'addr2' in df.columns:
            df['addr_combo'] = df['addr1'].astype(str) + '_' + df['addr2'].astype(str)
            addr_fraud_rate = df.groupby('addr_combo')['isFraud'].mean()
            df['addr_fraud_rate'] = df['addr_combo'].map(addr_fraud_rate)
        
        # Distance-based risk
        if 'dist1' in df.columns:
            df['is_high_distance'] = (df['dist1'] > df['dist1'].quantile(0.95)).astype(int)
        
        if 'dist2' in df.columns:
            df['is_high_distance2'] = (df['dist2'] > df['dist2'].quantile(0.95)).astype(int)
        
        risk_features = [
            'P_emaildomain_fraud_rate', 'R_emaildomain_fraud_rate',
            'card_type_fraud_rate', 'product_fraud_rate', 'device_fraud_rate',
            'addr_fraud_rate', 'is_high_distance', 'is_high_distance2'
        ]
        
        # Only keep features that actually exist
        risk_features = [f for f in risk_features if f in df.columns]
        self.feature_list.extend(risk_features)
        
        logger.info(f"Created {len(risk_features)} risk score features")
        
        return df
    
    def encode_categorical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical features"""
        logger.info("Encoding categorical features...")
        
        categorical_features = ['card4', 'card6', 'ProductCD', 'M1', 'M2', 'M3', 
                               'DeviceType', 'DeviceInfo', 'amount_bin']
        
        for feature in categorical_features:
            if feature in df.columns:
                le = LabelEncoder()
                df[f'{feature}_encoded'] = le.fit_transform(df[feature].astype(str))
                self.encoders[feature] = le
                self.feature_list.append(f'{feature}_encoded')
        
        logger.info(f"Encoded {len(categorical_features)} categorical features")
        
        return df
    
    def create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create interaction features between important variables"""
        logger.info("Creating interaction features...")
        
        interactions = []
        
        # Amount and time interactions
        if all(f in df.columns for f in ['transaction_hour', 'TransactionAmt']):
            df['amount_x_hour'] = df['TransactionAmt'] * df['transaction_hour']
            interactions.append('amount_x_hour')
        
        # Velocity and amount interactions
        if all(f in df.columns for f in ['card_txn_count_1h', 'TransactionAmt']):
            df['velocity_x_amount'] = df['card_txn_count_1h'] * df['TransactionAmt']
            interactions.append('velocity_x_amount')
        
        # Weekend and amount interaction
        if all(f in df.columns for f in ['transaction_weekend', 'TransactionAmt']):
            df['weekend_x_amount'] = df['transaction_weekend'] * df['TransactionAmt']
            interactions.append('weekend_x_amount')
        
        self.feature_list.extend(interactions)
        logger.info(f"Created {len(interactions)} interaction features")
        
        return df
    
    def run_feature_engineering(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """Run complete feature engineering pipeline"""
        logger.info("🚀 Starting feature engineering pipeline...")
        
        # Create temporal features
        df = self.create_temporal_features(df)
        
        # Create velocity features
        df = self.create_velocity_features(df)
        
        # Create amount features
        df = self.create_amount_features(df)
        
        # Create risk scores
        df = self.create_risk_scores(df)
        
        # Encode categorical features
        df = self.encode_categorical_features(df)
        
        # Create interaction features
        df = self.create_interaction_features(df)
        
        # Fill any remaining NaN values
        numeric_features = df.select_dtypes(include=[np.number]).columns
        df[numeric_features] = df[numeric_features].fillna(0)
        
        # Remove intermediate columns we don't need
        columns_to_drop = ['TransactionDateTime', 'transaction_date', 'addr_combo']
        existing_drop_cols = [col for col in columns_to_drop if col in df.columns]
        df = df.drop(columns=existing_drop_cols)
        
        logger.info(f"✅ Feature engineering completed! Created {len(self.feature_list)} features")
        logger.info(f"📊 Final dataset shape: {df.shape}")
        
        return df, self.feature_list
    
    def get_feature_importance_data(self, df: pd.DataFrame) -> Dict:
        """Get feature statistics for importance analysis"""
        feature_stats = {}
        
        for feature in self.feature_list:
            if feature in df.columns:
                feature_stats[feature] = {
                    'mean': df[feature].mean(),
                    'std': df[feature].std(),
                    'min': df[feature].min(),
                    'max': df[feature].max(),
                    'fraud_correlation': df[feature].corr(df['isFraud']) if 'isFraud' in df.columns else None
                }
        
        return feature_stats

def main():
    """Test the feature engineering pipeline"""
    from data_pipeline import FraudDataPipeline
    
    # Load data
    pipeline = FraudDataPipeline()
    df = pipeline.load_data()
    
    # Run feature engineering
    feature_engineer = FraudFeatureEngineer()
    df_features, feature_list = feature_engineer.run_feature_engineering(df)
    
    print(f"\n🎯 Feature Engineering Results:")
    print(f"Original features: {df.shape[1]}")
    print(f"New features created: {len(feature_list)}")
    print(f"Final dataset shape: {df_features.shape}")
    
    print(f"\n📋 Feature List:")
    for i, feature in enumerate(feature_list, 1):
        print(f"{i:2d}. {feature}")
    
    # Save processed data with features
    output_path = "data/processed/featured_data.csv"
    df_features.to_csv(output_path, index=False)
    print(f"\n✅ Featured dataset saved to {output_path}")

if __name__ == "__main__":
    main()