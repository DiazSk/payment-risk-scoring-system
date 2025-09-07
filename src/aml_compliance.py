"""
AML (Anti-Money Laundering) Compliance Module
Implements real-world AML detection rules and risk scoring
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json


class AMLComplianceChecker:
    """
    Comprehensive AML compliance checking for payment transactions
    Implements industry-standard AML rules and risk scoring
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize AML checker with configurable rules"""
        self.config = self._load_config(config_path)
        self.risk_thresholds = self.config.get("risk_thresholds", {
            "structuring_threshold": 10000,
            "rapid_movement_threshold": 50000,
            "velocity_threshold": 100000,
            "suspicious_pattern_threshold": 25000
        })
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load AML configuration from file or use defaults"""
        default_config = {
            "risk_thresholds": {
                "structuring_threshold": 10000,  # CTR threshold
                "rapid_movement_threshold": 50000,  # Rapid movement flag
                "velocity_threshold": 100000,  # Daily velocity limit
                "suspicious_pattern_threshold": 25000  # Pattern detection threshold
            },
            "time_windows": {
                "structuring_window_hours": 24,
                "rapid_movement_window_hours": 6,
                "velocity_window_hours": 24
            },
            "sanctions_list": [
                # Simplified sanctions list - in production would be comprehensive
                "SANCTIONED_ENTITY_1",
                "BLOCKED_COUNTRY_CODE"
            ]
        }
        
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    custom_config = json.load(f)
                    default_config.update(custom_config)
            except FileNotFoundError:
                pass  # Use defaults
                
        return default_config
    
    def check_structuring(self, transaction_data: Dict, transaction_history: List[Dict] = None) -> Dict:
        """
        Detect potential structuring (breaking up large transactions to avoid reporting)
        """
        amount = transaction_data.get("transaction_amount", 0)
        
        risk_score = 0.0
        flags = []
        
        # Check for amounts just below reporting thresholds
        ctr_threshold = self.risk_thresholds["structuring_threshold"]
        
        if 0.8 * ctr_threshold <= amount < ctr_threshold:
            risk_score += 0.4
            flags.append("AMOUNT_NEAR_CTR_THRESHOLD")
            
        # Check for multiple transactions in time window (if history available)
        if transaction_history:
            window_hours = self.config["time_windows"]["structuring_window_hours"]
            recent_amounts = [
                t["transaction_amount"] for t in transaction_history
                if self._is_within_time_window(t.get("timestamp"), window_hours)
            ]
            
            total_recent = sum(recent_amounts) + amount
            if total_recent > ctr_threshold and len(recent_amounts) >= 3:
                risk_score += 0.6
                flags.append("MULTIPLE_TRANSACTIONS_ABOVE_THRESHOLD")
                
        return {
            "structuring_risk_score": min(risk_score, 1.0),
            "structuring_flags": flags
        }
    
    def check_rapid_movement(self, transaction_data: Dict, account_history: List[Dict] = None) -> Dict:
        """
        Detect rapid movement of funds (potential laundering)
        """
        amount = transaction_data.get("transaction_amount", 0)
        
        risk_score = 0.0
        flags = []
        
        # Large single transaction
        if amount > self.risk_thresholds["rapid_movement_threshold"]:
            risk_score += 0.3
            flags.append("LARGE_SINGLE_TRANSACTION")
            
        # Check for round amounts (common in laundering)
        if amount % 1000 == 0 and amount >= 5000:
            risk_score += 0.2
            flags.append("ROUND_AMOUNT_TRANSACTION")
            
        # Check velocity if history available
        if account_history:
            window_hours = self.config["time_windows"]["rapid_movement_window_hours"]
            recent_transactions = [
                t for t in account_history
                if self._is_within_time_window(t.get("timestamp"), window_hours)
            ]
            
            if len(recent_transactions) >= 5:
                risk_score += 0.4
                flags.append("HIGH_FREQUENCY_TRANSACTIONS")
                
        return {
            "rapid_movement_risk_score": min(risk_score, 1.0),
            "rapid_movement_flags": flags
        }
    
    def check_suspicious_patterns(self, transaction_data: Dict) -> Dict:
        """
        Detect suspicious transaction patterns
        """
        amount = transaction_data.get("transaction_amount", 0)
        hour = transaction_data.get("transaction_hour", 12)
        merchant_category = transaction_data.get("merchant_category", "UNKNOWN")
        location = transaction_data.get("location", "UNKNOWN")
        
        risk_score = 0.0
        flags = []
        
        # Unusual timing patterns
        if hour < 6 or hour > 22:
            risk_score += 0.2
            flags.append("UNUSUAL_TIMING")
            
        # High-risk merchant categories
        high_risk_categories = ["CASH_ADVANCE", "GAMBLING", "CRYPTOCURRENCY", "MONEY_TRANSFER"]
        if merchant_category in high_risk_categories:
            risk_score += 0.3
            flags.append("HIGH_RISK_MERCHANT_CATEGORY")
            
        # Geographic risk factors
        high_risk_locations = ["OFFSHORE", "SANCTIONS_COUNTRY", "HIGH_RISK_JURISDICTION"]
        if any(risk_loc in location.upper() for risk_loc in high_risk_locations):
            risk_score += 0.4
            flags.append("HIGH_RISK_LOCATION")
            
        # Suspicious amount patterns
        amount_str = str(int(amount))
        if len(set(amount_str)) == 1 and len(amount_str) >= 4:  # e.g., 5555, 7777
            risk_score += 0.3
            flags.append("REPEATED_DIGIT_AMOUNT")
            
        return {
            "suspicious_pattern_risk_score": min(risk_score, 1.0),
            "suspicious_pattern_flags": flags
        }
    
    def check_sanctions_screening(self, transaction_data: Dict) -> Dict:
        """
        Screen against sanctions lists and PEP databases
        """
        customer_name = transaction_data.get("customer_name", "").upper()
        merchant_name = transaction_data.get("merchant_name", "").upper()
        location = transaction_data.get("location", "").upper()
        
        risk_score = 0.0
        flags = []
        
        # Check against sanctions list
        sanctions_list = self.config.get("sanctions_list", [])
        
        for sanctioned_entity in sanctions_list:
            if sanctioned_entity in customer_name or sanctioned_entity in merchant_name:
                risk_score = 1.0
                flags.append("SANCTIONS_MATCH")
                break
                
        # Location-based sanctions check
        if any(sanctions in location for sanctions in sanctions_list):
            risk_score = max(risk_score, 0.8)
            flags.append("SANCTIONS_LOCATION")
            
        return {
            "sanctions_risk_score": risk_score,
            "sanctions_flags": flags
        }
    
    def calculate_overall_aml_risk(self, transaction_data: Dict, 
                                 transaction_history: List[Dict] = None,
                                 account_history: List[Dict] = None) -> Dict:
        """
        Calculate comprehensive AML risk score and generate report
        """
        
        # Run all AML checks
        structuring_result = self.check_structuring(transaction_data, transaction_history)
        rapid_movement_result = self.check_rapid_movement(transaction_data, account_history)
        pattern_result = self.check_suspicious_patterns(transaction_data)
        sanctions_result = self.check_sanctions_screening(transaction_data)
        
        # Calculate weighted overall risk score (more weight on patterns and sanctions)
        weights = {
            "structuring": 0.2,
            "rapid_movement": 0.2,
            "suspicious_patterns": 0.35,
            "sanctions": 0.25
        }
        
        overall_risk = (
            structuring_result["structuring_risk_score"] * weights["structuring"] +
            rapid_movement_result["rapid_movement_risk_score"] * weights["rapid_movement"] +
            pattern_result["suspicious_pattern_risk_score"] * weights["suspicious_patterns"] +
            sanctions_result["sanctions_risk_score"] * weights["sanctions"]
        )
        
        # Determine risk level (more sensitive thresholds)
        if overall_risk >= 0.6:
            risk_level = "HIGH"
        elif overall_risk >= 0.35:
            risk_level = "MEDIUM"
        elif overall_risk >= 0.2:
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"
        
        # Compile all flags
        all_flags = (
            structuring_result["structuring_flags"] +
            rapid_movement_result["rapid_movement_flags"] +
            pattern_result["suspicious_pattern_flags"] +
            sanctions_result["sanctions_flags"]
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(overall_risk, all_flags)
        
        return {
            "aml_overall_risk_score": round(overall_risk, 4),
            "aml_risk_level": risk_level,
            "aml_flags": all_flags,
            "aml_recommendations": recommendations,
            "aml_component_scores": {
                "structuring": round(structuring_result["structuring_risk_score"], 4),
                "rapid_movement": round(rapid_movement_result["rapid_movement_risk_score"], 4),
                "suspicious_patterns": round(pattern_result["suspicious_pattern_risk_score"], 4),
                "sanctions": round(sanctions_result["sanctions_risk_score"], 4)
            },
            "requires_manual_review": overall_risk >= 0.7 or "SANCTIONS_MATCH" in all_flags
        }
    
    def _is_within_time_window(self, timestamp: str, window_hours: int) -> bool:
        """Check if timestamp is within specified time window"""
        try:
            if isinstance(timestamp, str):
                trans_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                trans_time = timestamp
                
            now = datetime.now()
            return (now - trans_time).total_seconds() / 3600 <= window_hours
        except:
            return False
    
    def _generate_recommendations(self, risk_score: float, flags: List[str]) -> List[str]:
        """Generate AML compliance recommendations based on risk assessment"""
        recommendations = []
        
        if risk_score >= 0.8:
            recommendations.append("IMMEDIATE_MANUAL_REVIEW_REQUIRED")
            recommendations.append("CONSIDER_SUSPICIOUS_ACTIVITY_REPORT")
            
        if risk_score >= 0.5:
            recommendations.append("ENHANCED_DUE_DILIGENCE")
            recommendations.append("ADDITIONAL_DOCUMENTATION_REQUIRED")
            
        if "SANCTIONS_MATCH" in flags:
            recommendations.append("BLOCK_TRANSACTION_IMMEDIATELY")
            recommendations.append("REPORT_TO_COMPLIANCE_TEAM")
            
        if any("STRUCTURING" in flag for flag in flags):
            recommendations.append("MONITOR_CUSTOMER_PATTERN")
            recommendations.append("REVIEW_TRANSACTION_HISTORY")
            
        if not recommendations:
            recommendations.append("STANDARD_PROCESSING")
            
        return recommendations


def add_aml_features_to_transaction(transaction_data: Dict, 
                                   aml_checker: AMLComplianceChecker = None) -> Dict:
    """
    Add AML compliance features to transaction data
    """
    if aml_checker is None:
        aml_checker = AMLComplianceChecker()
    
    # Calculate AML risk assessment
    aml_result = aml_checker.calculate_overall_aml_risk(transaction_data)
    
    # Add AML features to transaction data
    enhanced_data = transaction_data.copy()
    enhanced_data.update(aml_result)
    
    return enhanced_data
