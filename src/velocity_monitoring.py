"""
Transaction Velocity Monitoring Module
Implements real-time velocity tracking and risk scoring for payment transactions
"""

from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict, deque
import json
import threading
import time


class VelocityMonitor:
    """
    Real-time transaction velocity monitoring and risk assessment
    Tracks transaction frequency and volume across multiple time windows
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize velocity monitor with configurable thresholds"""
        self.config = self._load_config(config_path)
        self.velocity_thresholds = self.config.get("velocity_thresholds", {})
        self.time_windows = self.config.get("time_windows", {})
        
        # In-memory transaction storage for velocity calculations
        self.transaction_buffer = defaultdict(lambda: {
            'transactions': deque(),
            'amounts': deque(),
            'timestamps': deque()
        })
        
        # Thread lock for concurrent access
        self._lock = threading.Lock()
        
        # Cleanup old transactions periodically
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # 5 minutes
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load velocity monitoring configuration"""
        default_config = {
            "velocity_thresholds": {
                # Transaction count thresholds
                "max_transactions_per_minute": 10,
                "max_transactions_per_hour": 100,
                "max_transactions_per_day": 500,
                
                # Amount thresholds
                "max_amount_per_minute": 50000,
                "max_amount_per_hour": 200000,
                "max_amount_per_day": 1000000,
                
                # Risk scoring thresholds
                "high_velocity_threshold": 0.8,
                "medium_velocity_threshold": 0.5,
                "low_velocity_threshold": 0.3
            },
            "time_windows": {
                "minute_window": 60,      # 1 minute in seconds
                "hour_window": 3600,      # 1 hour in seconds
                "day_window": 86400,      # 24 hours in seconds
                "week_window": 604800     # 7 days in seconds
            },
            "risk_weights": {
                "frequency_weight": 0.4,   # Weight for transaction frequency
                "volume_weight": 0.4,      # Weight for transaction volume
                "pattern_weight": 0.2      # Weight for pattern anomalies
            }
        }
        
        if config_path:
            try:
                with open(config_path, 'r') as f:
                    custom_config = json.load(f)
                    default_config.update(custom_config)
            except FileNotFoundError:
                pass  # Use defaults
                
        return default_config
    
    def record_transaction(self, customer_id: str, transaction_data: Dict) -> None:
        """Record a new transaction for velocity tracking"""
        with self._lock:
            current_time = time.time()
            amount = float(transaction_data.get("transaction_amount", 0))
            
            # Add transaction to buffer
            customer_buffer = self.transaction_buffer[customer_id]
            customer_buffer['transactions'].append(transaction_data)
            customer_buffer['amounts'].append(amount)
            customer_buffer['timestamps'].append(current_time)
            
            # Cleanup old transactions if needed
            if current_time - self._last_cleanup > self._cleanup_interval:
                self._cleanup_old_transactions()
                self._last_cleanup = current_time
    
    def _cleanup_old_transactions(self) -> None:
        """Remove transactions older than the longest time window"""
        current_time = time.time()
        max_window = max(self.time_windows.values())
        cutoff_time = current_time - max_window
        
        for customer_id in list(self.transaction_buffer.keys()):
            customer_buffer = self.transaction_buffer[customer_id]
            
            # Remove old transactions
            while (customer_buffer['timestamps'] and 
                   customer_buffer['timestamps'][0] < cutoff_time):
                customer_buffer['transactions'].popleft()
                customer_buffer['amounts'].popleft()
                customer_buffer['timestamps'].popleft()
            
            # Remove empty buffers
            if not customer_buffer['timestamps']:
                del self.transaction_buffer[customer_id]
    
    def calculate_velocity_metrics(self, customer_id: str, current_time: Optional[float] = None) -> Dict:
        """Calculate velocity metrics for a customer"""
        if current_time is None:
            current_time = time.time()
            
        customer_buffer = self.transaction_buffer.get(customer_id, {
            'transactions': deque(),
            'amounts': deque(),
            'timestamps': deque()
        })
        
        timestamps = list(customer_buffer['timestamps'])
        amounts = list(customer_buffer['amounts'])
        
        if not timestamps:
            return self._empty_velocity_metrics()
        
        velocity_metrics = {}
        
        # Calculate metrics for each time window
        for window_name, window_seconds in self.time_windows.items():
            cutoff_time = current_time - window_seconds
            
            # Filter transactions within window
            window_transactions = []
            window_amounts = []
            
            for timestamp, amount in zip(timestamps, amounts):
                if timestamp >= cutoff_time:
                    window_transactions.append(timestamp)
                    window_amounts.append(amount)
            
            # Calculate metrics for this window
            velocity_metrics[f"{window_name}_count"] = len(window_transactions)
            velocity_metrics[f"{window_name}_total_amount"] = sum(window_amounts)
            velocity_metrics[f"{window_name}_avg_amount"] = (
                sum(window_amounts) / len(window_amounts) if window_amounts else 0
            )
            velocity_metrics[f"{window_name}_max_amount"] = max(window_amounts) if window_amounts else 0
            
            # Calculate transaction rate (transactions per second)
            if window_transactions:
                time_span = max(window_transactions) - min(window_transactions)
                velocity_metrics[f"{window_name}_rate"] = (
                    len(window_transactions) / max(time_span, 1) if time_span > 0 else len(window_transactions)
                )
            else:
                velocity_metrics[f"{window_name}_rate"] = 0
        
        return velocity_metrics
    
    def _empty_velocity_metrics(self) -> Dict:
        """Return empty velocity metrics structure"""
        metrics = {}
        for window_name in self.time_windows.keys():
            metrics[f"{window_name}_count"] = 0
            metrics[f"{window_name}_total_amount"] = 0
            metrics[f"{window_name}_avg_amount"] = 0
            metrics[f"{window_name}_max_amount"] = 0
            metrics[f"{window_name}_rate"] = 0
        return metrics
    
    def assess_velocity_risk(self, customer_id: str, transaction_data: Dict) -> Dict:
        """Assess velocity-based risk for a transaction"""
        
        # Record the current transaction for velocity tracking
        self.record_transaction(customer_id, transaction_data)
        
        # Calculate current velocity metrics
        velocity_metrics = self.calculate_velocity_metrics(customer_id)
        
        # Calculate risk scores for different aspects
        frequency_risk = self._calculate_frequency_risk(velocity_metrics)
        volume_risk = self._calculate_volume_risk(velocity_metrics)
        pattern_risk = self._calculate_pattern_risk(velocity_metrics, transaction_data)
        
        # Calculate overall velocity risk score
        weights = self.config["risk_weights"]
        overall_risk = (
            frequency_risk * weights["frequency_weight"] +
            volume_risk * weights["volume_weight"] +
            pattern_risk * weights["pattern_weight"]
        )
        
        # Determine risk level
        velocity_thresholds = self.velocity_thresholds
        if overall_risk >= velocity_thresholds.get("high_velocity_threshold", 0.8):
            risk_level = "HIGH"
        elif overall_risk >= velocity_thresholds.get("medium_velocity_threshold", 0.5):
            risk_level = "MEDIUM"
        elif overall_risk >= velocity_thresholds.get("low_velocity_threshold", 0.3):
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"
        
        # Generate velocity flags
        velocity_flags = self._generate_velocity_flags(velocity_metrics, transaction_data)
        
        # Generate recommendations
        recommendations = self._generate_velocity_recommendations(overall_risk, velocity_flags)
        
        return {
            "velocity_risk_score": round(overall_risk, 4),
            "velocity_risk_level": risk_level,
            "velocity_flags": velocity_flags,
            "velocity_recommendations": recommendations,
            "velocity_metrics": velocity_metrics,
            "velocity_component_scores": {
                "frequency_risk": round(frequency_risk, 4),
                "volume_risk": round(volume_risk, 4),
                "pattern_risk": round(pattern_risk, 4)
            },
            "requires_velocity_review": overall_risk >= 0.7
        }
    
    def _calculate_frequency_risk(self, velocity_metrics: Dict) -> float:
        """Calculate risk score based on transaction frequency"""
        thresholds = self.velocity_thresholds
        risk_score = 0.0
        
        # Check minute frequency
        minute_count = velocity_metrics.get("minute_window_count", 0)
        max_per_minute = thresholds.get("max_transactions_per_minute", 10)
        if minute_count > max_per_minute:
            risk_score = max(risk_score, min(minute_count / max_per_minute, 2.0) / 2.0)
        
        # Check hour frequency
        hour_count = velocity_metrics.get("hour_window_count", 0)
        max_per_hour = thresholds.get("max_transactions_per_hour", 100)
        if hour_count > max_per_hour:
            risk_score = max(risk_score, min(hour_count / max_per_hour, 2.0) / 2.0)
        
        # Check day frequency
        day_count = velocity_metrics.get("day_window_count", 0)
        max_per_day = thresholds.get("max_transactions_per_day", 500)
        if day_count > max_per_day:
            risk_score = max(risk_score, min(day_count / max_per_day, 2.0) / 2.0)
        
        return min(risk_score, 1.0)
    
    def _calculate_volume_risk(self, velocity_metrics: Dict) -> float:
        """Calculate risk score based on transaction volume"""
        thresholds = self.velocity_thresholds
        risk_score = 0.0
        
        # Check minute volume
        minute_amount = velocity_metrics.get("minute_window_total_amount", 0)
        max_amount_per_minute = thresholds.get("max_amount_per_minute", 50000)
        if minute_amount > max_amount_per_minute:
            risk_score = max(risk_score, min(minute_amount / max_amount_per_minute, 2.0) / 2.0)
        
        # Check hour volume
        hour_amount = velocity_metrics.get("hour_window_total_amount", 0)
        max_amount_per_hour = thresholds.get("max_amount_per_hour", 200000)
        if hour_amount > max_amount_per_hour:
            risk_score = max(risk_score, min(hour_amount / max_amount_per_hour, 2.0) / 2.0)
        
        # Check day volume
        day_amount = velocity_metrics.get("day_window_total_amount", 0)
        max_amount_per_day = thresholds.get("max_amount_per_day", 1000000)
        if day_amount > max_amount_per_day:
            risk_score = max(risk_score, min(day_amount / max_amount_per_day, 2.0) / 2.0)
        
        return min(risk_score, 1.0)
    
    def _calculate_pattern_risk(self, velocity_metrics: Dict, transaction_data: Dict) -> float:
        """Calculate risk score based on unusual patterns"""
        risk_score = 0.0
        
        # Check for burst patterns (many transactions in short time)
        minute_count = velocity_metrics.get("minute_window_count", 0)
        hour_count = velocity_metrics.get("hour_window_count", 0)
        
        if minute_count > 0 and hour_count > 0:
            burst_ratio = minute_count / max(hour_count / 60, 1)  # Normalize to per-minute rate
            if burst_ratio > 5:  # More than 5x the average rate
                risk_score += 0.3
        
        # Check for unusual timing patterns
        current_hour = datetime.now().hour
        if current_hour < 6 or current_hour > 22:  # Off-hours activity
            if minute_count > 3:  # Multiple transactions during off-hours
                risk_score += 0.2
        
        # Check for escalating amounts
        minute_avg = velocity_metrics.get("minute_window_avg_amount", 0)
        hour_avg = velocity_metrics.get("hour_window_avg_amount", 0)
        current_amount = float(transaction_data.get("transaction_amount", 0))
        
        if minute_avg > 0 and current_amount > minute_avg * 3:  # Current transaction 3x average
            risk_score += 0.2
        
        if hour_avg > 0 and minute_avg > hour_avg * 2:  # Recent minute average 2x hour average
            risk_score += 0.3
        
        return min(risk_score, 1.0)
    
    def _generate_velocity_flags(self, velocity_metrics: Dict, transaction_data: Dict) -> List[str]:
        """Generate velocity-related flags"""
        flags = []
        thresholds = self.velocity_thresholds
        
        # Frequency flags
        if velocity_metrics.get("minute_window_count", 0) > thresholds.get("max_transactions_per_minute", 10):
            flags.append("HIGH_FREQUENCY_MINUTE")
        
        if velocity_metrics.get("hour_window_count", 0) > thresholds.get("max_transactions_per_hour", 100):
            flags.append("HIGH_FREQUENCY_HOUR")
        
        if velocity_metrics.get("day_window_count", 0) > thresholds.get("max_transactions_per_day", 500):
            flags.append("HIGH_FREQUENCY_DAY")
        
        # Volume flags
        if velocity_metrics.get("minute_window_total_amount", 0) > thresholds.get("max_amount_per_minute", 50000):
            flags.append("HIGH_VOLUME_MINUTE")
        
        if velocity_metrics.get("hour_window_total_amount", 0) > thresholds.get("max_amount_per_hour", 200000):
            flags.append("HIGH_VOLUME_HOUR")
        
        if velocity_metrics.get("day_window_total_amount", 0) > thresholds.get("max_amount_per_day", 1000000):
            flags.append("HIGH_VOLUME_DAY")
        
        # Pattern flags
        minute_count = velocity_metrics.get("minute_window_count", 0)
        if minute_count >= 5:
            flags.append("BURST_PATTERN")
        
        current_hour = datetime.now().hour
        if (current_hour < 6 or current_hour > 22) and minute_count > 0:
            flags.append("OFF_HOURS_ACTIVITY")
        
        # Rate flags
        minute_rate = velocity_metrics.get("minute_window_rate", 0)
        if minute_rate > 0.5:  # More than 0.5 transactions per second
            flags.append("RAPID_FIRE_TRANSACTIONS")
        
        return flags
    
    def _generate_velocity_recommendations(self, risk_score: float, flags: List[str]) -> List[str]:
        """Generate velocity-based recommendations"""
        recommendations = []
        
        if risk_score >= 0.8:
            recommendations.append("IMMEDIATE_VELOCITY_REVIEW")
            recommendations.append("TEMPORARY_TRANSACTION_HOLD")
        
        if risk_score >= 0.6:
            recommendations.append("ENHANCED_VELOCITY_MONITORING")
            recommendations.append("CUSTOMER_VERIFICATION_REQUIRED")
        
        if "BURST_PATTERN" in flags:
            recommendations.append("INVESTIGATE_BURST_ACTIVITY")
        
        if "HIGH_FREQUENCY_MINUTE" in flags:
            recommendations.append("RATE_LIMIT_CUSTOMER")
        
        if "OFF_HOURS_ACTIVITY" in flags:
            recommendations.append("VERIFY_CUSTOMER_LOCATION")
        
        if "RAPID_FIRE_TRANSACTIONS" in flags:
            recommendations.append("CHECK_FOR_AUTOMATED_ACTIVITY")
        
        if not recommendations:
            recommendations.append("STANDARD_VELOCITY_PROCESSING")
        
        return recommendations
    
    def get_customer_velocity_summary(self, customer_id: str) -> Dict:
        """Get summary of customer's velocity metrics"""
        velocity_metrics = self.calculate_velocity_metrics(customer_id)
        
        # Calculate summary statistics
        summary = {
            "customer_id": customer_id,
            "total_transactions_24h": velocity_metrics.get("day_window_count", 0),
            "total_amount_24h": velocity_metrics.get("day_window_total_amount", 0),
            "avg_amount_24h": velocity_metrics.get("day_window_avg_amount", 0),
            "max_amount_24h": velocity_metrics.get("day_window_max_amount", 0),
            "transaction_rate_24h": velocity_metrics.get("day_window_rate", 0),
            "recent_activity": {
                "last_hour_count": velocity_metrics.get("hour_window_count", 0),
                "last_minute_count": velocity_metrics.get("minute_window_count", 0),
                "last_hour_amount": velocity_metrics.get("hour_window_total_amount", 0),
                "last_minute_amount": velocity_metrics.get("minute_window_total_amount", 0)
            }
        }
        
        return summary


def add_velocity_features_to_transaction(transaction_data: Dict, 
                                        velocity_monitor: Optional[VelocityMonitor] = None,
                                        customer_id: Optional[str] = None) -> Dict:
    """
    Add velocity monitoring features to transaction data
    """
    if velocity_monitor is None:
        velocity_monitor = VelocityMonitor()
    
    if customer_id is None:
        customer_id = transaction_data.get("customer_id", "UNKNOWN")
    
    # Ensure customer_id is a string
    if not isinstance(customer_id, str):
        customer_id = str(customer_id)
    
    # Assess velocity risk
    velocity_result = velocity_monitor.assess_velocity_risk(customer_id, transaction_data)
    
    # Add velocity features to transaction data
    enhanced_data = transaction_data.copy()
    enhanced_data.update(velocity_result)
    
    return enhanced_data
