"""
Test suite for AML Compliance features
"""

import pytest
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent / "src"))

try:
    from aml_compliance import AMLComplianceChecker, add_aml_features_to_transaction
except ImportError:
    pytest.skip("AML compliance module not available", allow_module_level=True)


class TestAMLCompliance:
    """Test AML compliance functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        self.aml_checker = AMLComplianceChecker()
        
    def test_aml_checker_initialization(self):
        """Test AML checker initialization"""
        assert self.aml_checker is not None
        assert hasattr(self.aml_checker, 'risk_thresholds')
        assert hasattr(self.aml_checker, 'config')
        
    def test_structuring_detection_low_risk(self):
        """Test structuring detection for low risk transactions"""
        transaction_data = {
            "transaction_amount": 1000,
            "customer_name": "John Doe",
            "timestamp": "2025-09-07T10:00:00Z"
        }
        
        result = self.aml_checker.check_structuring(transaction_data)
        
        assert "structuring_risk_score" in result
        assert "structuring_flags" in result
        assert result["structuring_risk_score"] <= 0.5  # Should be low risk
        
    def test_structuring_detection_high_risk(self):
        """Test structuring detection for high risk transactions"""
        transaction_data = {
            "transaction_amount": 9500,  # Just below CTR threshold
            "customer_name": "Jane Smith",
            "timestamp": "2025-09-07T10:00:00Z"
        }
        
        result = self.aml_checker.check_structuring(transaction_data)
        
        assert result["structuring_risk_score"] > 0
        assert "AMOUNT_NEAR_CTR_THRESHOLD" in result["structuring_flags"]
        
    def test_rapid_movement_detection(self):
        """Test rapid movement detection"""
        transaction_data = {
            "transaction_amount": 75000,  # Large amount
            "customer_name": "Big Corp",
            "timestamp": "2025-09-07T10:00:00Z"
        }
        
        result = self.aml_checker.check_rapid_movement(transaction_data)
        
        assert "rapid_movement_risk_score" in result
        assert "rapid_movement_flags" in result
        assert result["rapid_movement_risk_score"] > 0
        assert "LARGE_SINGLE_TRANSACTION" in result["rapid_movement_flags"]
        
    def test_suspicious_patterns_detection(self):
        """Test suspicious pattern detection"""
        transaction_data = {
            "transaction_amount": 5000,
            "transaction_hour": 3,  # Very early morning
            "merchant_category": "GAMBLING",  # High risk category
            "location": "OFFSHORE",  # High risk location
            "customer_name": "Test Customer"
        }
        
        result = self.aml_checker.check_suspicious_patterns(transaction_data)
        
        assert "suspicious_pattern_risk_score" in result
        assert "suspicious_pattern_flags" in result
        assert result["suspicious_pattern_risk_score"] > 0
        assert "UNUSUAL_TIMING" in result["suspicious_pattern_flags"]
        assert "HIGH_RISK_MERCHANT_CATEGORY" in result["suspicious_pattern_flags"]
        assert "HIGH_RISK_LOCATION" in result["suspicious_pattern_flags"]
        
    def test_sanctions_screening_clean(self):
        """Test sanctions screening for clean transaction"""
        transaction_data = {
            "customer_name": "John Doe",
            "merchant_name": "Local Store",
            "location": "DOMESTIC"
        }
        
        result = self.aml_checker.check_sanctions_screening(transaction_data)
        
        assert "sanctions_risk_score" in result
        assert "sanctions_flags" in result
        assert result["sanctions_risk_score"] == 0.0  # Should be clean
        assert len(result["sanctions_flags"]) == 0
        
    def test_overall_aml_risk_calculation(self):
        """Test overall AML risk calculation"""
        transaction_data = {
            "transaction_amount": 5000,
            "transaction_hour": 14,  # Business hours
            "customer_name": "Regular Customer",
            "merchant_name": "Normal Store",
            "location": "DOMESTIC",
            "merchant_category": "RETAIL"
        }
        
        result = self.aml_checker.calculate_overall_aml_risk(transaction_data)
        
        # Check required fields
        required_fields = [
            "aml_overall_risk_score", "aml_risk_level", "aml_flags",
            "aml_recommendations", "aml_component_scores", "requires_manual_review"
        ]
        
        for field in required_fields:
            assert field in result, f"Missing required field: {field}"
            
        # Check risk score is in valid range
        assert 0 <= result["aml_overall_risk_score"] <= 1
        
        # Check risk level is valid
        assert result["aml_risk_level"] in ["MINIMAL", "LOW", "MEDIUM", "HIGH"]
        
        # Check component scores
        component_scores = result["aml_component_scores"]
        for component, score in component_scores.items():
            assert 0 <= score <= 1, f"Component {component} score {score} out of range"
            
    def test_high_risk_transaction(self):
        """Test high risk transaction requiring manual review"""
        transaction_data = {
            "transaction_amount": 9800,  # Near CTR threshold
            "transaction_hour": 2,  # Unusual timing
            "customer_name": "SANCTIONED_ENTITY_1",  # Sanctions match
            "merchant_name": "Cash Plus",
            "location": "OFFSHORE",
            "merchant_category": "CASH_ADVANCE"
        }
        
        result = self.aml_checker.calculate_overall_aml_risk(transaction_data)
        
        # Should be high risk
        assert result["aml_overall_risk_score"] > 0.5
        assert result["aml_risk_level"] in ["MEDIUM", "HIGH"]
        assert result["requires_manual_review"] == True
        assert len(result["aml_flags"]) > 0
        
        # Should have multiple recommendations
        assert len(result["aml_recommendations"]) > 0
        
    def test_add_aml_features_to_transaction(self):
        """Test adding AML features to transaction data"""
        transaction_data = {
            "transaction_amount": 2500,
            "transaction_hour": 15,
            "customer_name": "Test Customer"
        }
        
        enhanced_data = add_aml_features_to_transaction(transaction_data, self.aml_checker)
        
        # Original data should be preserved
        for key, value in transaction_data.items():
            assert enhanced_data[key] == value
            
        # AML features should be added
        aml_fields = [
            "aml_overall_risk_score", "aml_risk_level", "aml_flags",
            "aml_recommendations", "aml_component_scores", "requires_manual_review"
        ]
        
        for field in aml_fields:
            assert field in enhanced_data
            
    def test_round_amount_detection(self):
        """Test detection of round amounts (potential money laundering indicator)"""
        transaction_data = {
            "transaction_amount": 10000,  # Round amount
            "customer_name": "Test Customer"
        }
        
        result = self.aml_checker.check_rapid_movement(transaction_data)
        
        # Should detect round amount if above threshold
        if transaction_data["transaction_amount"] >= 5000:
            assert "ROUND_AMOUNT_TRANSACTION" in result["rapid_movement_flags"]
            
    def test_repeated_digit_amount_detection(self):
        """Test detection of repeated digit amounts"""
        transaction_data = {
            "transaction_amount": 7777,  # Repeated digits
            "customer_name": "Test Customer"
        }
        
        result = self.aml_checker.check_suspicious_patterns(transaction_data)
        
        assert "REPEATED_DIGIT_AMOUNT" in result["suspicious_pattern_flags"]
        
    def test_business_hours_vs_unusual_timing(self):
        """Test difference between business hours and unusual timing"""
        # Business hours transaction
        business_hours_data = {
            "transaction_amount": 1000,
            "transaction_hour": 14,  # 2 PM
            "customer_name": "Business Customer"
        }
        
        business_result = self.aml_checker.check_suspicious_patterns(business_hours_data)
        assert "UNUSUAL_TIMING" not in business_result["suspicious_pattern_flags"]
        
        # Unusual timing transaction
        unusual_timing_data = {
            "transaction_amount": 1000,
            "transaction_hour": 3,  # 3 AM
            "customer_name": "Night Customer"
        }
        
        unusual_result = self.aml_checker.check_suspicious_patterns(unusual_timing_data)
        assert "UNUSUAL_TIMING" in unusual_result["suspicious_pattern_flags"]
        
    def test_aml_risk_levels(self):
        """Test different AML risk levels"""
        test_cases = [
            # Minimal risk
            {
                "data": {"transaction_amount": 50, "transaction_hour": 14},
                "expected_level": "MINIMAL"
            },
            # High risk
            {
                "data": {
                    "transaction_amount": 9900,
                    "transaction_hour": 2,
                    "merchant_category": "GAMBLING",
                    "location": "OFFSHORE"
                },
                "expected_level": ["MEDIUM", "HIGH"]
            }
        ]
        
        for case in test_cases:
            result = self.aml_checker.calculate_overall_aml_risk(case["data"])
            
            if isinstance(case["expected_level"], list):
                assert result["aml_risk_level"] in case["expected_level"]
            else:
                assert result["aml_risk_level"] == case["expected_level"]


def test_aml_integration_availability():
    """Test that AML integration is available and working"""
    try:
        aml_checker = AMLComplianceChecker()
        
        # Test basic functionality
        test_data = {"transaction_amount": 1000}
        result = aml_checker.calculate_overall_aml_risk(test_data)
        
        assert "aml_overall_risk_score" in result
        assert isinstance(result["aml_overall_risk_score"], (int, float))
        assert 0 <= result["aml_overall_risk_score"] <= 1
        
        print("✅ AML compliance integration is working correctly")
        
    except Exception as e:
        pytest.fail(f"AML integration failed: {e}")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
