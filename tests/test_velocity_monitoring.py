"""
Tests for Velocity Monitoring Module
Comprehensive test suite for transaction velocity monitoring and risk assessment
"""

import pytest
import time
import sys
import os
from datetime import datetime
from unittest.mock import patch

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from velocity_monitoring import VelocityMonitor, add_velocity_features_to_transaction


class TestVelocityMonitor:
    """Test suite for VelocityMonitor class"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.velocity_monitor = VelocityMonitor()
        
        # Sample transaction data
        self.sample_transaction = {
            "transaction_id": "TXN_001",
            "customer_id": "CUST_TEST",
            "transaction_amount": 500.0,
            "transaction_hour": 14,
            "merchant_category": "RETAIL",
            "payment_method": "CARD"
        }
    
    def test_velocity_monitor_initialization(self):
        """Test velocity monitor initialization"""
        monitor = VelocityMonitor()
        
        # Check default configuration
        assert monitor.velocity_thresholds is not None
        assert "max_transactions_per_minute" in monitor.velocity_thresholds
        assert "max_amount_per_minute" in monitor.velocity_thresholds
        assert monitor.time_windows is not None
        assert "minute_window" in monitor.time_windows
        
        # Check initial state
        assert len(monitor.transaction_buffer) == 0
    
    def test_record_transaction(self):
        """Test recording transactions for velocity tracking"""
        customer_id = "CUST_001"
        
        # Record a transaction
        self.velocity_monitor.record_transaction(customer_id, self.sample_transaction)
        
        # Verify transaction was recorded
        assert customer_id in self.velocity_monitor.transaction_buffer
        buffer = self.velocity_monitor.transaction_buffer[customer_id]
        assert len(buffer['transactions']) == 1
        assert len(buffer['amounts']) == 1
        assert len(buffer['timestamps']) == 1
        assert buffer['amounts'][0] == 500.0
    
    def test_velocity_metrics_calculation_empty(self):
        """Test velocity metrics calculation with no transactions"""
        customer_id = "CUST_EMPTY"
        
        metrics = self.velocity_monitor.calculate_velocity_metrics(customer_id)
        
        # All metrics should be zero for empty customer
        assert metrics['minute_window_count'] == 0
        assert metrics['hour_window_count'] == 0
        assert metrics['day_window_count'] == 0
        assert metrics['minute_window_total_amount'] == 0
        assert metrics['hour_window_total_amount'] == 0
        assert metrics['day_window_total_amount'] == 0
    
    def test_velocity_metrics_calculation_with_transactions(self):
        """Test velocity metrics calculation with recorded transactions"""
        customer_id = "CUST_002"
        
        # Record multiple transactions
        for _ in range(5):
            transaction = self.sample_transaction.copy()
            transaction['transaction_amount'] = 100.0 * (_ + 1)
            self.velocity_monitor.record_transaction(customer_id, transaction)
            time.sleep(0.01)  # Small delay to ensure different timestamps
        
        metrics = self.velocity_monitor.calculate_velocity_metrics(customer_id)
        
        # Should have 5 transactions recorded
        assert metrics['minute_window_count'] == 5
        assert metrics['hour_window_count'] == 5
        assert metrics['day_window_count'] == 5
        
        # Check total amounts
        expected_total = 100.0 + 200.0 + 300.0 + 400.0 + 500.0  # 1500.0
        assert metrics['minute_window_total_amount'] == expected_total
        assert metrics['hour_window_total_amount'] == expected_total
        assert metrics['day_window_total_amount'] == expected_total
        
        # Check average amount
        expected_avg = expected_total / 5  # 300.0
        assert metrics['minute_window_avg_amount'] == expected_avg
        assert metrics['hour_window_avg_amount'] == expected_avg
        assert metrics['day_window_avg_amount'] == expected_avg
        
        # Check maximum amount
        assert metrics['minute_window_max_amount'] == 500.0
        assert metrics['hour_window_max_amount'] == 500.0
        assert metrics['day_window_max_amount'] == 500.0
    
    def test_frequency_risk_calculation(self):
        """Test frequency-based risk calculation"""
        customer_id = "CUST_FREQ_TEST"
        
        # Create a scenario with high frequency (above threshold)
        for _ in range(15):  # Above max_transactions_per_minute (10)
            self.velocity_monitor.record_transaction(customer_id, self.sample_transaction)
        
        risk_assessment = self.velocity_monitor.assess_velocity_risk(customer_id, self.sample_transaction)
        
        # Should detect high frequency risk
        assert risk_assessment['velocity_risk_score'] > 0.3
        assert 'HIGH_FREQUENCY_MINUTE' in risk_assessment['velocity_flags']
        assert risk_assessment['velocity_component_scores']['frequency_risk'] > 0
    
    def test_volume_risk_calculation(self):
        """Test volume-based risk calculation"""
        customer_id = "CUST_VOL_TEST"
        
        # Create a scenario with high volume (above threshold)
        high_amount_transaction = self.sample_transaction.copy()
        high_amount_transaction['transaction_amount'] = 60000.0  # Above max_amount_per_minute (50000)
        
        risk_assessment = self.velocity_monitor.assess_velocity_risk(customer_id, high_amount_transaction)
        
        # Should detect high volume risk
        assert risk_assessment['velocity_risk_score'] > 0.2  # Adjusted threshold
        assert 'HIGH_VOLUME_MINUTE' in risk_assessment['velocity_flags']
        assert risk_assessment['velocity_component_scores']['volume_risk'] > 0
    
    def test_pattern_risk_calculation(self):
        """Test pattern-based risk calculation"""
        customer_id = "CUST_PATTERN_TEST"
        
        # Create burst pattern - many transactions in short time
        for _ in range(6):  # Should trigger burst pattern
            self.velocity_monitor.record_transaction(customer_id, self.sample_transaction)
        
        risk_assessment = self.velocity_monitor.assess_velocity_risk(customer_id, self.sample_transaction)
        
        # Should detect burst pattern
        assert 'BURST_PATTERN' in risk_assessment['velocity_flags']
        assert risk_assessment['velocity_component_scores']['pattern_risk'] > 0
    
    @patch('velocity_monitoring.datetime')
    def test_off_hours_detection(self, mock_datetime):
        """Test off-hours activity detection"""
        # Mock off-hours time (2 AM)
        mock_datetime.now.return_value = datetime(2025, 1, 1, 2, 0, 0)
        
        customer_id = "CUST_OFF_HOURS"
        
        # Record multiple transactions during off-hours
        for _ in range(4):
            self.velocity_monitor.record_transaction(customer_id, self.sample_transaction)
        
        risk_assessment = self.velocity_monitor.assess_velocity_risk(customer_id, self.sample_transaction)
        
        # Should detect off-hours activity
        assert 'OFF_HOURS_ACTIVITY' in risk_assessment['velocity_flags']
    
    def test_risk_level_determination(self):
        """Test risk level determination based on score"""
        customer_id = "CUST_RISK_LEVEL"
        
        # Test minimal risk (normal transaction)
        risk_assessment = self.velocity_monitor.assess_velocity_risk(customer_id, self.sample_transaction)
        assert risk_assessment['velocity_risk_level'] in ['MINIMAL', 'LOW']
        
        # Test high risk (multiple high-amount transactions)
        high_risk_transaction = self.sample_transaction.copy()
        high_risk_transaction['transaction_amount'] = 100000.0
        
        for _ in range(20):  # High frequency and volume
            self.velocity_monitor.record_transaction(customer_id, high_risk_transaction)
        
        risk_assessment = self.velocity_monitor.assess_velocity_risk(customer_id, high_risk_transaction)
        assert risk_assessment['velocity_risk_level'] in ['HIGH', 'MEDIUM']
    
    def test_velocity_recommendations(self):
        """Test velocity-based recommendations generation"""
        customer_id = "CUST_RECOMMENDATIONS"
        
        # Create high-risk scenario
        high_risk_transaction = self.sample_transaction.copy()
        high_risk_transaction['transaction_amount'] = 80000.0
        
        for _ in range(25):  # High frequency and volume
            self.velocity_monitor.record_transaction(customer_id, high_risk_transaction)
        
        risk_assessment = self.velocity_monitor.assess_velocity_risk(customer_id, high_risk_transaction)
        
        # Should have recommendations for high-risk scenario
        recommendations = risk_assessment['velocity_recommendations']
        assert len(recommendations) > 0
        assert any('REVIEW' in rec for rec in recommendations)
    
    def test_customer_velocity_summary(self):
        """Test customer velocity summary generation"""
        customer_id = "CUST_SUMMARY"
        
        # Record several transactions
        for idx in range(10):
            transaction = self.sample_transaction.copy()
            transaction['transaction_amount'] = 200.0 * (idx + 1)
            self.velocity_monitor.record_transaction(customer_id, transaction)
        
        summary = self.velocity_monitor.get_customer_velocity_summary(customer_id)
        
        # Verify summary structure and data
        assert summary['customer_id'] == customer_id
        assert summary['total_transactions_24h'] == 10
        assert summary['total_amount_24h'] > 0
        assert summary['avg_amount_24h'] > 0
        assert summary['max_amount_24h'] == 2000.0  # Last transaction amount
        assert 'recent_activity' in summary
        assert 'last_hour_count' in summary['recent_activity']
    
    def test_cleanup_old_transactions(self):
        """Test cleanup of old transactions"""
        customer_id = "CUST_CLEANUP"
        
        # Record a transaction
        self.velocity_monitor.record_transaction(customer_id, self.sample_transaction)
        assert customer_id in self.velocity_monitor.transaction_buffer
        
        # Mock old timestamp to trigger cleanup
        with patch('velocity_monitoring.time') as mock_time:
            # Set current time far in the future
            future_time = time.time() + 1000000  # Far future
            mock_time.time.return_value = future_time
            
            # Force cleanup
            self.velocity_monitor._cleanup_old_transactions()
            
            # Customer buffer should be removed due to old transactions
            assert customer_id not in self.velocity_monitor.transaction_buffer
    
    def test_concurrent_access_thread_safety(self):
        """Test thread safety with concurrent access"""
        import threading
        
        customer_id = "CUST_CONCURRENT"
        results = []
        
        def record_transactions():
            for idx in range(5):
                self.velocity_monitor.record_transaction(customer_id, self.sample_transaction)
                results.append(idx)
        
        # Create multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=record_transactions)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify transactions were recorded safely
        assert customer_id in self.velocity_monitor.transaction_buffer
        buffer = self.velocity_monitor.transaction_buffer[customer_id]
        assert len(buffer['transactions']) == 15  # 3 threads * 5 transactions each
    
    def test_custom_configuration(self):
        """Test velocity monitor with custom configuration"""
        custom_config = {
            "velocity_thresholds": {
                "max_transactions_per_minute": 5,  # Lower threshold
                "max_amount_per_minute": 10000     # Lower threshold
            }
        }
        
        # Create monitor with custom config (would need to implement config parameter)
        monitor = VelocityMonitor()
        monitor.velocity_thresholds = custom_config["velocity_thresholds"]
        
        customer_id = "CUST_CUSTOM"
        
        # Test with transaction that exceeds custom threshold
        for _ in range(6):  # Above custom threshold of 5
            monitor.record_transaction(customer_id, self.sample_transaction)
        
        risk_assessment = monitor.assess_velocity_risk(customer_id, self.sample_transaction)
        
        # Should trigger frequency alert with custom threshold
        assert 'HIGH_FREQUENCY_MINUTE' in risk_assessment['velocity_flags']


class TestVelocityFeatureIntegration:
    """Test velocity monitoring integration with other features"""
    
    def test_add_velocity_features_to_transaction(self):
        """Test adding velocity features to transaction data"""
        transaction_data = {
            "transaction_id": "TXN_INTEGRATION",
            "customer_id": "CUST_INTEGRATION",
            "transaction_amount": 1000.0,
            "transaction_hour": 10
        }
        
        enhanced_data = add_velocity_features_to_transaction(transaction_data)
        
        # Verify velocity features were added
        assert 'velocity_risk_score' in enhanced_data
        assert 'velocity_risk_level' in enhanced_data
        assert 'velocity_flags' in enhanced_data
        assert 'velocity_recommendations' in enhanced_data
        assert 'velocity_metrics' in enhanced_data
        assert 'velocity_component_scores' in enhanced_data
        assert 'requires_velocity_review' in enhanced_data
        
        # Verify original data is preserved
        assert enhanced_data['transaction_id'] == "TXN_INTEGRATION"
        assert enhanced_data['customer_id'] == "CUST_INTEGRATION"
        assert enhanced_data['transaction_amount'] == 1000.0
    
    def test_velocity_features_with_custom_monitor(self):
        """Test velocity features with custom velocity monitor"""
        velocity_monitor = VelocityMonitor()
        
        transaction_data = {
            "customer_id": "CUST_CUSTOM_MONITOR",
            "transaction_amount": 750.0
        }
        
        enhanced_data = add_velocity_features_to_transaction(
            transaction_data, 
            velocity_monitor=velocity_monitor,
            customer_id="CUST_CUSTOM_MONITOR"
        )
        
        # Verify features were added using custom monitor
        assert enhanced_data['velocity_risk_score'] >= 0.0
        assert enhanced_data['velocity_risk_level'] in ['MINIMAL', 'LOW', 'MEDIUM', 'HIGH']
    
    def test_velocity_features_unknown_customer(self):
        """Test velocity features with unknown customer ID"""
        transaction_data = {
            "transaction_amount": 300.0,
            "transaction_hour": 15
        }
        
        enhanced_data = add_velocity_features_to_transaction(transaction_data)
        
        # Should handle missing customer_id gracefully
        assert 'velocity_risk_score' in enhanced_data
        assert enhanced_data['velocity_risk_score'] >= 0.0


if __name__ == "__main__":
    pytest.main([__file__])
