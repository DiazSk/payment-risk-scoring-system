"""
Prediction Utilities for Fraud Detection API
Helper functions for feature processing and batch predictions
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import joblib
import numpy as np
import pandas as pd

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureProcessor:
    """Process and validate features for fraud detection"""

    def __init__(self):
        self.required_features = 82  # Based on trained models

    def validate_features(self, features: Union[Dict, List, np.ndarray]) -> bool:
        """Validate input features"""

        if isinstance(features, dict):
            feature_array = self._dict_to_array(features)
        elif isinstance(features, list):
            feature_array = np.array(features)
        elif isinstance(features, np.ndarray):
            feature_array = features.flatten()
        else:
            logger.error(f"Invalid feature type: {type(features)}")
            return False

        # Check feature count
        if len(feature_array) != self.required_features:
            logger.warning(
                f"Expected {
                    self.required_features} features, got {
                    len(feature_array)}. Padding/truncating..."
            )
            return True  # We'll handle padding in processing

        # Check for invalid values
        if np.any(np.isnan(feature_array)) or np.any(np.isinf(feature_array)):
            logger.warning("Features contain NaN or infinite values, replacing with 0")
            return True  # We'll handle this in processing

        return True

    def _dict_to_array(self, feature_dict: Dict) -> np.ndarray:
        """Convert feature dictionary to array with proper padding"""

        # Define expected feature order
        expected_features = [
            "transaction_amount",
            "transaction_hour",
            "transaction_day",
            "transaction_weekend",
            "is_business_hours",
            "card_amount_mean",
            "card_txn_count_recent",
            "time_since_last_txn",
            "merchant_risk_score",
            "amount_zscore",
            "is_amount_outlier",
        ]

        # Extract core features
        feature_list = []
        for feature_name in expected_features:
            value = feature_dict.get(feature_name, 0.0)
            feature_list.append(float(value))

        # Add additional features if provided
        additional = feature_dict.get("additional_features", [])
        if additional:
            feature_list.extend(additional)

        # Pad to required length with zeros
        while len(feature_list) < self.required_features:
            feature_list.append(0.0)

        # Truncate if too long
        feature_list = feature_list[: self.required_features]

        # Convert to numpy array and handle NaN/inf values
        feature_array: np.ndarray = np.array(feature_list)
        feature_array = np.nan_to_num(feature_array, nan=0.0, posinf=0.0, neginf=0.0)

        return feature_array

    def process_transaction_features(self, transaction_data: Dict) -> np.ndarray:
        """Process raw transaction data into model features"""

        # Extract and compute features
        amount = float(transaction_data.get("transaction_amount", 0))
        hour = int(transaction_data.get("transaction_hour", 12))

        features = {
            "transaction_amount": amount,
            "transaction_hour": hour,
            "transaction_day": int(transaction_data.get("transaction_day", 15)),
            "transaction_weekend": int(transaction_data.get("transaction_weekend", 0)),
            "is_business_hours": int(
                transaction_data.get("is_business_hours", 1 if 9 <= hour <= 17 else 0)
            ),
            "card_amount_mean": float(transaction_data.get("card_amount_mean", 50)),
            "card_txn_count_recent": int(transaction_data.get("card_txn_count_recent", 1)),
            "time_since_last_txn": float(transaction_data.get("time_since_last_txn", 3600)),
            "merchant_risk_score": float(transaction_data.get("merchant_risk_score", 0.1)),
            "amount_zscore": float(transaction_data.get("amount_zscore", 0)),
            "is_amount_outlier": int(transaction_data.get("is_amount_outlier", 0)),
        }

        # Add any additional features from transaction_data
        if "additional_features" in transaction_data:
            features["additional_features"] = transaction_data["additional_features"]

        return self._dict_to_array(features)


class BatchPredictor:
    """Handle batch predictions efficiently"""

    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.feature_processor = FeatureProcessor()

    def predict_batch(
        self, transactions: List[Dict], model_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Make fraud predictions for multiple transactions

        Args:
            transactions: List of transaction feature dictionaries
            model_name: Specific model to use (optional)

        Returns:
            List of prediction results
        """

        if not self.model_manager.model_loaded:
            raise RuntimeError("Models not loaded")

        results = []

        for i, transaction in enumerate(transactions):
            try:
                # Process features
                features = self.feature_processor.process_transaction_features(transaction)
                features = features.reshape(1, -1)

                # Make prediction
                prediction = self.model_manager.predict_fraud(features, model_name)
                prediction["transaction_index"] = i

                # Add transaction ID if provided
                if "transaction_id" in transaction:
                    prediction["transaction_id"] = transaction["transaction_id"]

                results.append(prediction)

            except Exception as e:
                logger.error(f"Failed to process transaction {i}: {e}")
                results.append(
                    {
                        "transaction_index": i,
                        "transaction_id": transaction.get("transaction_id", f"txn_{i}"),
                        "error": str(e),
                        "is_fraud": False,
                        "fraud_probability": 0.0,
                        "risk_level": "ERROR",
                    }
                )

        return results

    def analyze_batch_results(self, predictions: List[Dict]) -> Dict[str, Any]:
        """Analyze batch prediction results"""

        valid_predictions = [p for p in predictions if "error" not in p]
        error_count = len(predictions) - len(valid_predictions)

        if not valid_predictions:
            return {"error": "No valid predictions to analyze"}

        # Extract metrics
        fraud_flags = [p["is_fraud"] for p in valid_predictions]
        fraud_probabilities = [p["fraud_probability"] for p in valid_predictions]
        risk_levels = [p["risk_level"] for p in valid_predictions]

        # Calculate statistics
        analysis = {
            "total_transactions": len(predictions),
            "valid_predictions": len(valid_predictions),
            "error_count": error_count,
            "fraud_detected": sum(fraud_flags),
            "fraud_rate": np.mean(fraud_flags) if fraud_flags else 0,
            "avg_fraud_probability": np.mean(fraud_probabilities) if fraud_probabilities else 0,
            "max_fraud_probability": np.max(fraud_probabilities) if fraud_probabilities else 0,
            "min_fraud_probability": np.min(fraud_probabilities) if fraud_probabilities else 0,
            "risk_distribution": {
                "HIGH": sum(1 for r in risk_levels if r == "HIGH"),
                "MEDIUM": sum(1 for r in risk_levels if r == "MEDIUM"),
                "LOW": sum(1 for r in risk_levels if r == "LOW"),
                "VERY_LOW": sum(1 for r in risk_levels if r == "VERY_LOW"),
            },
            "processing_timestamp": datetime.now().isoformat(),
        }

        # Add percentile information
        if fraud_probabilities:
            analysis["fraud_probability_percentiles"] = {
                "p50": float(np.percentile(fraud_probabilities, 50)),
                "p90": float(np.percentile(fraud_probabilities, 90)),
                "p95": float(np.percentile(fraud_probabilities, 95)),
                "p99": float(np.percentile(fraud_probabilities, 99)),
            }

        return analysis


