# AML Compliance Documentation

## Overview

The Credit Card Fraud Detection System now includes comprehensive Anti-Money Laundering (AML) compliance features designed to detect suspicious activities and ensure regulatory compliance. This document outlines the AML features, their implementation, and usage.

## Features

### 1. Structuring Detection

**Purpose**: Identify transactions designed to avoid Currency Transaction Report (CTR) thresholds.

**Implementation**:
- Monitors transactions near the $10,000 CTR threshold
- Analyzes patterns of multiple transactions within 24-hour windows
- Flags transactions between 80% and 100% of reporting thresholds

**Risk Factors**:
- Single transactions between $8,000 - $9,999
- Multiple transactions totaling above $10,000 in 24 hours
- Pattern of consistent amounts just below thresholds

### 2. Rapid Movement of Funds

**Purpose**: Detect suspicious rapid movement of large amounts of money.

**Implementation**:
- Monitors large single transactions (>$50,000)
- Analyzes transaction velocity within 6-hour windows
- Identifies round-number transactions (potential money laundering indicators)

**Risk Factors**:
- Transactions above $50,000
- High frequency transactions (5+ in 6 hours)
- Round amounts (e.g., $10,000, $25,000, $50,000)

### 3. Suspicious Pattern Detection

**Purpose**: Identify unusual transaction patterns and behaviors.

**Implementation**:
- Analyzes timing patterns (unusual hours)
- Monitors high-risk merchant categories
- Evaluates geographic risk factors
- Detects suspicious amount patterns

**Risk Factors**:
- Transactions outside business hours (before 6 AM or after 10 PM)
- High-risk merchant categories (gambling, cryptocurrency, cash advances)
- High-risk geographic locations
- Repeated digit patterns in amounts (e.g., $5,555, $7,777)

### 4. Sanctions Screening

**Purpose**: Screen against sanctions lists and Politically Exposed Persons (PEP) databases.

**Implementation**:
- Real-time screening of customer and merchant names
- Geographic sanctions checking
- Configurable sanctions lists

**Risk Factors**:
- Name matches against sanctions lists
- Transactions from sanctioned countries/regions
- PEP involvement (when implemented)

## API Integration

### Endpoints

#### POST /predict
Enhanced fraud prediction with integrated AML assessment.

**Request**:
```json
{
    "transaction_amount": 15000,
    "transaction_hour": 23,
    "merchant_category": "CASH_ADVANCE",
    "location": "OFFSHORE",
    "customer_name": "John Doe",
    "merchant_name": "ABC Exchange"
}
```

**Response**:
```json
{
    "is_fraud": true,
    "fraud_probability": 0.75,
    "aml_risk_score": 0.65,
    "combined_risk_score": 0.72,
    "risk_level": "HIGH",
    "aml_risk_level": "MEDIUM",
    "aml_flags": ["LARGE_SINGLE_TRANSACTION", "UNUSUAL_TIMING"],
    "requires_manual_review": true,
    "model_used": "ensemble",
    "confidence": 0.44,
    "prediction_timestamp": "2025-09-07T10:30:00"
}
```

#### POST /aml_check
Dedicated AML compliance assessment endpoint.

**Request**:
```json
{
    "transaction_id": "TXN_20250907_001",
    "transaction_amount": 9500,
    "customer_name": "Jane Smith",
    "merchant_name": "Cash Plus",
    "location": "DOMESTIC",
    "merchant_category": "CASH_ADVANCE"
}
```

**Response**:
```json
{
    "transaction_id": "TXN_20250907_001",
    "aml_assessment": {
        "aml_overall_risk_score": 0.4,
        "aml_risk_level": "MEDIUM",
        "aml_flags": ["AMOUNT_NEAR_CTR_THRESHOLD", "HIGH_RISK_MERCHANT_CATEGORY"],
        "aml_recommendations": ["ENHANCED_DUE_DILIGENCE", "ADDITIONAL_DOCUMENTATION_REQUIRED"],
        "aml_component_scores": {
            "structuring": 0.4,
            "rapid_movement": 0.3,
            "suspicious_patterns": 0.5,
            "sanctions": 0.0
        },
        "requires_manual_review": false
    },
    "assessment_timestamp": "2025-09-07T10:30:00",
    "compliance_status": "REVIEW_REQUIRED"
}
```

## Configuration

### AML Thresholds

The system uses configurable thresholds that can be updated as regulations change:

```python
{
    "risk_thresholds": {
        "structuring_threshold": 10000,      # CTR threshold
        "rapid_movement_threshold": 50000,   # Large transaction flag
        "velocity_threshold": 100000,        # Daily velocity limit
        "suspicious_pattern_threshold": 25000 # Pattern detection threshold
    },
    "time_windows": {
        "structuring_window_hours": 24,      # Structuring detection window
        "rapid_movement_window_hours": 6,    # Rapid movement window
        "velocity_window_hours": 24          # Velocity calculation window
    }
}
```

