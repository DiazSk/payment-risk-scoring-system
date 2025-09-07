"""
Feature Engineering for Fraud Detection System
Enhanced implementation with AML compliance and velocity monitoring features
"""

import numpy as np
import pandas as pd
from .aml_compliance import AMLComplianceChecker, add_aml_features_to_transaction
from .velocity_monitoring import VelocityMonitor, add_velocity_features_to_transaction


class FeatureEngineer:
    """Enhanced feature engineering for fraud detection with AML compliance and velocity monitoring"""

    def __init__(self):
        self.aml_checker = AMLComplianceChecker()
        self.velocity_monitor = VelocityMonitor()

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enhanced feature engineering with AML compliance and velocity monitoring features"""

        # Add some basic engineered features
        if "transaction_amount" in df.columns:
            df["amount_log"] = np.log1p(df["transaction_amount"])

        if "transaction_hour" in df.columns:
            df["is_night"] = ((df["transaction_hour"] < 6) | (df["transaction_hour"] > 22)).astype(
                int
            )

        # Add AML compliance and velocity monitoring features for each transaction
        enhanced_features = []
        for _, row in df.iterrows():
            transaction_data = row.to_dict()
            
            # Get AML features
            aml_result = self.aml_checker.calculate_overall_aml_risk(transaction_data)
            
            # Get velocity features
            customer_id = transaction_data.get("customer_id", "UNKNOWN")
            velocity_result = self.velocity_monitor.assess_velocity_risk(customer_id, transaction_data)
            
            # Combine features
            features = {
                # AML features
                'aml_risk_score': aml_result['aml_overall_risk_score'],
                'aml_risk_level': aml_result['aml_risk_level'],
                'aml_flags_count': len(aml_result['aml_flags']),
                'requires_manual_review': int(aml_result['requires_manual_review']),
                'structuring_risk': aml_result['aml_component_scores']['structuring'],
                'rapid_movement_risk': aml_result['aml_component_scores']['rapid_movement'],
                'suspicious_patterns_risk': aml_result['aml_component_scores']['suspicious_patterns'],
                'sanctions_risk': aml_result['aml_component_scores']['sanctions'],
                
                # Velocity features
                'velocity_risk_score': velocity_result['velocity_risk_score'],
                'velocity_risk_level': velocity_result['velocity_risk_level'],
                'velocity_flags_count': len(velocity_result['velocity_flags']),
                'requires_velocity_review': int(velocity_result['requires_velocity_review']),
                'frequency_risk': velocity_result['velocity_component_scores']['frequency_risk'],
                'volume_risk': velocity_result['velocity_component_scores']['volume_risk'],
                'pattern_risk': velocity_result['velocity_component_scores']['pattern_risk'],
                
                # Velocity metrics
                'transactions_last_minute': velocity_result['velocity_metrics'].get('minute_window_count', 0),
                'transactions_last_hour': velocity_result['velocity_metrics'].get('hour_window_count', 0),
                'transactions_last_day': velocity_result['velocity_metrics'].get('day_window_count', 0),
                'amount_last_minute': velocity_result['velocity_metrics'].get('minute_window_total_amount', 0),
                'amount_last_hour': velocity_result['velocity_metrics'].get('hour_window_total_amount', 0),
                'amount_last_day': velocity_result['velocity_metrics'].get('day_window_total_amount', 0),
                'avg_amount_last_hour': velocity_result['velocity_metrics'].get('hour_window_avg_amount', 0),
                'transaction_rate_last_hour': velocity_result['velocity_metrics'].get('hour_window_rate', 0)
            }
            
            enhanced_features.append(features)
        
        enhanced_df = pd.DataFrame(enhanced_features)
        df = pd.concat([df, enhanced_df], axis=1)

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
