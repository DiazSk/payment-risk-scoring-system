# API Design and Integration

### API Integration Strategy

**API Integration Strategy:** Extend existing FastAPI router in `app/main.py` with new endpoints following current patterns for middleware, authentication, and response formatting

**Authentication:** Maintain existing authentication approach (currently open endpoints for demo, easily secured later with same patterns)

**Versioning:** No versioning required for initial implementation - new endpoints are additive and don't break existing contracts

### New API Endpoints

#### AML Compliance Check Endpoint

**Method:** POST
**Endpoint:** `/aml_check`
**Purpose:** Real-time Anti-Money Laundering compliance analysis for transactions
**Integration:** Follows existing FastAPI route handler patterns, uses current Pydantic validation models

**Request:**
```json
{
  "transaction_id": "txn_12345",
  "user_id": "user_67890",
  "amount": 5000.00,
  "merchant_category": "high_risk",
  "transaction_time": "2025-09-07T14:30:00Z",
  "user_history_days": 30
}
```

**Response:**
```json
{
  "transaction_id": "txn_12345",
  "aml_risk_score": 0.75,
  "compliance_status": "FLAGGED",
  "suspicious_patterns": ["unusual_amount", "high_risk_merchant"],
  "regulatory_flags": {
    "exceeds_daily_threshold": true,
    "rapid_succession": false
  },
  "recommended_action": "REVIEW",
  "analysis_timestamp": "2025-09-07T14:30:01Z"
}
```

#### Velocity Analysis Endpoint

**Method:** POST
**Endpoint:** `/velocity_analysis`
**Purpose:** Multi-timeframe transaction velocity risk assessment
**Integration:** Integrates with existing feature engineering pipeline, follows current error handling patterns

**Request:**
```json
{
  "user_id": "user_67890",
  "current_transaction": {
    "amount": 1500.00,
    "timestamp": "2025-09-07T14:30:00Z"
  },
  "analysis_windows": ["1h", "24h", "7d"],
  "include_baseline": true
}
```

**Response:**
```json
{
  "user_id": "user_67890",
  "velocity_analysis": {
    "1h": {
      "transaction_count": 3,
      "total_amount": 4500.00,
      "velocity_score": 0.85,
      "threshold_exceeded": true
    },
    "24h": {
      "transaction_count": 12,
      "total_amount": 15000.00,
      "velocity_score": 0.65,
      "threshold_exceeded": false
    },
    "7d": {
      "transaction_count": 45,
      "total_amount": 47000.00,
      "velocity_score": 0.45,
      "threshold_exceeded": false
    }
  },
  "baseline_deviation": 2.3,
  "overall_risk_score": 0.72,
  "recommended_action": "APPROVE_WITH_MONITORING"
}
```

#### Enhanced Comprehensive Analysis Endpoint

**Method:** POST
**Endpoint:** `/comprehensive_analysis`
**Purpose:** Combined fraud detection + AML + velocity analysis in single call
**Integration:** Orchestrates existing `/predict` logic with new AML and velocity components

**Request:**
```json
{
  "transaction_data": {
    "amount": 750.00,
    "merchant_category": "online_retail",
    "transaction_time": "2025-09-07T14:30:00Z",
    "user_location": "US",
    "device_type": "mobile"
  },
  "user_id": "user_67890",
  "include_aml": true,
  "include_velocity": true,
  "velocity_windows": ["1h", "24h"]
}
```

**Response:**
```json
{
  "transaction_id": "generated_txn_id",
  "fraud_analysis": {
    "fraud_probability": 0.23,
    "risk_category": "LOW",
    "model_confidence": 0.89
  },
  "aml_analysis": {
    "aml_risk_score": 0.15,
    "compliance_status": "PASSED",
    "suspicious_patterns": []
  },
  "velocity_analysis": {
    "overall_risk_score": 0.35,
    "highest_risk_window": "1h",
    "baseline_deviation": 0.8
  },
  "comprehensive_risk_score": 0.31,
  "final_recommendation": "APPROVE",
  "processing_time_ms": 127
}
```
