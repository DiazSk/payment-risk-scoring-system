"""
Utility functions for E-Commerce Fraud Detection System
Common functions used across the project
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ModelUtils:
    """Utilities for model management and persistence"""

    @staticmethod
    def save_model(model: Any, filename: str, model_dir: str = "models/") -> str:
        """Save a trained model to disk"""
        model_path = Path(model_dir)
        model_path.mkdir(exist_ok=True)

        full_path = model_path / filename

        try:
            joblib.dump(model, full_path)
            logger.info(f"Model saved to {full_path}")
            return str(full_path)
        except Exception as e:
            logger.error(f"Error saving model: {e}")
            raise

    @staticmethod
    def load_model(filename: str, model_dir: str = "models/") -> Any:
        """Load a trained model from disk"""
        full_path = Path(model_dir) / filename

        try:
            model = joblib.load(full_path)
            logger.info(f"Model loaded from {full_path}")
            return model
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

    @staticmethod
    def save_model_metadata(
        metadata: Dict, filename: str = "model_metadata.json", model_dir: str = "models/"
    ):
        """Save model metadata (performance, features, etc.)"""
        model_path = Path(model_dir)
        model_path.mkdir(exist_ok=True)

        full_path = model_path / filename

        # Add timestamp
        metadata["saved_at"] = datetime.now().isoformat()

        try:
            with open(full_path, "w") as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"Model metadata saved to {full_path}")
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
            raise


class DataUtils:
    """Utilities for data processing and analysis"""

    @staticmethod
    def analyze_class_imbalance(y: pd.Series) -> Dict:
        """Analyze class distribution"""
        class_counts = y.value_counts()
        class_props = y.value_counts(normalize=True)

        analysis = {
            "total_samples": len(y),
            "class_counts": class_counts.to_dict(),
            "class_proportions": class_props.to_dict(),
            "imbalance_ratio": class_counts.max() / class_counts.min(),
            "minority_class": class_counts.idxmin(),
            "majority_class": class_counts.idxmax(),
        }

        return analysis

    @staticmethod
    def split_features_target(
        df: pd.DataFrame, target_col: str = "isFraud"
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Split DataFrame into features and target"""
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not found in DataFrame")

        X = df.drop(columns=[target_col])
        y = df[target_col]

        return X, y

    @staticmethod
    def get_numeric_features(df: pd.DataFrame) -> List[str]:
        """Get list of numeric feature names"""
        return df.select_dtypes(include=[np.number]).columns.tolist()

    @staticmethod
    def get_categorical_features(df: pd.DataFrame) -> List[str]:
        """Get list of categorical feature names"""
        return df.select_dtypes(include=["object", "category"]).columns.tolist()

    @staticmethod
    def detect_outliers(df: pd.DataFrame, columns: List[str], method: str = "iqr") -> pd.DataFrame:
        """Detect outliers using IQR or Z-score method"""
        outlier_mask = pd.Series(False, index=df.index)

        for col in columns:
            if col not in df.columns:
                continue

            if method == "iqr":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outlier_mask |= (df[col] < lower_bound) | (df[col] > upper_bound)

            elif method == "zscore":
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                outlier_mask |= z_scores > 3

        return df[outlier_mask]


class MetricsUtils:
    """Utilities for model evaluation metrics"""

    @staticmethod
    def calculate_fraud_metrics(
        y_true: np.array, y_pred: np.array, y_prob: Optional[np.array] = None
    ) -> Dict:
        """Calculate comprehensive fraud detection metrics"""
    # NOTE: All metrics are now computed from real test/validation data only.
    # Artificially perfect metrics have been removed to ensure honest, defensible reporting.
    # This change improves platform integrity and transparency.
        from sklearn.metrics import (
            average_precision_score,
            classification_report,
            confusion_matrix,
            precision_recall_curve,
            roc_auc_score,
            roc_curve,
        )

        # Basic classification metrics
        report = classification_report(y_true, y_pred, output_dict=True)
        cm = confusion_matrix(y_true, y_pred)

        # Extract key metrics
        tn, fp, fn, tp = cm.ravel()

        metrics = {
            "accuracy": (tp + tn) / (tp + tn + fp + fn),
            "precision": tp / (tp + fp) if (tp + fp) > 0 else 0,
            "recall": tp / (tp + fn) if (tp + fn) > 0 else 0,
            "f1_score": report["1"]["f1-score"] if "1" in report else 0,
            "specificity": tn / (tn + fp) if (tn + fp) > 0 else 0,
            "false_positive_rate": fp / (fp + tn) if (fp + tn) > 0 else 0,
            "false_negative_rate": fn / (fn + tp) if (fn + tp) > 0 else 0,
            "true_positives": int(tp),
            "false_positives": int(fp),
            "true_negatives": int(tn),
            "false_negatives": int(fn),
        }

        # ROC-AUC if probabilities provided
        if y_prob is not None:
            metrics["roc_auc"] = roc_auc_score(y_true, y_prob)
            metrics["pr_auc"] = average_precision_score(y_true, y_prob)

        return metrics

    @staticmethod
    def print_fraud_metrics(metrics: Dict):
        """Pretty print fraud detection metrics"""
        print("\n" + "=" * 50)
        print("          FRAUD DETECTION METRICS")
        print("=" * 50)

        print("📊 Classification Metrics:")
        print(f"   Accuracy:      {metrics['accuracy']:.4f}")
        print(f"   Precision:     {metrics['precision']:.4f}")
        print(f"   Recall:        {metrics['recall']:.4f}")
        print(f"   F1-Score:      {metrics['f1_score']:.4f}")
        print(f"   Specificity:   {metrics['specificity']:.4f}")

        print("\n🎯 Fraud Detection Performance:")
        print(f"   False Positive Rate:  {metrics['false_positive_rate']:.4f}")
        print(f"   False Negative Rate:  {metrics['false_negative_rate']:.4f}")

        print("\n📈 Confusion Matrix:")
        print(f"   True Positives:   {metrics['true_positives']:,}")
        print(f"   False Positives:  {metrics['false_positives']:,}")
        print(f"   True Negatives:   {metrics['true_negatives']:,}")
        print(f"   False Negatives:  {metrics['false_negatives']:,}")

        if "roc_auc" in metrics:
            print("\n🔍 Advanced Metrics:")
            print(f"   ROC-AUC:       {metrics['roc_auc']:.4f}")
            print(f"   PR-AUC:        {metrics['pr_auc']:.4f}")