### High-Risk Categories

- CASH_ADVANCE
- GAMBLING
- CRYPTOCURRENCY
- MONEY_TRANSFER

### Risk Levels

- **MINIMAL** (0.0 - 0.29): Standard processing
- **LOW** (0.3 - 0.49): Standard processing with monitoring
- **MEDIUM** (0.5 - 0.79): Enhanced due diligence recommended
- **HIGH** (0.8 - 1.0): Manual review required

## Dashboard Integration

The dashboard includes a dedicated AML Compliance page with:

- Real-time AML risk assessment tools
- Interactive transaction testing
- AML analytics and trends
- Configuration management
- Compliance reporting tools

### Key Features:

1. **Test AML Compliance**: Interactive form to test AML rules
2. **Risk Distribution**: Visual analytics of AML risk levels
3. **Flags Trend**: Historical view of AML flag patterns
4. **Configuration View**: Current AML thresholds and rules
5. **Compliance Reports**: Generate daily/weekly reports

## Implementation Details

### Feature Engineering Integration

AML features are automatically added to the feature engineering pipeline:

- `aml_risk_score`: Overall AML risk score
- `aml_flags_count`: Number of AML flags triggered
- `requires_manual_review`: Binary flag for manual review requirement
- `structuring_risk`: Structuring component risk score
- `rapid_movement_risk`: Rapid movement component risk score
- `suspicious_patterns_risk`: Suspicious patterns component risk score
- `sanctions_risk`: Sanctions screening risk score

### Error Handling

The system includes robust error handling:
- Fallback values when AML checker fails
- Graceful degradation if AML module is unavailable
- Comprehensive logging of AML assessment failures

## Compliance and Regulatory Considerations

### Important Notes:

1. **Regulatory Compliance**: This implementation provides a framework for AML compliance but should be reviewed by compliance professionals before production use.

2. **Sanctions Lists**: The current implementation uses simplified sanctions lists. Production systems should integrate with official OFAC and other regulatory sanctions databases.

3. **Reporting**: The system provides foundations for SAR (Suspicious Activity Report) generation but requires manual review and completion by qualified compliance officers.

4. **Data Retention**: Consider implementing appropriate data retention policies for AML-related data as required by regulations.

5. **Audit Trail**: All AML assessments are logged with timestamps for audit purposes.

## Future Enhancements

1. **Real-time Sanctions Integration**: Connect to live OFAC and other sanctions databases
2. **PEP Database Integration**: Add Politically Exposed Persons screening
3. **Advanced Pattern Recognition**: Machine learning-based pattern detection
4. **Automated Reporting**: Enhanced SAR generation and filing capabilities
5. **Geographic Risk Scoring**: Advanced country/region risk assessment
6. **Customer Risk Profiling**: Historical customer behavior analysis

## Usage Examples

### Basic AML Check

```python
from src.aml_compliance import AMLComplianceChecker

aml_checker = AMLComplianceChecker()
transaction_data = {
    "transaction_amount": 9800,
    "customer_name": "John Doe",
    "merchant_category": "CASH_ADVANCE"
}

result = aml_checker.calculate_overall_aml_risk(transaction_data)
print(f"AML Risk Score: {result['aml_overall_risk_score']}")
print(f"Risk Level: {result['aml_risk_level']}")
print(f"Flags: {result['aml_flags']}")
```

### Custom Configuration

```python
import json

# Create custom AML configuration
custom_config = {
    "risk_thresholds": {
        "structuring_threshold": 8000,  # Lower threshold for stricter compliance
        "rapid_movement_threshold": 40000
    }
}

# Save configuration
with open('custom_aml_config.json', 'w') as f:
    json.dump(custom_config, f)

# Initialize checker with custom config
aml_checker = AMLComplianceChecker(config_path='custom_aml_config.json')
```

## Testing

The AML compliance features include comprehensive testing:

1. **Unit Tests**: Test individual AML check functions
2. **Integration Tests**: Test API endpoints with AML features
3. **Dashboard Tests**: Test interactive AML compliance tools
4. **Performance Tests**: Ensure AML checks don't impact system performance

Run AML-specific tests:
```bash
python -m pytest tests/test_aml_compliance.py -v
```

## Monitoring and Alerts

### Key Metrics to Monitor:

- AML assessment response times
- False positive rates for AML flags
- Manual review queue sizes
- Sanctions screening match rates
- System availability for AML checks

### Recommended Alerts:

- High volume of HIGH risk AML scores
- Sanctions screening system failures
- AML assessment timeouts
- Unusual patterns in AML flag distributions

---

*This documentation should be reviewed by qualified compliance professionals before production deployment.*
