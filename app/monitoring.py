"""
Production Monitoring System for Fraud Detection API
Real-time performance tracking and system health monitoring
"""

import os
import json
import time
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Deque
from dataclasses import dataclass
from pathlib import Path
from collections import deque
import warnings
warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PredictionLog:
    """Individual prediction log entry"""
    transaction_id: str
    prediction: bool
    fraud_probability: float
    model_used: str
    timestamp: datetime
    response_time_ms: float
    risk_level: str

@dataclass
class SystemMetrics:
    """System performance metrics"""
    total_requests: int = 0
    successful_predictions: int = 0
    failed_predictions: int = 0
    total_fraud_detected: int = 0
    avg_response_time_ms: float = 0.0
    uptime_seconds: float = 0.0
    last_updated: Optional[datetime] = None

class PerformanceMonitor:
    """Monitor API and model performance"""
    
    def __init__(self, max_logs: int = 10000):
        self.start_time = datetime.now()
        self.prediction_logs: Deque[PredictionLog] = deque(maxlen=max_logs)  # Circular buffer for memory efficiency
        self.response_times: Deque[float] = deque(maxlen=1000)  # Keep last 1000 response times
        
        # Metrics
        self.metrics = SystemMetrics()
        self.metrics.last_updated = datetime.now()
        
        # Performance thresholds
        self.thresholds = {
            'max_response_time_ms': 1000,
            'min_success_rate': 0.95,
            'max_error_rate': 0.05
        }
        
        # Load baseline performance if exists
        self._load_baseline_performance()
    
    def _load_baseline_performance(self):
        """Load baseline performance metrics from model metadata"""
        try:
            metadata_path = Path("models/model_metadata.json")
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    self.baseline_performance = metadata.get('performance_summary', {})
                    logger.info("✅ Baseline performance loaded")
            else:
                self.baseline_performance = {}
        except Exception as e:
            logger.warning(f"Could not load baseline performance: {e}")
            self.baseline_performance = {}
    
    def log_prediction(self, 
                      transaction_id: str,
                      prediction: bool,
                      fraud_probability: float,
                      model_used: str,
                      response_time_ms: float,
                      risk_level: str):
        """Log a successful prediction"""
        
        log_entry = PredictionLog(
            transaction_id=transaction_id,
            prediction=prediction,
            fraud_probability=fraud_probability,
            model_used=model_used,
            timestamp=datetime.now(),
            response_time_ms=response_time_ms,
            risk_level=risk_level
        )
        
        # Update logs
        self.prediction_logs.append(log_entry)
        self.response_times.append(response_time_ms)
        
        # Update metrics
        self.metrics.total_requests += 1
        self.metrics.successful_predictions += 1
        if prediction:
            self.metrics.total_fraud_detected += 1
        
        # Update average response time
        if self.response_times:
            self.metrics.avg_response_time_ms = float(np.mean(list(self.response_times)))
        
        self.metrics.last_updated = datetime.now()
        
        # Check for performance issues
        self._check_performance_alerts(response_time_ms)
    
    def log_failed_prediction(self, error_msg: str, response_time_ms: float):
        """Log a failed prediction"""
        
        self.metrics.total_requests += 1
        self.metrics.failed_predictions += 1
        self.response_times.append(response_time_ms)
        self.metrics.last_updated = datetime.now()
        
        logger.error(f"Prediction failed: {error_msg}")
    
    def _check_performance_alerts(self, response_time_ms: float):
        """Check for performance issues and log alerts"""
        
        # Check response time
        if response_time_ms > self.thresholds['max_response_time_ms']:
            logger.warning(f"⚠️ High response time: {response_time_ms:.1f}ms")
        
        # Check error rate
        if self.metrics.total_requests > 100:  # Only check after sufficient requests
            error_rate = self.metrics.failed_predictions / self.metrics.total_requests
            if error_rate > self.thresholds['max_error_rate']:
                logger.warning(f"⚠️ High error rate: {error_rate:.2%}")
    
    def get_metrics(self, window_hours: int = 24) -> Dict[str, Any]:
        """Get performance metrics for specified time window"""
        
        # Calculate uptime
        uptime_seconds = (datetime.now() - self.start_time).total_seconds()
        self.metrics.uptime_seconds = uptime_seconds
        
        # Filter logs by time window if needed
        if window_hours < float('inf'):
            cutoff_time = datetime.now() - timedelta(hours=window_hours)
            recent_logs = [log for log in self.prediction_logs 
                          if log.timestamp >= cutoff_time]
        else:
            recent_logs = list(self.prediction_logs)
        
        # Calculate metrics for the window
        if recent_logs:
            fraud_count = sum(1 for log in recent_logs if log.prediction)
            fraud_rate = fraud_count / len(recent_logs)
            
            risk_distribution = {
                'HIGH': sum(1 for log in recent_logs if log.risk_level == 'HIGH'),
                'MEDIUM': sum(1 for log in recent_logs if log.risk_level == 'MEDIUM'),
                'LOW': sum(1 for log in recent_logs if log.risk_level == 'LOW'),
                'VERY_LOW': sum(1 for log in recent_logs if log.risk_level == 'VERY_LOW')
            }
        else:
            fraud_rate = 0
            risk_distribution = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'VERY_LOW': 0}
        
        return {
            'total_requests': self.metrics.total_requests,
            'successful_predictions': self.metrics.successful_predictions,
            'failed_predictions': self.metrics.failed_predictions,
            'success_rate': self.metrics.successful_predictions / max(self.metrics.total_requests, 1),
            'error_rate': self.metrics.failed_predictions / max(self.metrics.total_requests, 1),
            'total_fraud_detected': self.metrics.total_fraud_detected,
            'fraud_rate': fraud_rate,
            'avg_response_time_ms': self.metrics.avg_response_time_ms,
            'max_response_time_ms': float(max(self.response_times)) if self.response_times else 0,
            'min_response_time_ms': float(min(self.response_times)) if self.response_times else 0,
            'p95_response_time_ms': float(np.percentile(list(self.response_times), 95)) if self.response_times else 0,
            'uptime_seconds': uptime_seconds,
            'uptime_hours': uptime_seconds / 3600,
            'predictions_per_hour': self.metrics.total_requests / max(uptime_seconds / 3600, 0.001),
            'risk_distribution': risk_distribution,
            'window_hours': window_hours,
            'last_updated': self.metrics.last_updated.isoformat() if self.metrics.last_updated else None
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        
        metrics = self.get_metrics(window_hours=1)  # Last hour metrics
        
        # Determine health status
        health_score = 100
        issues = []
        
        # Check success rate
        if metrics['success_rate'] < self.thresholds['min_success_rate']:
            health_score -= 30
            issues.append(f"Low success rate: {metrics['success_rate']:.1%}")
        
        # Check response time
        if metrics['avg_response_time_ms'] > self.thresholds['max_response_time_ms']:
            health_score -= 20
            issues.append(f"High response time: {metrics['avg_response_time_ms']:.0f}ms")
        
        # Check error rate
        if metrics['error_rate'] > self.thresholds['max_error_rate']:
            health_score -= 25
            issues.append(f"High error rate: {metrics['error_rate']:.1%}")
        
        # Determine status
        if health_score >= 90:
            status = "HEALTHY"
        elif health_score >= 70:
            status = "DEGRADED"
        elif health_score >= 50:
            status = "WARNING"
        else:
            status = "CRITICAL"
        
        return {
            'status': status,
            'health_score': health_score,
            'issues': issues,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_recent_predictions(self, limit: int = 10) -> List[Dict]:
        """Get recent prediction logs"""
        
        recent = list(self.prediction_logs)[-limit:]
        return [
            {
                'transaction_id': log.transaction_id,
                'prediction': log.prediction,
                'fraud_probability': log.fraud_probability,
                'risk_level': log.risk_level,
                'model_used': log.model_used,
                'response_time_ms': log.response_time_ms,
                'timestamp': log.timestamp.isoformat()
            }
            for log in reversed(recent)
        ]
    
    def generate_summary_report(self) -> str:
        """Generate a summary report of system performance"""
        
        metrics = self.get_metrics()
        health = self.get_health_status()
        
        report = f"""
🛡️ FRAUD DETECTION SYSTEM - MONITORING REPORT
{'='*50}
📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
⏱️ Uptime: {metrics['uptime_hours']:.1f} hours

📊 PERFORMANCE METRICS
{'='*30}
Total Requests: {metrics['total_requests']:,}
Success Rate: {metrics['success_rate']:.1%}
Error Rate: {metrics['error_rate']:.1%}
Avg Response Time: {metrics['avg_response_time_ms']:.1f}ms
P95 Response Time: {metrics['p95_response_time_ms']:.1f}ms

🚨 FRAUD DETECTION
{'='*30}
Total Fraud Detected: {metrics['total_fraud_detected']:,}
Fraud Rate: {metrics['fraud_rate']:.2%}
High Risk: {metrics['risk_distribution']['HIGH']}
Medium Risk: {metrics['risk_distribution']['MEDIUM']}
Low Risk: {metrics['risk_distribution']['LOW']}

🏥 SYSTEM HEALTH: {health['status']}
{'='*30}
Health Score: {health['health_score']}/100
"""
        
        if health['issues']:
            report += "Issues Detected:\n"
            for issue in health['issues']:
                report += f"  ⚠️ {issue}\n"
        else:
            report += "✅ No issues detected\n"
        
        report += "\n" + "="*50
        
        return report

class ModelPerformanceTracker:
    """Track model-specific performance metrics"""
    
    def __init__(self):
        self.model_metrics = {}
        self.model_usage_count = {}
        
    def track_model_prediction(self, model_name: str, 
                              actual_fraud: Optional[bool], 
                              predicted_fraud: bool,
                              fraud_probability: float):
        """Track performance for a specific model"""
        
        if model_name not in self.model_metrics:
            self.model_metrics[model_name] = {
                'predictions': [],
                'true_positives': 0,
                'false_positives': 0,
                'true_negatives': 0,
                'false_negatives': 0
            }
            self.model_usage_count[model_name] = 0
        
        self.model_usage_count[model_name] += 1
        
        # If we have ground truth, update confusion matrix
        if actual_fraud is not None:
            if actual_fraud and predicted_fraud:
                self.model_metrics[model_name]['true_positives'] += 1
            elif actual_fraud and not predicted_fraud:
                self.model_metrics[model_name]['false_negatives'] += 1
            elif not actual_fraud and predicted_fraud:
                self.model_metrics[model_name]['false_positives'] += 1
            else:
                self.model_metrics[model_name]['true_negatives'] += 1
    
    def get_model_performance(self, model_name: str) -> Dict[str, Any]:
        """Get performance metrics for a specific model"""
        
        if model_name not in self.model_metrics:
            return {'error': 'Model not found'}
        
        metrics = self.model_metrics[model_name]
        
        # Calculate performance metrics
        tp = metrics['true_positives']
        fp = metrics['false_positives']
        tn = metrics['true_negatives']
        fn = metrics['false_negatives']
        
        total = tp + fp + tn + fn
        
        if total == 0:
            return {
                'model': model_name,
                'usage_count': self.model_usage_count[model_name],
                'message': 'No ground truth data available'
            }
        
        accuracy = (tp + tn) / total if total > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'model': model_name,
            'usage_count': self.model_usage_count[model_name],
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'confusion_matrix': {
                'true_positives': tp,
                'false_positives': fp,
                'true_negatives': tn,
                'false_negatives': fn
            }
        }

# Global monitor instances
performance_monitor = PerformanceMonitor()
model_tracker = ModelPerformanceTracker()

def get_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance"""
    return performance_monitor

def get_model_tracker() -> ModelPerformanceTracker:
    """Get the global model tracker instance"""
    return model_tracker

# Convenience functions for API integration
def log_api_request(transaction_id: str, 
                   prediction_result: Dict,
                   response_time_ms: float):
    """Log an API prediction request"""
    
    performance_monitor.log_prediction(
        transaction_id=transaction_id,
        prediction=prediction_result.get('is_fraud', False),
        fraud_probability=prediction_result.get('fraud_probability', 0.0),
        model_used=prediction_result.get('model_used', 'unknown'),
        response_time_ms=response_time_ms,
        risk_level=prediction_result.get('risk_level', 'UNKNOWN')
    )

def get_api_metrics() -> Dict[str, Any]:
    """Get current API performance metrics"""
    return performance_monitor.get_metrics()

def get_api_health() -> Dict[str, Any]:
    """Get current API health status"""
    return performance_monitor.get_health_status()

def get_monitoring_report() -> str:
    """Get a formatted monitoring report"""
    return performance_monitor.generate_summary_report()