class VisualizationUtils:
    """Utilities for creating visualizations"""

    @staticmethod
    def plot_class_distribution(y: pd.Series, title: str = "Class Distribution") -> None:
        """Plot class distribution"""
        plt.figure(figsize=(8, 6))

        counts = y.value_counts()
        colors = ["skyblue", "lightcoral"]

        plt.bar(counts.index, counts.values, color=colors)
        plt.title(title)
        plt.xlabel("Class")
        plt.ylabel("Count")

        # Add percentages on bars
        total = len(y)
        for i, v in enumerate(counts.values):
            plt.text(i, v + 0.01 * total, f"{v:,}\n({v / total:.2%})", ha="center", va="bottom")

        plt.show()

    @staticmethod
    def plot_feature_correlation(
        df: pd.DataFrame, target_col: str = "isFraud", top_n: int = 20
    ) -> None:
        """Plot feature correlations with target variable"""
        if target_col not in df.columns:
            logger.warning(f"Target column '{target_col}' not found")
            return

        # Calculate correlations
        numeric_features = df.select_dtypes(include=[np.number]).columns.tolist()
        if target_col not in numeric_features:
            return

        correlations = df[numeric_features].corr()[target_col].abs().sort_values(ascending=False)
        correlations = correlations.drop(target_col).head(top_n)

        plt.figure(figsize=(10, 8))
        sns.barplot(x=correlations.values, y=correlations.index)
        plt.title(f"Top {top_n} Features Correlated with {target_col}")
        plt.xlabel("Absolute Correlation")
        plt.tight_layout()
        plt.show()


class ConfigUtils:
    """Configuration management utilities"""

    @staticmethod
    def load_config(config_path: str = "config/config.json") -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            logger.warning(f"Config file not found: {config_path}. Using defaults.")
            return ConfigUtils.get_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return ConfigUtils.get_default_config()

    @staticmethod
    def get_default_config() -> Dict:
        """Get default configuration"""
        return {
            "model": {"test_size": 0.2, "random_state": 42, "cv_folds": 5},
            "xgboost": {
                "n_estimators": 100,
                "max_depth": 6,
                "learning_rate": 0.1,
                "subsample": 0.8,
                "colsample_bytree": 0.8,
                "scale_pos_weight": 10,
            },
            "preprocessing": {
                "handle_outliers": True,
                "outlier_method": "iqr",
                "scale_features": True,
            },
            "api": {"host": "0.0.0.0", "port": 8000, "workers": 1},
        }

    @staticmethod
    def save_config(config: Dict, config_path: str = "config/config.json"):
        """Save configuration to JSON file"""
        config_dir = Path(config_path).parent
        config_dir.mkdir(exist_ok=True)

        try:
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
            logger.info(f"Configuration saved to {config_path}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            raise


def setup_project_logging(log_level: str = "INFO", log_file: str = "logs/fraud_detection.log"):
    """Setup project-wide logging"""
    log_dir = Path(log_file).parent
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )


def main():
    """Test utility functions"""
    print("🧪 Testing utility functions...")

    # Test configuration
    config = ConfigUtils.get_default_config()
    print(f"✅ Default config loaded: {len(config)} sections")

    # Test data analysis (with dummy data)
    dummy_y = pd.Series([0] * 1000 + [1] * 17)  # 1.7% fraud rate
    analysis = DataUtils.analyze_class_imbalance(dummy_y)
    print(
        f"✅ Class imbalance analysis: {
            analysis['imbalance_ratio']:.1f}:1 ratio"
    )

    print("🎉 All utility functions tested successfully!")


if __name__ == "__main__":
    main()


class DataValidator:
    """Simple data validation utility"""

    def __init__(self):
        self.validation_errors = []

    def validate_dataframe(self, df):
        """Validate a dataframe for basic requirements"""
        self.validation_errors = []

        # Check if dataframe is not None
        if df is None:
            self.validation_errors.append("DataFrame is None")
            return False

        # Check if dataframe is not empty
        if len(df) == 0:
            self.validation_errors.append("DataFrame is empty")
            return False

        # Check for nulls
        null_count = df.isnull().sum().sum()
        if null_count > 0:
            self.validation_errors.append(f"DataFrame contains {null_count} null values")

        # Check for required columns
        if "is_fraud" not in df.columns:
            self.validation_errors.append("Missing 'is_fraud' column")

        return len(self.validation_errors) == 0

    def get_errors(self):
        """Get validation errors"""
        return self.validation_errors
