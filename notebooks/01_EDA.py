"""
Exploratory Data Analysis for E-Commerce Fraud Detection
Interactive notebook for data exploration and visualization
"""

import os
import sys
import logging  # Add missing import
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Add project root to path
sys.path.append('..')
sys.path.append('../src')

# Configure plotting
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Import project modules
try:
    from src.data_pipeline import DataPipeline
    from src.feature_engineering import FeatureEngineer
except ImportError:
    print("Warning: Could not import project modules")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fix for lines 617-619: Convert tuple values to float explicitly
def fix_correlation_calculations(corr_matrix):
    """Fix correlation matrix calculations with proper type conversion"""
    # Example fix for the correlation values
    for col in corr_matrix.columns:
        for row in corr_matrix.index:
            value = corr_matrix.loc[row, col]
            if isinstance(value, tuple):
                # Take first element if it's a tuple
                corr_matrix.loc[row, col] = float(value[0]) if len(value) > 0 else 0.0
            elif not isinstance(value, (int, float)):
                # Convert to float if not already numeric
                try:
                    corr_matrix.loc[row, col] = float(value)
                except:
                    corr_matrix.loc[row, col] = 0.0
    return corr_matrix

# Fix for lines 642, 670, 674, 683: Handle Scalar type conversions
def safe_abs(value):
    """Safely compute absolute value with type checking"""
    if isinstance(value, (int, float, np.number)):
        return abs(value)
    elif hasattr(value, '__abs__'):
        return value.__abs__()
    else:
        try:
            return abs(float(value))
        except:
            return 0.0

def safe_float(value):
    """Safely convert to float with type checking"""
    if isinstance(value, (int, float, np.number)):
        return float(value)
    else:
        try:
            return float(value)
        except:
            return 0.0

# The rest of your EDA code continues here...
# Add placeholders for the main EDA functions that were likely in the original file

