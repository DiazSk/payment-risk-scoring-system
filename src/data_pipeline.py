"""
Data Pipeline for E-Commerce Fraud Detection System
Handles data ingestion, cleaning, and preprocessing
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FraudDataPipeline:
    """
    Complete data pipeline for fraud detection
    Handles data loading, cleaning, validation, and preparation
    """
    
    def __init__(self, data_path: str = "data/raw"):
        self.data_path = Path(data_path)
        self.processed_path = Path("data/processed")
        self.processed_path.mkdir(exist_ok=True)
        
    def generate_sample_data(self, n_samples: int = 284807) -> pd.DataFrame:
        """
        Generate realistic sample e-commerce transaction data
        Mimics the IEEE-CIS Fraud Detection dataset structure
        """
        logger.info(f"Generating {n_samples} sample transactions...")
        
        np.random.seed(42)  # For reproducibility
        
        # Define realistic ranges and categories
        merchants = [
            'amazon', 'walmart', 'target', 'bestbuy', 'macys', 'nordstrom',
            'ebay', 'etsy', 'apple', 'google', 'microsoft', 'samsung',
            'nike', 'adidas', 'zara', 'h&m', 'starbucks', 'mcdonalds'
        ]
        
        product_categories = [
            'electronics', 'clothing', 'home_garden', 'sports', 'books',
            'beauty', 'automotive', 'groceries', 'jewelry', 'toys'
        ]
        
        payment_methods = ['credit_card', 'debit_card', 'paypal', 'apple_pay', 'google_pay']
        
        countries = ['US', 'CA', 'UK', 'DE', 'FR', 'IT', 'ES', 'AU', 'JP', 'BR']
        devices = ['desktop', 'mobile', 'tablet']
        browsers = ['chrome', 'firefox', 'safari', 'edge', 'opera']
        
        # Generate base data
        data = {
            'TransactionID': [f'T_{i:08d}' for i in range(n_samples)],
            'TransactionDT': np.random.randint(0, 31536000, n_samples),  # Seconds in a year
            'TransactionAmt': self._generate_transaction_amounts(n_samples),
            'ProductCD': np.random.choice(product_categories, n_samples),
            'card1': np.random.randint(1000, 9999, n_samples),  # Card identifier
            'card2': np.random.randint(100, 999, n_samples),
            'card3': np.random.randint(100, 999, n_samples),
            'card4': np.random.choice(['visa', 'mastercard', 'amex', 'discover'], n_samples),
            'card5': np.random.randint(100, 999, n_samples),
            'card6': np.random.choice(['credit', 'debit'], n_samples),
            'addr1': np.random.randint(1, 999, n_samples),  # Address codes
            'addr2': np.random.randint(1, 99, n_samples),
            'dist1': np.random.exponential(scale=50, size=n_samples),  # Distance features
            'dist2': np.random.exponential(scale=30, size=n_samples),
            'P_emaildomain': np.random.choice(['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com'], n_samples),
            'R_emaildomain': np.random.choice(['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com'], n_samples),
            'C1': np.random.exponential(scale=5, size=n_samples),  # Count features
            'C2': np.random.exponential(scale=3, size=n_samples),
            'C3': np.random.exponential(scale=2, size=n_samples),
            'C4': np.random.exponential(scale=1, size=n_samples),
            'D1': np.random.exponential(scale=100, size=n_samples),  # Timedelta features
            'D2': np.random.exponential(scale=200, size=n_samples),
            'D3': np.random.exponential(scale=150, size=n_samples),
            'M1': np.random.choice(['T', 'F'], n_samples),  # Match features
            'M2': np.random.choice(['T', 'F'], n_samples),
            'M3': np.random.choice(['T', 'F'], n_samples),
            'V1': np.random.normal(0, 1, n_samples),  # Vesta features
            'V2': np.random.normal(0, 1, n_samples),
            'V3': np.random.normal(0, 1, n_samples),
            'id_01': np.random.uniform(0, 1, n_samples),  # Identity features
            'id_02': np.random.uniform(0, 100, n_samples),
            'id_03': np.random.uniform(0, 1, n_samples),
            'DeviceType': np.random.choice(devices, n_samples),
            'DeviceInfo': np.random.choice(browsers, n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Generate fraud labels (0.17% fraud rate)
        fraud_rate = 0.0017
        n_fraud = int(n_samples * fraud_rate)
        
        # Create fraud labels
        fraud_labels = np.zeros(n_samples)
        fraud_indices = np.random.choice(n_samples, n_fraud, replace=False)
        fraud_labels[fraud_indices] = 1
        
        # Make fraudulent transactions more suspicious
        df.loc[fraud_indices, 'TransactionAmt'] *= np.random.uniform(2, 10, n_fraud)  # Higher amounts
        df.loc[fraud_indices, 'C1'] *= np.random.uniform(3, 8, n_fraud)  # Higher frequency
        df.loc[fraud_indices, 'dist1'] *= np.random.uniform(5, 15, n_fraud)  # Unusual distances
        
        df['isFraud'] = fraud_labels.astype(int)
        
        logger.info(f"Generated {len(df)} transactions with {df['isFraud'].sum()} fraudulent cases ({df['isFraud'].mean():.3%} fraud rate)")
        
        return df
    
    def _generate_transaction_amounts(self, n_samples: int) -> np.array:
        """Generate realistic transaction amounts with multiple modes"""
        # Mix of different transaction types
        small_purchases = np.random.lognormal(mean=3, sigma=0.5, size=int(n_samples * 0.6))  # $20-200
        medium_purchases = np.random.lognormal(mean=5, sigma=0.3, size=int(n_samples * 0.3))  # $100-500
        large_purchases = np.random.lognormal(mean=7, sigma=0.4, size=int(n_samples * 0.1))  # $500-5000
        
        amounts = np.concatenate([small_purchases, medium_purchases, large_purchases])
        np.random.shuffle(amounts)
        
        return np.round(amounts[:n_samples], 2)
    
    def load_data(self, filename: str = "sample_data.csv") -> pd.DataFrame:
        """Load transaction data from CSV file"""
        file_path = self.data_path / filename
        
        if not file_path.exists():
            logger.warning(f"Data file not found at {file_path}. Generating sample data...")
            df = self.generate_sample_data()
            df.to_csv(file_path, index=False)
            logger.info(f"Sample data saved to {file_path}")
            return df
        
        logger.info(f"Loading data from {file_path}")
        df = pd.read_csv(file_path)
        logger.info(f"Loaded {len(df)} transactions")
        
        return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate transaction data"""
        logger.info("Starting data cleaning...")
        
        initial_rows = len(df)
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['TransactionID'], keep='first')
        logger.info(f"Removed {initial_rows - len(df)} duplicate transactions")
        
        # Handle missing values
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        categorical_columns = df.select_dtypes(include=['object']).columns
        
        # Fill numeric missing values with median
        for col in numeric_columns:
            if df[col].isnull().sum() > 0:
                df[col].fillna(df[col].median(), inplace=True)
        
        # Fill categorical missing values with mode or 'unknown'
        for col in categorical_columns:
            if df[col].isnull().sum() > 0:
                mode_value = df[col].mode()
                fill_value = mode_value[0] if len(mode_value) > 0 else 'unknown'
                df[col].fillna(fill_value, inplace=True)
        
        # Remove transactions with invalid amounts
        df = df[df['TransactionAmt'] > 0]
        df = df[df['TransactionAmt'] < 50000]  # Remove extremely large transactions
        
        # Convert datetime if needed
        if 'TransactionDT' in df.columns:
            # Convert seconds to datetime (assuming epoch start)
            base_date = datetime(2019, 1, 1)
            df['TransactionDateTime'] = df['TransactionDT'].apply(
                lambda x: base_date + timedelta(seconds=x)
            )
        
        logger.info(f"Data cleaning completed. Final dataset: {len(df)} transactions")
        
        return df
    
    def save_processed_data(self, df: pd.DataFrame, filename: str = "processed_transactions.csv"):
        """Save processed data"""
        file_path = self.processed_path / filename
        df.to_csv(file_path, index=False)
        logger.info(f"Processed data saved to {file_path}")
        
        # Save basic statistics
        stats_path = self.processed_path / "data_summary.txt"
        with open(stats_path, 'w') as f:
            f.write("Dataset Summary\n")
            f.write("=" * 50 + "\n")
            f.write(f"Total transactions: {len(df)}\n")
            f.write(f"Fraudulent transactions: {df['isFraud'].sum()}\n")
            f.write(f"Fraud rate: {df['isFraud'].mean():.4%}\n")
            f.write(f"Average transaction amount: ${df['TransactionAmt'].mean():.2f}\n")
            f.write(f"Median transaction amount: ${df['TransactionAmt'].median():.2f}\n")
            f.write("\nColumn Info:\n")
            f.write(str(df.dtypes))
        
        logger.info(f"Data summary saved to {stats_path}")
    
    def run_pipeline(self, filename: str = "sample_data.csv") -> pd.DataFrame:
        """Run the complete data pipeline"""
        logger.info("🚀 Starting fraud detection data pipeline...")
        
        # Load data
        df = self.load_data(filename)
        
        # Clean data
        df_clean = self.clean_data(df)
        
        # Save processed data
        self.save_processed_data(df_clean)
        
        logger.info("✅ Data pipeline completed successfully!")
        
        return df_clean

def main():
    """Main execution function"""
    pipeline = FraudDataPipeline()
    df = pipeline.run_pipeline()
    
    print("\n📊 Dataset Overview:")
    print(f"Shape: {df.shape}")
    print(f"Fraud rate: {df['isFraud'].mean():.4%}")
    print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    print("\n🎯 Top 10 rows preview:")
    print(df.head(10))

if __name__ == "__main__":
    main()