class TransactionValidator:
    """Validate and preprocess transaction data"""

    @staticmethod
    def validate_transaction(transaction_data: Dict) -> Tuple[bool, str]:
        """
        Validate a single transaction's data

        Returns:
            (is_valid, error_message)
        """

        # Check for required core fields
        required_fields = ["transaction_amount"]

        for field in required_fields:
            if field not in transaction_data:
                return False, f"Missing required field: {field}"

        # Validate amount
        try:
            amount = float(transaction_data["transaction_amount"])
            if amount < 0:
                return False, "Transaction amount cannot be negative"
            if amount > 1000000:  # Sanity check
                return False, "Transaction amount exceeds maximum limit"
        except (ValueError, TypeError):
            return False, "Invalid transaction amount"

        # Validate hour if provided
        if "transaction_hour" in transaction_data:
            try:
                hour = int(transaction_data["transaction_hour"])
                if not 0 <= hour <= 23:
                    return False, "Transaction hour must be between 0 and 23"
            except (ValueError, TypeError):
                return False, "Invalid transaction hour"

        # Validate day if provided
        if "transaction_day" in transaction_data:
            try:
                day = int(transaction_data["transaction_day"])
                if not 1 <= day <= 31:
                    return False, "Transaction day must be between 1 and 31"
            except (ValueError, TypeError):
                return False, "Invalid transaction day"

        # Validate risk score if provided
        if "merchant_risk_score" in transaction_data:
            try:
                risk = float(transaction_data["merchant_risk_score"])
                if not 0 <= risk <= 1:
                    return False, "Merchant risk score must be between 0 and 1"
            except (ValueError, TypeError):
                return False, "Invalid merchant risk score"

        return True, ""

    @staticmethod
    def preprocess_transaction(transaction_data: Dict) -> Dict:
        """
        Preprocess transaction data with defaults and computed features
        """

        # Create a copy to avoid modifying original
        processed = transaction_data.copy()

        # Set defaults for missing fields
        defaults = {
            "transaction_hour": 12,
            "transaction_day": 15,
            "transaction_weekend": 0,
            "is_business_hours": 1,
            "card_amount_mean": 75.0,
            "card_txn_count_recent": 3,
            "time_since_last_txn": 3600.0,
            "merchant_risk_score": 0.1,
            "amount_zscore": 0.0,
            "is_amount_outlier": 0,
        }

        for key, default_value in defaults.items():
            if key not in processed:
                processed[key] = default_value

        # Compute derived features if not provided
        hour = processed["transaction_hour"]
        if "is_business_hours" not in transaction_data:
            processed["is_business_hours"] = 1 if 9 <= hour <= 17 else 0

        # Compute amount z-score if not provided
        if "amount_zscore" not in transaction_data:
            amount = processed["transaction_amount"]
            mean = processed["card_amount_mean"]
            if mean > 0:
                processed["amount_zscore"] = (amount - mean) / (mean * 0.5 + 1)
            else:
                processed["amount_zscore"] = 0

        # Determine outlier status
        if "is_amount_outlier" not in transaction_data:
            processed["is_amount_outlier"] = 1 if abs(processed["amount_zscore"]) > 3 else 0

        return processed