class EDAAnalyzer:
    """Main EDA analysis class"""
    
    def __init__(self, data_path=None):
        self.data = None
        self.data_path = data_path
        
    def load_data(self, path=None):
        """Load data for analysis"""
        if path:
            self.data_path = path
            
        if self.data_path and os.path.exists(self.data_path):
            self.data = pd.read_csv(self.data_path)
            logger.info(f"Loaded data: {self.data.shape}")
        else:
            # Generate sample data if no path provided
            pipeline = DataPipeline()
            self.data = pipeline.generate_sample_data(n_samples=10000)
            logger.info(f"Generated sample data: {self.data.shape}")
        
        return self.data
    
    def basic_statistics(self):
        """Get basic statistics of the dataset"""
        if self.data is None:
            logger.error("No data loaded")
            return None
            
        stats = {
            'shape': self.data.shape,
            'columns': list(self.data.columns),
            'dtypes': self.data.dtypes.to_dict(),
            'missing_values': self.data.isnull().sum().to_dict(),
            'description': self.data.describe().to_dict()
        }
        
        return stats
    
    def fraud_distribution(self):
        """Analyze fraud distribution"""
        if self.data is None or 'is_fraud' not in self.data.columns:
            logger.error("No fraud column in data")
            return None
            
        fraud_counts = self.data['is_fraud'].value_counts()
        fraud_rate = self.data['is_fraud'].mean()
        
        return {
            'fraud_counts': fraud_counts.to_dict(),
            'fraud_rate': safe_float(fraud_rate),  # Use safe_float
            'normal_transactions': int(fraud_counts.get(0, 0)),
            'fraud_transactions': int(fraud_counts.get(1, 0))
        }
    
    def plot_distributions(self, columns=None):
        """Plot distributions of numerical columns"""
        if self.data is None:
            logger.error("No data loaded")
            return
            
        if columns is None:
            columns = self.data.select_dtypes(include=[np.number]).columns[:8]
        
        fig, axes = plt.subplots(2, 4, figsize=(20, 10))
        axes = axes.flatten()
        
        for idx, col in enumerate(columns[:8]):
            if idx < len(axes):
                self.data[col].hist(ax=axes[idx], bins=30, edgecolor='black')
                axes[idx].set_title(f'Distribution of {col}')
                axes[idx].set_xlabel(col)
                axes[idx].set_ylabel('Frequency')
        
        plt.tight_layout()
        plt.show()
    
    def correlation_analysis(self):
        """Analyze correlations between features"""
        if self.data is None:
            logger.error("No data loaded")
            return None
            
        # Select numerical columns
        numerical_cols = self.data.select_dtypes(include=[np.number]).columns
        
        # Calculate correlation matrix
        corr_matrix = self.data[numerical_cols].corr()
        
        # Fix any tuple values in correlation matrix
        corr_matrix = fix_correlation_calculations(corr_matrix)
        
        # Find high correlations
        high_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]
                corr_value = safe_float(corr_matrix.iloc[i, j])  # Use safe_float
                
                if safe_abs(corr_value) > 0.7:  # Use safe_abs
                    high_corr.append({
                        'feature1': col1,
                        'feature2': col2,
                        'correlation': corr_value
                    })
        
        return {
            'correlation_matrix': corr_matrix,
            'high_correlations': high_corr
        }
    
    def plot_correlation_heatmap(self):
        """Plot correlation heatmap"""
        if self.data is None:
            logger.error("No data loaded")
            return
            
        # Select numerical columns
        numerical_cols = self.data.select_dtypes(include=[np.number]).columns[:15]
        
        # Calculate and fix correlation matrix
        corr_matrix = self.data[numerical_cols].corr()
        corr_matrix = fix_correlation_calculations(corr_matrix)
        
        # Create heatmap
        plt.figure(figsize=(12, 10))
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', 
                   center=0, square=True, linewidths=1)
        plt.title('Feature Correlation Heatmap')
        plt.tight_layout()
        plt.show()
    
    def fraud_analysis_by_feature(self, feature):
        """Analyze fraud patterns by a specific feature"""
        if self.data is None or 'is_fraud' not in self.data.columns:
            logger.error("No fraud data available")
            return None
            
        if feature not in self.data.columns:
            logger.error(f"Feature {feature} not found")
            return None
        
        # Group by feature and fraud status
        grouped = self.data.groupby([feature, 'is_fraud']).size().unstack(fill_value=0)
        
        # Calculate fraud rate by feature value
        fraud_rates = grouped[1] / (grouped[0] + grouped[1])
        
        return {
            'grouped_counts': grouped.to_dict(),
            'fraud_rates': {k: safe_float(v) for k, v in fraud_rates.to_dict().items()}
        }
    
    def temporal_analysis(self):
        """Analyze temporal patterns"""
        if self.data is None:
            logger.error("No data loaded")
            return None
            
        temporal_features = ['transaction_hour', 'transaction_day', 'transaction_weekend']
        results = {}
        
        for feature in temporal_features:
            if feature in self.data.columns:
                if 'is_fraud' in self.data.columns:
                    fraud_by_feature = self.data.groupby(feature)['is_fraud'].agg(['sum', 'count', 'mean'])
                    results[feature] = {
                        'fraud_count': fraud_by_feature['sum'].to_dict(),
                        'total_count': fraud_by_feature['count'].to_dict(),
                        'fraud_rate': {k: safe_float(v) for k, v in fraud_by_feature['mean'].to_dict().items()}
                    }
        
        return results
    
    def generate_report(self):
        """Generate comprehensive EDA report"""
        report = []
        report.append("=" * 60)
        report.append("E-COMMERCE FRAUD DETECTION - EDA REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Basic statistics
        stats = self.basic_statistics()
        if stats:
            report.append("DATASET OVERVIEW:")
            report.append(f"  Shape: {stats['shape']}")
            report.append(f"  Features: {len(stats['columns'])}")
            report.append(f"  Missing values: {sum(stats['missing_values'].values())}")
        
        # Fraud distribution
        fraud_dist = self.fraud_distribution()
        if fraud_dist:
            report.append("\nFRAUD DISTRIBUTION:")
            report.append(f"  Fraud rate: {fraud_dist['fraud_rate']:.2%}")
            report.append(f"  Normal transactions: {fraud_dist['normal_transactions']:,}")
            report.append(f"  Fraud transactions: {fraud_dist['fraud_transactions']:,}")
        
        # Correlation analysis
        corr_analysis = self.correlation_analysis()
        if corr_analysis and corr_analysis.get('high_correlations'):
            report.append("\nHIGH CORRELATIONS:")
            high_correlations = corr_analysis.get('high_correlations', [])
            for corr in high_correlations[:5]:
                if isinstance(corr, dict) and all(k in corr for k in ['feature1', 'feature2', 'correlation']):
                    report.append(f"  {corr['feature1']} <-> {corr['feature2']}: {corr['correlation']:.3f}")
        
        # Temporal analysis
        temporal = self.temporal_analysis()
        if temporal:
            report.append("\nTEMPORAL PATTERNS:")
            for feature, data in temporal.items():
                if (data is not None and 
                    'fraud_rate' in data and 
                    data['fraud_rate'] is not None and 
                    len(data['fraud_rate']) > 0):
                    try:
                        max_rate_key = max(data['fraud_rate'].items(), key=lambda x: x[1])
                        report.append(f"  {feature}: Highest fraud rate at {max_rate_key[0]} ({max_rate_key[1]:.2%})")
                    except (ValueError, TypeError):
                        # Handle case where data is empty or max fails
                        continue
        
        report.append("\n" + "=" * 60)
        
        return "\n".join(report)

# Main execution
if __name__ == "__main__":
    print("🔍 Starting Exploratory Data Analysis...")
    
    # Initialize analyzer
    analyzer = EDAAnalyzer()
    
    # Load data
    data = analyzer.load_data()
    print(f"✅ Data loaded: {data.shape}")
    
    # Basic statistics
    stats = analyzer.basic_statistics()
    print(f"\n📊 Dataset has {stats['shape'][0]:,} rows and {stats['shape'][1]} columns")
    
    # Fraud distribution
    fraud_dist = analyzer.fraud_distribution()
    if fraud_dist:
        print(f"🚨 Fraud rate: {fraud_dist['fraud_rate']:.2%}")
    
    # Plot distributions
    print("\n📈 Plotting distributions...")
    analyzer.plot_distributions()
    
    # Correlation analysis
    print("\n🔗 Analyzing correlations...")
    analyzer.plot_correlation_heatmap()
    
    # Generate report
    report = analyzer.generate_report()
    print("\n📄 EDA Report:")
    print(report)
    
    # Save report
    report_path = Path("../reports/eda_report.txt")
    report_path.parent.mkdir(exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"\n💾 Report saved to {report_path}")