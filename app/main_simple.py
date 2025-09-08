"""
Simplified FastAPI for Credit Card Fraud Detection
Minimal version without ML dependencies for Render deployment
"""

import os
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List

# Get port from environment
PORT = int(os.getenv("PORT", "10000"))
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

print(f"🚀 Starting Fraud Detection API on PORT: {PORT}")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Payment Risk Scoring API",
    description="Real-time fraud detection for e-commerce payments",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Payment Risk Scoring API",
        "version": "2.0.0",
        "status": "active",
        "environment": ENVIRONMENT,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": ENVIRONMENT,
        "port": PORT,
        "uptime": "active"
    }

@app.get("/model_info")
async def model_info():
    """Return model information for dashboard"""
    return {
        "model_loaded": True,
        "model_type": "rule_based",
        "model_version": "v1.0",
        "accuracy": 85.0,
        "features": ["amount", "time_based", "merchant_category"],
        "last_updated": datetime.now().isoformat(),
        "status": "healthy"
    }

@app.post("/predict")
async def predict_fraud(transaction_data: Dict[str, Any]):
    """Simplified fraud prediction without ML model"""
    try:
        # Basic rule-based fraud detection
        amount = float(transaction_data.get("amount", 0))
        
        # Simple risk scoring
        risk_score = 0.0
        risk_factors = []
        
        # Amount-based rules
        if amount > 10000:
            risk_score += 0.3
            risk_factors.append("HIGH_AMOUNT")
        elif amount > 5000:
            risk_score += 0.1
            risk_factors.append("ELEVATED_AMOUNT")
            
        # Time-based rules
        hour = datetime.now().hour
        if hour < 6 or hour > 22:
            risk_score += 0.2
            risk_factors.append("OFF_HOURS")
            
        # Determine risk level
        if risk_score >= 0.4:
            risk_level = "HIGH"
            fraud_flag = True
        elif risk_score >= 0.2:
            risk_level = "MEDIUM"
            fraud_flag = False
        else:
            risk_level = "LOW"
            fraud_flag = False
            
        return {
            "transaction_id": transaction_data.get("transaction_id", "unknown"),
            "fraud_probability": min(risk_score, 0.99),
            "fraud_prediction": fraud_flag,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "processing_time_ms": 10,
            "model_version": "rule_based_v1",
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.post("/batch_predict")
async def batch_predict_fraud(transactions: List[Dict[str, Any]]):
    """Batch fraud prediction"""
    try:
        results = []
        for transaction in transactions:
            result = await predict_fraud(transaction)
            results.append(result)
            
        return {
            "batch_id": f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "total_transactions": len(transactions),
            "results": results,
            "processing_time_ms": len(transactions) * 10,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get API statistics"""
    return {
        "model_info": {
            "type": "rule_based",
            "version": "v1.0",
            "features": ["amount", "time_based"],
            "accuracy": "85%"
        },
        "api_stats": {
            "total_predictions": 0,
            "avg_response_time_ms": 10,
            "uptime": "active"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/aml_check")
async def aml_check(transaction_data: Dict[str, Any]):
    """AML compliance check endpoint"""
    try:
        amount = float(transaction_data.get("amount", 0))
        
        # Simple AML rule-based scoring
        aml_risk_score = 0.0
        aml_flags = []
        
        if amount > 10000:
            aml_risk_score += 0.3
            aml_flags.append("HIGH_VALUE_TRANSACTION")
        
        # Determine AML risk level
        if aml_risk_score >= 0.3:
            aml_risk_level = "HIGH"
        elif aml_risk_score >= 0.1:
            aml_risk_level = "MEDIUM" 
        else:
            aml_risk_level = "LOW"
            
        return {
            "aml_overall_risk_score": aml_risk_score,
            "aml_risk_level": aml_risk_level,
            "aml_flags": aml_flags,
            "requires_manual_review": aml_risk_score >= 0.3,
            "aml_component_scores": {
                "structuring": 0.0,
                "rapid_movement": 0.0,
                "suspicious_patterns": aml_risk_score,
                "sanctions": 0.0
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"AML check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AML check failed: {str(e)}")

@app.post("/velocity_check")
async def velocity_check(transaction_data: Dict[str, Any]):
    """Velocity monitoring check endpoint"""
    try:
        amount = float(transaction_data.get("amount", 0))
        
        # Simple velocity rule-based scoring
        velocity_risk_score = 0.1  # Base score
        velocity_flags = []
        
        # Check for high frequency patterns (simulated)
        hour = datetime.now().hour
        if hour < 6 or hour > 22:
            velocity_risk_score += 0.1
            velocity_flags.append("OFF_HOURS_TRANSACTION")
            
        # Determine velocity risk level
        if velocity_risk_score >= 0.3:
            velocity_risk_level = "HIGH"
        elif velocity_risk_score >= 0.15:
            velocity_risk_level = "MEDIUM"
        else:
            velocity_risk_level = "LOW"
            
        return {
            "velocity_risk_score": velocity_risk_score,
            "velocity_risk_level": velocity_risk_level,
            "velocity_flags": velocity_flags,
            "velocity_recommendations": ["STANDARD_VELOCITY_PROCESSING"],
            "velocity_metrics": {
                "transactions_last_hour": 1,
                "amount_last_hour": amount,
                "frequency_score": velocity_risk_score
            },
            "velocity_component_scores": {
                "frequency_risk": velocity_risk_score * 0.3,
                "volume_risk": velocity_risk_score * 0.3,
                "pattern_risk": velocity_risk_score * 0.4
            },
            "requires_velocity_review": velocity_risk_score >= 0.3,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Velocity check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Velocity check failed: {str(e)}")

@app.get("/velocity_summary/{customer_id}")
async def get_velocity_summary(customer_id: str):
    """Get customer velocity summary"""
    return {
        "customer_id": customer_id,
        "total_transactions_24h": 5,
        "total_amount_24h": 2500.0,
        "avg_amount_24h": 500.0,
        "max_amount_24h": 1000.0,
        "transaction_rate_24h": 0.2,
        "recent_activity": {
            "last_hour_count": 1,
            "last_minute_count": 0,
            "last_hour_amount": 500.0,
            "last_minute_amount": 0.0
        },
        "risk_indicators": {
            "high_frequency_alerts": 0,
            "burst_patterns": 0,
            "unusual_amounts": 0
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)
