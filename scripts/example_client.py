#!/usr/bin/env python3
"""
Fraud Detection API Client Example
Shows how to interact with the fraud detection API
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

class FraudDetectionClient:
    """Client for interacting with the Fraud Detection API"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
        
    def check_health(self) -> Dict[str, Any]:
        """Check API health status"""
        response = self.session.get(f"{self.api_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models"""
        response = self.session.get(f"{self.api_url}/model_info")
        response.raise_for_status()
        return response.json()
    
    def predict_single_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Predict fraud for a single transaction"""
        response = self.session.post(
            f"{self.api_url}/predict",
            json=transaction
        )
        response.raise_for_status()
        return response.json()
    
    def predict_batch_transactions(self, transactions: List[Dict[str, Any]], 
                                  model_name: str = None) -> Dict[str, Any]:
        """Predict fraud for multiple transactions"""
        payload = {"transactions": transactions}
        if model_name:
            payload["model_name"] = model_name
            
        response = self.session.post(
            f"{self.api_url}/batch_predict",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get API performance metrics"""
        response = self.session.get(f"{self.api_url}/metrics")
        response.raise_for_status()
        return response.json()

def example_usage():
    """Demonstrate API usage with examples"""
    
    print("🚀 FRAUD DETECTION API CLIENT EXAMPLE")
    print("=" * 60)
    
    # Initialize client
    client = FraudDetectionClient()
    
    try:
        # 1. Check API health
        print("\n1. 🔍 Checking API health...")
        health = client.check_health()
        print(f"   Status: {health['status']}")
        print(f"   Models loaded: {health['models_loaded']}")
        print(f"   Available models: {', '.join(health['available_models'])}")
        
        # 2. Get model information
        print("\n2. 📊 Getting model information...")
        model_info = client.get_model_info()
        print(f"   Best model: {model_info['best_model']}")
        print(f"   Feature count: {model_info['feature_count']}")
        
        # 3. Single transaction prediction
        print("\n3. 🎯 Testing single transaction prediction...")
        
        # Example: Normal transaction
        normal_transaction = {
            "transaction_amount": 45.99,
            "transaction_hour": 14,  # 2 PM
            "transaction_day": 15,
            "transaction_weekend": 0,  # Weekday
            "is_business_hours": 1,
            "card_amount_mean": 52.30,
            "card_txn_count_recent": 2,
            "time_since_last_txn": 7200.0,  # 2 hours
            "merchant_risk_score": 0.1,  # Low risk merchant
            "amount_zscore": -0.3,  # Below average amount
            "is_amount_outlier": 0
        }
        
        result = client.predict_single_transaction(normal_transaction)
        print(f"   Normal transaction result:")
        print(f"     Is fraud: {result['is_fraud']}")
        print(f"     Fraud probability: {result['fraud_probability']:.3f}")
        print(f"     Risk level: {result['risk_level']}")
        print(f"     Confidence: {result['confidence']:.3f}")
        
        # Example: Suspicious transaction
        suspicious_transaction = {
            "transaction_amount": 2500.00,  # High amount
            "transaction_hour": 3,  # 3 AM
            "transaction_day": 15,
            "transaction_weekend": 1,  # Weekend
            "is_business_hours": 0,
            "card_amount_mean": 75.50,
            "card_txn_count_recent": 8,  # Many recent transactions
            "time_since_last_txn": 300.0,  # 5 minutes ago
            "merchant_risk_score": 0.7,  # High risk merchant
            "amount_zscore": 5.2,  # Way above average
            "is_amount_outlier": 1
        }
        
        result = client.predict_single_transaction(suspicious_transaction)
        print(f"\n   Suspicious transaction result:")
        print(f"     Is fraud: {result['is_fraud']}")
        print(f"     Fraud probability: {result['fraud_probability']:.3f}")
        print(f"     Risk level: {result['risk_level']}")
        print(f"     Confidence: {result['confidence']:.3f}")
        
        # 4. Batch prediction
        print("\n4. 📦 Testing batch prediction...")
        
        batch_transactions = [
            {
                "transaction_amount": 29.99,
                "transaction_hour": 10,
                "transaction_day": 15,
                "transaction_weekend": 0,
                "is_business_hours": 1,
                "card_amount_mean": 45.00,
                "card_txn_count_recent": 1,
                "time_since_last_txn": 86400.0,
                "merchant_risk_score": 0.1,
                "amount_zscore": -1.0,
                "is_amount_outlier": 0
            },
            {
                "transaction_amount": 1200.00,
                "transaction_hour": 23,
                "transaction_day": 15,
                "transaction_weekend": 1,
                "is_business_hours": 0,
                "card_amount_mean": 60.00,
                "card_txn_count_recent": 5,
                "time_since_last_txn": 600.0,
                "merchant_risk_score": 0.6,
                "amount_zscore": 8.0,
                "is_amount_outlier": 1
            },
            {
                "transaction_amount": 67.50,
                "transaction_hour": 15,
                "transaction_day": 15,
                "transaction_weekend": 0,
                "is_business_hours": 1,
                "card_amount_mean": 70.00,
                "card_txn_count_recent": 2,
                "time_since_last_txn": 3600.0,
                "merchant_risk_score": 0.2,
                "amount_zscore": -0.2,
                "is_amount_outlier": 0
            }
        ]
        
        batch_result = client.predict_batch_transactions(batch_transactions)
        print(f"   Batch prediction results:")
        print(f"     Total transactions: {batch_result['summary']['total_transactions']}")
        print(f"     Fraud detected: {batch_result['summary']['fraud_detected']}")
        print(f"     Fraud rate: {batch_result['summary']['fraud_rate']:.1%}")
        print(f"     High risk transactions: {batch_result['summary']['high_risk_transactions']}")
        
        print(f"\n   Individual results:")
        for i, prediction in enumerate(batch_result['predictions']):
            print(f"     Transaction {i+1}: {prediction['risk_level']} "
                  f"(probability: {prediction['fraud_probability']:.3f})")
        
        # 5. Performance metrics
        print("\n5. 📈 Getting performance metrics...")
        metrics = client.get_metrics()
        print(f"   API uptime: {metrics['api_uptime_seconds']:.1f} seconds")
        print(f"   Models loaded: {metrics['models_loaded']}")
        print(f"   Best model: {metrics['best_model']}")
        
        print("\n🎉 API client example completed successfully!")
        print("\n💡 Integration Tips:")
        print("   - Use batch predictions for processing multiple transactions")
        print("   - Monitor the fraud probability threshold based on your business needs")
        print("   - Consider the risk level (VERY_LOW, LOW, MEDIUM, HIGH) for different actions")
        print("   - Implement retry logic and error handling for production use")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure it's running:")
        print("   python app/main.py")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def performance_benchmark():
    """Run a performance benchmark"""
    
    print("\n🚀 PERFORMANCE BENCHMARK")
    print("=" * 40)
    
    client = FraudDetectionClient()
    
    # Sample transaction for benchmarking
    benchmark_transaction = {
        "transaction_amount": 99.99,
        "transaction_hour": 14,
        "transaction_day": 15,
        "transaction_weekend": 0,
        "is_business_hours": 1,
        "card_amount_mean": 85.50,
        "card_txn_count_recent": 3,
        "time_since_last_txn": 1800.0,
        "merchant_risk_score": 0.15,
        "amount_zscore": 0.8,
        "is_amount_outlier": 0
    }
    
    # Warmup request
    try:
        client.predict_single_transaction(benchmark_transaction)
        print("✅ API warmed up")
    except:
        print("❌ API not available for benchmark")
        return
    
    # Performance test
    num_requests = 100
    response_times = []
    
    print(f"🔄 Running {num_requests} requests...")
    
    for i in range(num_requests):
        start_time = time.time()
        try:
            client.predict_single_transaction(benchmark_transaction)
            end_time = time.time()
            response_times.append((end_time - start_time) * 1000)  # Convert to ms
            
            if (i + 1) % 25 == 0:
                print(f"   Completed {i + 1} requests...")
                
        except Exception as e:
            print(f"   Request {i + 1} failed: {e}")
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        p95_time = sorted(response_times)[int(len(response_times) * 0.95)]
        
        print(f"\n📊 Performance Results:")
        print(f"   Successful requests: {len(response_times)}/{num_requests}")
        print(f"   Average response time: {avg_time:.1f}ms")
        print(f"   Min response time: {min_time:.1f}ms")
        print(f"   Max response time: {max_time:.1f}ms")
        print(f"   95th percentile: {p95_time:.1f}ms")
        
        # Throughput calculation
        total_time = sum(response_times) / 1000  # Convert to seconds
        throughput = len(response_times) / total_time
        print(f"   Estimated throughput: {throughput:.0f} requests/second")
        
        if avg_time < 100:
            print("🚀 Excellent performance! Sub-100ms average response time.")
        elif avg_time < 200:
            print("✅ Good performance! Under 200ms average response time.")
        else:
            print("⚠️  Performance could be improved. Consider optimization.")

def main():
    """Main function"""
    
    print("🛡️ FRAUD DETECTION API CLIENT")
    print("Interactive client for testing the fraud detection system")
    print("=" * 70)
    
    # Run example usage
    success = example_usage()
    
    if success:
        # Run performance benchmark
        print("\n" + "="*70)
        performance_benchmark()
        
        print("\n" + "="*70)
        print("✅ CLIENT EXAMPLE COMPLETED SUCCESSFULLY!")
        print("\n🎯 Your fraud detection API is working perfectly!")
        print("\n📚 Additional Resources:")
        print("   - Interactive API docs: http://localhost:8000/docs")
        print("   - API homepage: http://localhost:8000")
        print("   - Model metrics: http://localhost:8000/metrics")
    else:
        print("\n❌ Could not connect to API. Please ensure it's running.")

if __name__ == "__main__":
    main()