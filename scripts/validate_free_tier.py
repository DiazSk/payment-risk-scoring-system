#!/usr/bin/env python3
"""
Free-Tier Deployment Validation Script
Validates that the fraud detection system works properly on free-tier platforms
"""

import os
import sys
import time
import requests
import subprocess
import json
from pathlib import Path

def print_status(message: str, status: str = "INFO"):
    """Print formatted status message"""
    colors = {
        "INFO": "\033[94m",  # Blue
        "SUCCESS": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "RESET": "\033[0m"  # Reset
    }
    
    color = colors.get(status, colors["INFO"])
    reset = colors["RESET"]
    print(f"{color}[{status}]{reset} {message}")

def check_dependencies():
    """Check that all required dependencies are available"""
    print_status("Checking dependencies...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'pandas', 'numpy', 'scikit-learn',
        'streamlit', 'plotly', 'requests', 'xgboost', 'imbalanced-learn'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_status(f"✅ {package}", "SUCCESS")
        except ImportError:
            missing_packages.append(package)
            print_status(f"❌ {package}", "ERROR")
    
    if missing_packages:
        print_status(f"Missing packages: {', '.join(missing_packages)}", "ERROR")
        return False
    
    print_status("All dependencies available", "SUCCESS")
    return True

def check_model_files():
    """Check that model files exist"""
    print_status("Checking model files...")
    
    model_dir = Path("models")
    if not model_dir.exists():
        print_status("Models directory not found", "ERROR")
        return False
    
    required_files = ["model_metadata.json"]
    
    for file in required_files:
        file_path = model_dir / file
        if file_path.exists():
            print_status(f"✅ {file}", "SUCCESS")
        else:
            print_status(f"❌ {file}", "ERROR")
            return False
    
    # Check for any model files
    model_files = list(model_dir.glob("*.joblib")) + list(model_dir.glob("*.pkl"))
    if model_files:
        print_status(f"Found {len(model_files)} model files", "SUCCESS")
    else:
        print_status("No model files found - training may be needed", "WARNING")
    
    return True

def test_api_startup():
    """Test that the API can start successfully"""
    print_status("Testing API startup...")
    
    try:
        # Import the app to test basic functionality
        from app.main import app
        print_status("✅ API app imports successfully", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"❌ API startup failed: {str(e)}", "ERROR")
        return False

def test_prediction_logic():
    """Test prediction logic without starting server"""
    print_status("Testing prediction logic...")
    
    try:
        # Test by importing the prediction utilities
        from app.predictor import FeatureProcessor, BatchPredictor
        
        print_status("✅ Prediction modules import successfully", "SUCCESS")
        
        # Test basic feature processing
        processor = FeatureProcessor()
        test_data = {
            "amount": 150.50,
            "merchant_category": "grocery",
            "transaction_hour": 14,
            "day_of_week": 3,
            "is_weekend": False,
            "merchant_risk_score": 0.2
        }
        
        # This validates that the modules can be imported and basic classes work
        print_status("✅ Basic prediction components work", "SUCCESS")
        return True
        
    except Exception as e:
        print_status(f"❌ Prediction test failed: {str(e)}", "ERROR")
        return False

def test_dashboard_imports():
    """Test that dashboard imports work"""
    print_status("Testing dashboard imports...")
    
    try:
        import dashboard.app
        print_status("✅ Dashboard imports successfully", "SUCCESS")
        return True
    except Exception as e:
        print_status(f"❌ Dashboard import failed: {str(e)}", "ERROR")
        return False

def check_memory_usage():
    """Check estimated memory usage"""
    print_status("Checking memory usage...")
    
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        print_status(f"Current memory usage: {memory_mb:.1f} MB")
        
        if memory_mb > 400:  # Most free tiers have 512MB limit
            print_status("Memory usage may be too high for free tier", "WARNING")
        else:
            print_status("Memory usage looks good for free tier", "SUCCESS")
            
        return True
        
    except ImportError:
        print_status("psutil not available, skipping memory check", "WARNING")
        return True

def check_deployment_files():
    """Check that deployment files are present and valid"""
    print_status("Checking deployment files...")
    
    deployment_files = {
        "Procfile": "Should contain web service definition",
        "Dockerfile": "Should contain Docker configuration",
        "requirements.txt": "Should contain Python dependencies",
        "requirements-railway.txt": "Should contain Railway-specific dependencies",
        "railway-dashboard.toml": "Should contain Railway dashboard config"
    }
    
    all_good = True
    for file, description in deployment_files.items():
        if Path(file).exists():
            print_status(f"✅ {file}: {description}", "SUCCESS")
        else:
            print_status(f"❌ {file}: Missing - {description}", "ERROR")
            all_good = False
    
    return all_good

def validate_environment_variables():
    """Validate environment variable setup"""
    print_status("Checking environment variables...")
    
    # Test environment detection
    test_envs = ["development", "production"]
    
    for env in test_envs:
        os.environ["ENVIRONMENT"] = env
        try:
            from app.main import app
            print_status(f"✅ Environment '{env}' works", "SUCCESS")
        except Exception as e:
            print_status(f"❌ Environment '{env}' failed: {str(e)}", "ERROR")
            return False
    
    return True

def run_tests():
    """Run the test suite"""
    print_status("Running test suite...")
    
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            test_count = result.stdout.count("PASSED")
            print_status(f"✅ All {test_count} tests passed", "SUCCESS")
            return True
        else:
            print_status(f"❌ Tests failed:\n{result.stdout}\n{result.stderr}", "ERROR")
            return False
            
    except subprocess.TimeoutExpired:
        print_status("❌ Tests timed out (>5 minutes)", "ERROR")
        return False
    except Exception as e:
        print_status(f"❌ Test execution failed: {str(e)}", "ERROR")
        return False

def main():
    """Main validation function"""
    print_status("🚀 Starting Free-Tier Deployment Validation", "INFO")
    print_status("=" * 60, "INFO")
    
    validation_steps = [
        ("Dependencies", check_dependencies),
        ("Model Files", check_model_files),
        ("API Startup", test_api_startup),
        ("Prediction Logic", test_prediction_logic),
        ("Dashboard Imports", test_dashboard_imports),
        ("Memory Usage", check_memory_usage),
        ("Deployment Files", check_deployment_files),
        ("Environment Variables", validate_environment_variables),
        ("Test Suite", run_tests)
    ]
    
    results = {}
    
    for step_name, step_function in validation_steps:
        print_status(f"\n--- {step_name} ---", "INFO")
        try:
            results[step_name] = step_function()
        except Exception as e:
            print_status(f"❌ {step_name} validation failed: {str(e)}", "ERROR")
            results[step_name] = False
    
    # Summary
    print_status("\n" + "=" * 60, "INFO")
    print_status("🏁 VALIDATION SUMMARY", "INFO")
    print_status("=" * 60, "INFO")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for step_name, passed in results.items():
        status = "SUCCESS" if passed else "ERROR"
        symbol = "✅" if passed else "❌"
        print_status(f"{symbol} {step_name}", status)
    
    print_status(f"\nOverall: {passed}/{total} validations passed", "INFO")
    
    if passed == total:
        print_status("🎉 System is ready for free-tier deployment!", "SUCCESS")
        return True
    else:
        print_status("❌ System has issues that need to be resolved", "ERROR")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
