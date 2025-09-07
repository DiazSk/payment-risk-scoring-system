# Data Models and Schema Changes

### New Data Models

#### AML Compliance Model

**Purpose:** Track Anti-Money Laundering compliance checks and suspicious activity patterns
**Integration:** Extends existing Pydantic models in `app/models.py` following current validation patterns

**Key Attributes:**
- `transaction_id`: str - Links to existing transaction prediction flow
- `aml_risk_score`: float - Compliance risk score (0.0-1.0)
- `suspicious_patterns`: List[str] - Detected pattern types (rapid_transfers, unusual_amounts, high_risk_merchants)
- `regulatory_flags`: Dict[str, bool] - Threshold violations for compliance reporting
- `watchlist_matches`: List[str] - Potential entity matches requiring review
- `compliance_status`: str - PASSED, FLAGGED, REQUIRES_REVIEW
- `check_timestamp`: datetime - When AML analysis was performed

**Relationships:**
- **With Existing:** Links to current transaction prediction via shared transaction_id
- **With New:** Connects to VelocityCheck model for comprehensive risk assessment

#### Velocity Check Model

**Purpose:** Monitor transaction velocity patterns across multiple time windows
**Integration:** Complements existing feature engineering pipeline with velocity-specific tracking

**Key Attributes:**
- `user_id`: str - Customer identifier for velocity tracking
- `time_window`: str - Analysis period (1h, 24h, 7d)
- `transaction_count`: int - Number of transactions in window
- `total_amount`: float - Sum of transaction amounts in window
- `velocity_score`: float - Risk score based on velocity patterns (0.0-1.0)
- `baseline_deviation`: float - How much current velocity deviates from user's normal pattern
- `risk_threshold_exceeded`: bool - Whether velocity exceeds configured risk limits
- `window_start`: datetime - Start of analysis window
- `window_end`: datetime - End of analysis window

**Relationships:**
- **With Existing:** Enhances current 82-feature engineering with velocity-specific features
- **With New:** Correlates with AML model for comprehensive fraud assessment

#### Enhanced Transaction Response Model

**Purpose:** Extend existing API response with new AML and velocity information
**Integration:** Backwards-compatible extension of current prediction response schema

**Key Attributes:**
- `fraud_probability`: float - Existing fraud prediction (maintains compatibility)
- `risk_category`: str - Existing risk classification (maintains compatibility)
- `aml_compliance`: AMLComplianceModel - New AML analysis results
- `velocity_analysis`: VelocityCheckModel - New velocity assessment
- `comprehensive_risk_score`: float - Combined fraud + AML + velocity score
- `recommended_action`: str - APPROVE, REVIEW, DECLINE based on all factors

### Schema Integration Strategy

**Database Changes Required:**
- **New Model Artifacts:** 
  - `models/aml_classifier.pkl` - AML pattern detection model
  - `models/velocity_analyzer.pkl` - Velocity risk assessment model
  - `models/aml_metadata.json` - AML model configuration and thresholds
  - `models/velocity_metadata.json` - Velocity analysis parameters
- **Enhanced Metadata:** Extend existing `model_metadata.json` with new model references
- **New Configuration:** Add AML/velocity thresholds to existing environment variable pattern

**Backward Compatibility:**
- Existing API responses maintain current schema when AML/velocity features not requested
- New fields added as optional extensions to existing models
- Current pickle model loading preserved alongside new model artifacts
- Existing feature engineering pipeline enhanced, not replaced
