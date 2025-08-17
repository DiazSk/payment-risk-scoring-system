#!/usr/bin/env python3
"""
Fraud Detection API Startup Script
Easy way to start the FastAPI server with proper configuration
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path


def check_prerequisites():
    """Check if all required files exist"""
    print("🔍 Checking prerequisites...")

    required_files = ["app/main.py", "models/model_metadata.json"]

    required_dirs = ["models", "app"]

    missing_files = []
    missing_dirs = []

    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)

    if missing_files or missing_dirs:
        print("❌ Missing required files/directories:")
        for file in missing_files:
            print(f"   Missing file: {file}")
        for directory in missing_dirs:
            print(f"   Missing directory: {directory}")
        return False

    # Check if models exist
    models_dir = Path("models")
    model_files = list(models_dir.glob("*.pkl"))

    if not model_files:
        print("❌ No trained models found in models/ directory")
        print("   Please run model training first: python train_fraud_models.py")
        return False

    print("✅ All prerequisites satisfied!")
    print(f"   Found {len(model_files)} trained models")
    return True


def start_api_server(host="0.0.0.0", port=8000, reload=True, workers=1):
    """Start the FastAPI server"""

    print("🚀 Starting Fraud Detection API...")
    print(f"   Host: {host}")
    print(f"   Port: {port}")
    print(f"   Reload: {reload}")
    print(f"   Workers: {workers}")

    # Build uvicorn command
    cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", host, "--port", str(port)]

    if reload:
        cmd.append("--reload")

    if workers > 1:
        cmd.extend(["--workers", str(workers)])

    cmd.extend(["--log-level", "info"])

    print(f"📋 Running command: {' '.join(cmd)}")

    try:
        # Start the server
        process = subprocess.run(cmd)
        return process.returncode == 0
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
        return True
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return False


def show_startup_info():
    """Show information about the API after startup"""

    print("\n" + "=" * 70)
    print("🎉 FRAUD DETECTION API STARTED SUCCESSFULLY!")
    print("=" * 70)

    print("\n🌐 API Endpoints:")
    print("   📍 Homepage:        http://localhost:8000")
    print("   📖 Documentation:   http://localhost:8000/docs")
    print("   📋 ReDoc:          http://localhost:8000/redoc")
    print("   💗 Health Check:   http://localhost:8000/health")
    print("   📊 Model Info:     http://localhost:8000/model_info")
    print("   📈 Metrics:        http://localhost:8000/metrics")

    print("\n🧪 Testing:")
    print("   python test_api.py              # Test all endpoints")
    print("   python example_client.py        # See client examples")

    print("\n📚 Sample API Usage:")
    print(
        """
   # Single prediction
   curl -X POST "http://localhost:8000/predict" \\
        -H "Content-Type: application/json" \\
        -d '{
          "transaction_amount": 156.78,
          "transaction_hour": 14,
          "transaction_day": 15,
          "transaction_weekend": 0,
          "is_business_hours": 1,
          "card_amount_mean": 89.45,
          "card_txn_count_recent": 3,
          "time_since_last_txn": 3600.0,
          "merchant_risk_score": 0.2,
          "amount_zscore": 1.5,
          "is_amount_outlier": 0
        }'
    """
    )

    print("\n🎯 Your fraud detection system is now LIVE and ready to serve predictions!")
    print("   Press Ctrl+C to stop the server")


def main():
    """Main startup function"""

    parser = argparse.ArgumentParser(description="Start the Fraud Detection API")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    parser.add_argument("--skip-checks", action="store_true", help="Skip prerequisite checks")

    args = parser.parse_args()

    print("🛡️ FRAUD DETECTION API STARTUP")
    print("=" * 50)

    # Check prerequisites
    if not args.skip_checks:
        if not check_prerequisites():
            print("\n❌ Prerequisites check failed!")
            print("🔧 To fix:")
            print("   1. Ensure you've run: python train_fraud_models.py")
            print("   2. Ensure app/main.py exists")
            print("   3. Ensure models/ directory has .pkl files")
            return False

    # Show startup info
    show_startup_info()

    print("\n⏳ Starting server in 3 seconds...")
    time.sleep(3)

    # Start the API server
    success = start_api_server(
        host=args.host, port=args.port, reload=not args.no_reload, workers=args.workers
    )

    if success:
        print("\n✅ API server shut down successfully")
    else:
        print("\n❌ API server encountered an error")

    return success


if __name__ == "__main__":
    main()
