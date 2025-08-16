#!/usr/bin/env python3
"""
FastAPI Testing Script
Test all API endpoints to ensure everything works correctly
"""

import requests
import json
import time
from datetime import datetime
import asyncio
import sys

class FraudAPITester:
    """Test the Fraud Detection API"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def test_health_endpoint(self):
        """Test the health check endpoint"""
        print("🔍 Testing health endpoint...")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed")
                print(f"   Status: {data['status']}")
                print(f"   Models loaded: {data['models_loaded']}")
                print(f"   Available models: {data['available_models']}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_model_info_endpoint(self):
        """Test the model info endpoint"""
        print("\n🔍 Testing model info endpoint...")
        
        try:
            response = self.session.get(f"{self.base_url}/model_info")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Model info retrieved")
                print(f"   Best model: {data['best_model']}")
                print(f"   Available models: {data['available_models']}")
                print(f"   Feature count: {data['feature_count']}")
                return True
            else:
                print(f"❌ Model info failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Model info error: {e}")
            return False
    
    def test_single_prediction(self):
        """Test single fraud prediction"""
        print("\n🔍 Testing single prediction...")
        
        # Create sample transaction data
        sample_transaction = {
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
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/predict",
                json=sample_transaction
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Single prediction successful")
                print(f"   Is fraud: {data['is_fraud']}")
                print(f"   Fraud probability: {data['fraud_probability']:.3f}")
                print(f"   Risk level: {data['risk_level']}")
                print(f"   Model used: {data['model_used']}")
                print(f"   Confidence: {data['confidence']:.3f}")
                return True
            else:
                print(f"❌ Single prediction failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Single prediction error: {e}")
            return False
    
    def test_batch_prediction(self):
        """Test batch fraud prediction"""
        print("\n🔍 Testing batch prediction...")
        
        # Create sample batch data
        transactions = []
        for i in range(5):
            transaction = {
                "transaction_amount": 100.0 + i * 50,
                "transaction_hour": 10 + i,
                "transaction_day": 15,
                "transaction_weekend": i % 2,
                "is_business_hours": 1,
                "card_amount_mean": 75.0 + i * 10,
                "card_txn_count_recent": i + 1,
                "time_since_last_txn": 1800.0 * i,
                "merchant_risk_score": 0.1 + i * 0.1,
                "amount_zscore": i - 2,
                "is_amount_outlier": 1 if i > 3 else 0
            }
            transactions.append(transaction)
        
        batch_request = {
            "transactions": transactions
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/batch_predict",
                json=batch_request
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Batch prediction successful")
                print(f"   Total transactions: {data['summary']['total_transactions']}")
                print(f"   Fraud detected: {data['summary']['fraud_detected']}")
                print(f"   Fraud rate: {data['summary']['fraud_rate']:.2%}")
                print(f"   High risk transactions: {data['summary']['high_risk_transactions']}")
                
                # Show individual predictions
                print(f"\n   Individual predictions:")
                for i, pred in enumerate(data['predictions'][:3]):  # Show first 3
                    print(f"     Transaction {i+1}: {pred['risk_level']} risk ({pred['fraud_probability']:.3f})")
                
                return True
            else:
                print(f"❌ Batch prediction failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Batch prediction error: {e}")
            return False
    
    def test_metrics_endpoint(self):
        """Test the metrics endpoint"""
        print("\n🔍 Testing metrics endpoint...")
        
        try:
            response = self.session.get(f"{self.base_url}/metrics")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Metrics retrieved")
                print(f"   API uptime: {data['api_uptime_seconds']:.1f} seconds")
                print(f"   Models loaded: {data['models_loaded']}")
                print(f"   Best model: {data['best_model']}")
                return True
            else:
                print(f"❌ Metrics failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Metrics error: {e}")
            return False
    
    def test_api_performance(self, num_requests=10):
        """Test API response time performance"""
        print(f"\n🔍 Testing API performance ({num_requests} requests)...")
        
        sample_transaction = {
            "transaction_amount": 99.99,
            "transaction_hour": 12,
            "transaction_day": 15,
            "transaction_weekend": 0,
            "is_business_hours": 1,
            "card_amount_mean": 75.50,
            "card_txn_count_recent": 2,
            "time_since_last_txn": 1200.0,
            "merchant_risk_score": 0.15,
            "amount_zscore": 0.5,
            "is_amount_outlier": 0
        }
        
        response_times = []
        successful_requests = 0
        
        for i in range(num_requests):
            try:
                start_time = time.time()
                
                response = self.session.post(
                    f"{self.base_url}/predict",
                    json=sample_transaction
                )
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to ms
                
                if response.status_code == 200:
                    response_times.append(response_time)
                    successful_requests += 1
                
            except Exception as e:
                print(f"   Request {i+1} failed: {e}")
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            print(f"✅ Performance test completed")
            print(f"   Successful requests: {successful_requests}/{num_requests}")
            print(f"   Average response time: {avg_response_time:.1f}ms")
            print(f"   Min response time: {min_response_time:.1f}ms")
            print(f"   Max response time: {max_response_time:.1f}ms")
            
            return avg_response_time < 200  # Should be under 200ms
        else:
            print(f"❌ No successful requests in performance test")
            return False
    
    def wait_for_api(self, timeout=30):
        """Wait for API to be ready"""
        print(f"⏳ Waiting for API to be ready (timeout: {timeout}s)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.session.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    print("✅ API is ready!")
                    return True
            except:
                pass
            
            time.sleep(1)
        
        print("❌ API not ready within timeout")
        return False
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 FRAUD DETECTION API TEST SUITE")
        print("=" * 60)
        
        # Wait for API to be ready
        if not self.wait_for_api():
            print("❌ API is not responding. Make sure it's running:")
            print("   python app/main.py")
            return False
        
        # Run tests
        tests = [
            ("Health Check", self.test_health_endpoint),
            ("Model Info", self.test_model_info_endpoint),
            ("Single Prediction", self.test_single_prediction),
            ("Batch Prediction", self.test_batch_prediction),
            ("Metrics", self.test_metrics_endpoint),
            ("Performance", lambda: self.test_api_performance(10))
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                print(f"❌ {test_name} test failed with exception: {e}")
        
        # Final report
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Tests passed: {passed_tests}/{total_tests}")
        print(f"Success rate: {passed_tests/total_tests:.1%}")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! Your API is working perfectly!")
            print("\n🚀 Next steps:")
            print("   1. API is production ready")
            print("   2. Access interactive docs at: http://localhost:8000/docs")
            print("   3. Try the web interface at: http://localhost:8000")
            print("   4. Ready for deployment!")
            return True
        else:
            print("⚠️  Some tests failed. Check the API and models.")
            return False

def main():
    """Main test runner"""
    
    # Check if API URL provided
    api_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
    
    # Run tests
    tester = FraudAPITester(api_url)
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Your FastAPI fraud detection system is working perfectly!")
    else:
        print("\n❌ Some tests failed. Check the API server.")
    
    return success

if __name__ == "__main__":
    main()