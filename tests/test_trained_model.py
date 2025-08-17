#!/usr/bin/env python3
"""
Test Trained Models
Quick script to test trained models and generate sample predictions
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

# Add src to path
sys.path.append("src")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelTester:
    """Test trained fraud detection models"""

    def __init__(self):
        self.models_dir = Path("models")
        self.models = {}
        self.scalers = {}
        self.metadata = {}

    def load_trained_models(self):
        """Load all trained models and metadata"""
        logger.info("Loading trained models...")

        # Load metadata
        metadata_path = self.models_dir / "model_metadata.json"
        if metadata_path.exists():
            with open(metadata_path, "r") as f:
                self.metadata = json.load(f)
            logger.info("✅ Metadata loaded")
        else:
            logger.warning("⚠️ No metadata file found")
            return False

        # Load scalers
        scalers_path = self.models_dir / "scalers.pkl"
        if scalers_path.exists():
            self.scalers = joblib.load(scalers_path)
            logger.info("✅ Scalers loaded")

        # Load individual models
        model_count = 0
        for model_name, model_info in self.metadata.get("models", {}).items():
            model_path = self.models_dir / model_info["file_path"]
            if model_path.exists():
                try:
                    self.models[model_name] = joblib.load(model_path)
                    logger.info(f"✅ Loaded {model_name}")
                    model_count += 1
                except Exception as e:
                    logger.error(f"❌ Failed to load {model_name}: {e}")

        logger.info(f"📊 Loaded {model_count} models successfully")
        return model_count > 0

    def prepare_sample_data(self, n_samples=100):
        """Create sample data for testing"""
        logger.info(f"Preparing {n_samples} sample transactions...")

        # Load original data to get feature structure
        data_path = "data/processed/test_featured_data.csv"
        if not Path(data_path).exists():
            logger.error("❌ Original dataset not found")
            return None

        df_original = pd.read_csv(data_path)

        # Get a sample of real transactions
        sample_data = df_original.sample(n=min(n_samples, len(df_original)), random_state=42)

        # Prepare features (remove target and ID columns)
        X_sample = sample_data.drop(columns=["isFraud", "TransactionID"], errors="ignore")
        y_sample = sample_data.get("isFraud", pd.Series([0] * len(sample_data)))

        logger.info(f"✅ Prepared {len(X_sample)} sample transactions")
        return X_sample, y_sample, sample_data

    def test_single_model(self, model_name, model, X_test, y_test):
        """Test a single model"""
        logger.info(f"Testing {model_name}...")

        try:
            # Prepare data for model
            if model_name in ["logistic_regression", "ensemble"]:
                if "standard" in self.scalers:
                    X_test_scaled = self.scalers["standard"].transform(X_test)
                else:
                    logger.warning(f"⚠️ No scaler found for {model_name}")
                    X_test_scaled = X_test
            else:
                X_test_scaled = X_test

            # Make predictions
            if hasattr(model, "predict_proba"):
                y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]

                # Use threshold from metadata
                threshold = (
                    self.metadata.get("models", {}).get(model_name, {}).get("threshold", 0.5)
                )
                y_pred = (y_pred_proba >= threshold).astype(int)

            elif model_name == "isolation_forest":
                anomaly_pred = model.predict(X_test_scaled)
                y_pred = (anomaly_pred == -1).astype(int)  # -1 indicates anomaly/fraud
                y_pred_proba = None

            else:
                y_pred = model.predict(X_test_scaled)
                y_pred_proba = None

            # Calculate basic metrics
            from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

            metrics = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred, zero_division=0),
                "recall": recall_score(y_test, y_pred),
                "f1_score": f1_score(y_test, y_pred, zero_division=0),
                "fraud_predictions": int(np.sum(y_pred)),
                "total_predictions": len(y_pred),
            }

            logger.info(
                f"  ✅ {model_name} - Accuracy: {metrics['accuracy']:.3f}, "
                f"Recall: {metrics['recall']:.3f}, Predicted Fraud: {metrics['fraud_predictions']}"
            )

            return {"predictions": y_pred, "probabilities": y_pred_proba, "metrics": metrics}

        except Exception as e:
            logger.error(f"❌ Failed to test {model_name}: {e}")
            return None

    def test_all_models(self, X_test, y_test):
        """Test all loaded models"""
        logger.info("🧪 Testing all models...")

        results = {}

        for model_name, model in self.models.items():
            result = self.test_single_model(model_name, model, X_test, y_test)
            if result:
                results[model_name] = result

        return results

    def create_sample_predictions_demo(self, results, sample_data):
        """Create a demo showing sample predictions"""
        logger.info("Creating sample predictions demo...")

        # Get best model
        best_model = max(results.keys(), key=lambda x: results[x]["metrics"]["f1_score"])
        best_predictions = results[best_model]["predictions"]
        best_probabilities = results[best_model].get("probabilities")

        # Create demo data
        demo_data = sample_data.head(10).copy()
        demo_data["predicted_fraud"] = best_predictions[:10]

        if best_probabilities is not None:
            demo_data["fraud_probability"] = best_probabilities[:10]

        # Select interesting columns for display
        display_columns = [
            "TransactionAmt",
            "transaction_hour",
            "transaction_weekend",
            "card_amount_mean",
            "isFraud",
            "predicted_fraud",
        ]

        if "fraud_probability" in demo_data.columns:
            display_columns.append("fraud_probability")

        available_columns = [col for col in display_columns if col in demo_data.columns]
        demo_display = demo_data[available_columns]

        print("\n" + "=" * 80)
        print("🎯 SAMPLE PREDICTIONS DEMO")
        print("=" * 80)
        print(f"Model: {best_model}")
        print(f"Sample of 10 transactions with predictions:")
        print("-" * 80)

        for idx, row in demo_display.iterrows():
            print(f"\nTransaction {idx + 1}:")
            for col in available_columns:
                if col == "fraud_probability":
                    print(f"  {col}: {row[col]:.3f}")
                elif col in ["isFraud", "predicted_fraud"]:
                    status = "FRAUD" if row[col] == 1 else "NORMAL"
                    print(f"  {col}: {status}")
                else:
                    print(f"  {col}: {row[col]}")

            # Show prediction accuracy
            actual = row.get("isFraud", 0)
            predicted = row.get("predicted_fraud", 0)
            correct = "✅ CORRECT" if actual == predicted else "❌ INCORRECT"
            print(f"  Prediction: {correct}")

        return demo_display

    def generate_test_report(self, results):
        """Generate a comprehensive test report"""
        logger.info("Generating test report...")

        report = []
        report.append("# TRAINED MODELS TEST REPORT")
        report.append("=" * 50)
        report.append(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Models Tested: {len(results)}")
        report.append("")

        # Summary table
        report.append("## MODEL PERFORMANCE SUMMARY")
        report.append("-" * 40)
        report.append(f"{'Model':<20} {'Accuracy':<10} {'Recall':<8} {'Precision':<10} {'F1':<8}")
        report.append("-" * 40)

        for model_name, result in results.items():
            metrics = result["metrics"]
            report.append(
                f"{model_name:<20} "
                f"{metrics['accuracy']:<10.3f} "
                f"{metrics['recall']:<8.3f} "
                f"{metrics['precision']:<10.3f} "
                f"{metrics['f1_score']:<8.3f}"
            )

        # Best model
        best_model = max(results.keys(), key=lambda x: results[x]["metrics"]["f1_score"])
        report.append(f"\nBest Performing Model: {best_model}")

        # Prediction summary
        report.append("\n## PREDICTION SUMMARY")
        report.append("-" * 25)

        for model_name, result in results.items():
            metrics = result["metrics"]
            report.append(f"{model_name}:")
            report.append(
                f"  - Fraud predictions: {metrics['fraud_predictions']}/{metrics['total_predictions']}"
            )
            report.append(
                f"  - Fraud rate: {metrics['fraud_predictions']/metrics['total_predictions']:.2%}"
            )

        report.append("\n## DEPLOYMENT READINESS")
        report.append("-" * 30)

        best_metrics = results[best_model]["metrics"]
        if best_metrics["recall"] >= 0.8 and best_metrics["precision"] >= 0.5:
            report.append("✅ Models are ready for production deployment")
        elif best_metrics["recall"] >= 0.7:
            report.append("⚠️ Models are ready for staging deployment")
        else:
            report.append("🔧 Models need further optimization before deployment")

        # Save report
        report_text = "\n".join(report)
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)

        with open(reports_dir / "model_testing_report.txt", "w") as f:
            f.write(report_text)

        return report_text

    def run_complete_test(self, n_samples=100):
        """Run complete model testing pipeline"""
        logger.info("🚀 Starting complete model testing...")

        # Load models
        if not self.load_trained_models():
            logger.error("❌ Failed to load models")
            return False

        # Prepare sample data
        sample_data_result = self.prepare_sample_data(n_samples)
        if sample_data_result is None:
            logger.error("❌ Failed to prepare sample data")
            return False

        X_test, y_test, sample_data = sample_data_result

        # Test all models
        results = self.test_all_models(X_test, y_test)

        if not results:
            logger.error("❌ No models tested successfully")
            return False

        # Create demo predictions
        demo_data = self.create_sample_predictions_demo(results, sample_data)

        # Generate test report
        report = self.generate_test_report(results)

        print("\n" + "=" * 80)
        print("✅ MODEL TESTING COMPLETE!")
        print("=" * 80)
        print(f"📊 Models tested: {len(results)}")
        print(f"📄 Report saved: reports/model_testing_report.txt")
        print(
            f"🎯 Best model: {max(results.keys(), key=lambda x: results[x]['metrics']['f1_score'])}"
        )
        print("\n🚀 Your models are ready for API integration!")

        return True


def main():
    """Main testing function"""
    print("🧪 TRAINED MODELS TESTING SUITE")
    print("=" * 50)

    # Check if models exist
    models_dir = Path("models")
    if not models_dir.exists() or not any(models_dir.glob("*.pkl")):
        print("❌ No trained models found!")
        print("   Please run the model training first: python train_fraud_models.py")
        return False

    # Run testing
    tester = ModelTester()
    success = tester.run_complete_test(n_samples=200)

    if success:
        print("\n✅ All tests completed successfully!")
        print("\n🎯 Next steps:")
        print("   1. Review the test report: reports/model_testing_report.txt")
        print("   2. Build FastAPI endpoints: python app/main.py")
        print("   3. Create Streamlit dashboard")
    else:
        print("\n❌ Testing failed. Check the logs for details.")

    return success


if __name__ == "__main__":
    main()
