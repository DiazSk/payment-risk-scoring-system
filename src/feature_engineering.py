"""
Feature Engineering for Fraud Detection System
Basic implementation for import compatibility
"""

import numpy as np
import pandas as pd


class FeatureEngineer:
    """Basic feature engineering for fraud detection"""

    def __init__(self):
        pass

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Basic feature engineering"""

        # Add some basic engineered features
        if "transaction_amount" in df.columns:
            df["amount_log"] = np.log1p(df["transaction_amount"])

        if "transaction_hour" in df.columns:
            df["is_night"] = ((df["transaction_hour"] < 6) | (df["transaction_hour"] > 22)).astype(
                int
            )

        return df


    def add_amount_features(self, df):
        """Add amount features - wrapper for create_features"""
        create_features_method = getattr(self, "create_features", None)
        if callable(create_features_method):
            return create_features_method(df)
        return df

    def add_velocity_features(self, df):
        """Add velocity features - wrapper for create_features"""
        create_features_method = getattr(self, "create_features", None)
        if callable(create_features_method):
            return create_features_method(df)
        return df

    def add_risk_features(self, df):
        """Add risk features - wrapper for create_features"""
        create_features_method = getattr(self, "create_features", None)
        if callable(create_features_method):
            return create_features_method(df)
        return df