# Utility functions for the API
def create_prediction_explanation(transaction_data: Dict, prediction: Dict) -> str:
    """Generate human-readable explanation for prediction"""

    risk_factors = []

    # Analyze risk factors
    amount = transaction_data.get("transaction_amount", 0)
    hour = transaction_data.get("transaction_hour", 12)
    amount_zscore = transaction_data.get("amount_zscore", 0)
    merchant_risk = transaction_data.get("merchant_risk_score", 0)

    if amount > 500:
        risk_factors.append("high transaction amount")

    if hour < 6 or hour > 22:
        risk_factors.append("unusual transaction time")

    if abs(amount_zscore) > 2:
        risk_factors.append("amount significantly different from user pattern")

    if merchant_risk > 0.5:
        risk_factors.append("high-risk merchant")

    # Generate explanation
    if prediction["is_fraud"]:
        if risk_factors:
            explanation = f"🚨 FRAUD DETECTED: {', '.join(risk_factors)}"
        else:
            explanation = "🚨 FRAUD DETECTED: Pattern matches known fraud signatures"
    else:
        if prediction["fraud_probability"] > 0.3:
            explanation = "⚠️ ELEVATED RISK: Some concerning patterns detected"
        else:
            explanation = "✅ NORMAL: Transaction appears legitimate"

    explanation += f" (Confidence: {prediction['confidence']:.1%})"

    return explanation


# Quick fraud check function for simple API calls
def quick_fraud_check(amount: float, hour: int = 12, merchant_risk: float = 0.1) -> Dict[str, Any]:
    """
    Quick fraud check with minimal inputs
    Returns a simple risk assessment
    """

    # Simple rule-based check (fallback when models aren't loaded)
    risk_score = 0.0

    # Check amount
    if amount > 1000:
        risk_score += 0.4
    elif amount > 500:
        risk_score += 0.2

    # Check time
    if hour < 6 or hour > 22:
        risk_score += 0.2

    # Check merchant risk
    risk_score += merchant_risk * 0.4

    # Cap at 1.0
    risk_score = min(1.0, risk_score)

    return {
        "is_fraud": risk_score >= 0.5,
        "fraud_probability": risk_score,
        "risk_level": "HIGH" if risk_score >= 0.7 else "MEDIUM" if risk_score >= 0.4 else "LOW",
        "confidence": abs(risk_score - 0.5) * 2,
        "method": "rule_based",
    }
