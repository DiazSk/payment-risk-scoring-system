# 🏗️ System Architecture - Credit Card Fraud Detection

## 📋 **Architecture Overview**

The Credit Card Fraud Detection System follows a **microservices architecture** with clear separation of concerns, enabling scalability, maintainability, and independent deployment of components.

---

## 🎯 **High-Level Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Browser   │    │   Mobile App    │    │  External API   │
│    Dashboard    │    │    Client       │    │   Integration   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼──────────────┐
                    │      Railway Cloud         │
                    │     Load Balancer          │
                    └─────────────┬──────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                       │                        │
┌───────▼────────┐    ┌─────────▼─────────┐    ┌─────────▼─────────┐
│   Streamlit    │    │     FastAPI       │    │    Monitoring     │
│   Dashboard    │    │       API         │    │     Service       │
│   (Frontend)   │    │    (Backend)      │    │   (Observability) │
└───────┬────────┘    └─────────┬─────────┘    └─────────┬─────────┘
        │                       │                        │
        │              ┌────────▼─────────┐              │
        │              │   Model Manager  │              │
        │              │   (ML Engine)    │              │
        │              └────────┬─────────┘              │
        │                       │                        │
        └───────────────────────┼────────────────────────┘
                                │
                   ┌────────────▼─────────────┐
                   │     Model Storage        │
                   │   (Pickle Files +        │
                   │    Metadata JSON)        │
                   └──────────────────────────┘
```

---

## 🔄 **Data Flow Architecture**

### **1. Real-time Prediction Flow**
```
Transaction Input → Feature Engineering → Model Ensemble → Risk Scoring → Response
       ↓                    ↓                   ↓              ↓           ↓
   [Raw Data]         [82 Features]      [ML Algorithms]  [Probability]  [JSON]
   JSON Request       NumPy Arrays       XGB+RF+LR        0.0 - 1.0      API Response
```

### **2. Batch Processing Flow**
```
Multiple Transactions → Vectorized Processing → Parallel Predictions → Aggregated Results
         ↓                       ↓                       ↓                    ↓
    [JSON Array]           [Feature Matrix]         [Batch Inference]    [Summary Stats]
    1-1000 requests        N×82 DataFrame          Async Processing      Fraud Rate, etc.
```

### **3. Model Training Flow**
```
Raw Data → Data Cleaning → Feature Engineering → Model Training → Evaluation → Deployment
    ↓           ↓               ↓                    ↓              ↓           ↓
[280K rows] [Clean Data]   [82 Features]      [5 Algorithms]  [Performance] [Production]
CSV Files   Processed DF   Engineered DF     Cross-validation  Metrics      Model Files
```

---

## 🧠 **Machine Learning Pipeline**

### **Feature Engineering Architecture**

```python
Input Transaction
├── Temporal Features (9)
│   ├── transaction_hour
│   ├── transaction_day_of_week  
│   ├── is_weekend
│   └── is_business_hours
├── Velocity Features (12)
│   ├── txn_count_last_hour
│   ├── txn_count_last_day
│   ├── avg_amount_last_week
│   └── time_since_last_txn
├── Amount Features (15)
│   ├── amount_zscore
│   ├── amount_percentile
│   ├── is_amount_outlier
│   └── amount_category
├── Risk Features (18)
│   ├── merchant_risk_score
│   ├── user_risk_profile
│   ├── location_risk
│   └── device_fingerprint
├── Behavioral Features (20)
│   ├── spending_pattern_score
│   ├── frequency_deviation
│   ├── merchant_diversity
│   └── transaction_regularity
└── Interaction Features (8)
    ├── amount_hour_interaction
    ├── risk_velocity_product
    └── pattern_anomaly_score
```

### **Model Ensemble Strategy**

```python
Ensemble Architecture:
├── Base Learners
│   ├── XGBoost Classifier (40% weight)
│   │   ├── n_estimators: 200
│   │   ├── max_depth: 6
│   │   └── learning_rate: 0.1
│   ├── Random Forest (30% weight)
│   │   ├── n_estimators: 100
│   │   ├── max_depth: 10
│   │   └── min_samples_split: 5
│   └── Logistic Regression (30% weight)
│       ├── C: 1.0
│       ├── penalty: 'l2'
│       └── solver: 'liblinear'
├── Meta-Learner
│   └── Voting Classifier (soft voting)
└── Anomaly Detector
    └── Isolation Forest (ensemble validation)
```

---

## 🌐 **API Architecture**

### **FastAPI Application Structure**

```python
FastAPI App
├── Middleware Layer
│   ├── CORS Middleware
│   ├── Trusted Host Middleware
│   └── Custom Exception Handlers
├── Route Handlers
│   ├── Health Endpoints (/health, /healthz)
│   ├── Prediction Endpoints (/predict, /batch_predict)
│   ├── Information Endpoints (/model_info, /metrics)
│   └── Documentation (/docs, /redoc)
├── Model Management
│   ├── Model Loading & Caching
│   ├── Prediction Logic
│   ├── Performance Tracking
│   └── Error Handling
└── Data Validation
    ├── Pydantic Models
    ├── Input Validation
    ├── Type Safety
    └── Response Formatting
```

### **Request/Response Cycle**

```
Client Request → FastAPI Router → Middleware Chain → Route Handler
      ↓                                                      ↓
JSON Validation ← Pydantic Models ← Data Processing ← Model Manager
      ↓                                                      ↓
Response JSON ← Error Handling ← Prediction Logic ← Model Inference
```

---

## 📊 **Dashboard Architecture**

### **Streamlit Application Structure**

```python
Streamlit Dashboard
├── Main Application (app.py)
│   ├── Page Router
│   ├── API Client Manager
│   ├── State Management
│   └── UI Rendering
├── Component Library (components.py)
│   ├── Metric Cards
│   ├── Chart Generators
│   ├── Data Tables
│   └── Status Indicators
├── Pages
│   ├── Overview (KPIs, business metrics)
│   ├── Real-time Prediction (transaction testing)
│   ├── Model Performance (algorithm comparison)
│   ├── Analytics (fraud trends, insights)
│   └── System Status (health monitoring)
└── API Integration
    ├── Connection Management
    ├── Error Handling
    ├── Data Caching
    └── Real-time Updates
```

---

## ☁️ **Deployment Architecture**

### **Railway Cloud Infrastructure**

```
Internet Traffic
       ↓
Railway Edge Network (CDN)
       ↓
Load Balancer (Automatic)
       ↓
┌─────────────────┬─────────────────┐
│   API Service   │ Dashboard Service│
│   (Port 8080)   │   (Port 8080)    │
└─────────────────┴─────────────────┘
       ↓                     ↓
Railway Container Runtime (Docker)
       ↓                     ↓
┌─────────────────┬─────────────────┐
│   FastAPI App   │  Streamlit App  │
│   + ML Models   │  + Components   │
└─────────────────┴─────────────────┘
```

### **Scaling Strategy**

```python
Horizontal Scaling:
├── API Service
│   ├── Stateless design (scales easily)
│   ├── Model caching (shared across instances)
│   └── Load balancer distribution
├── Dashboard Service  
│   ├── Read-only operations (cacheable)
│   ├── API consumption (no state)
│   └── CDN optimization
└── Database Layer (Future)
    ├── Read replicas for analytics
    ├── Write optimization for logging
    └── Connection pooling
```

---

## 🔒 **Security Architecture**

### **API Security**
- **HTTPS Encryption**: All communication encrypted in transit
- **CORS Configuration**: Controlled cross-origin access
- **Rate Limiting**: Protection against abuse (1000 req/min)
- **Input Validation**: Pydantic model validation
- **Error Sanitization**: No sensitive data in error responses

### **Data Security**
- **No PII Storage**: Only aggregate transaction features
- **Model Protection**: Serialized models with integrity checks
- **Environment Isolation**: Separate dev/staging/production
- **Audit Logging**: Request/response tracking for compliance

---

## 📊 **Performance Architecture**

### **Optimization Strategies**

```python
Performance Optimizations:
├── API Level
│   ├── Async FastAPI (non-blocking I/O)
│   ├── Pydantic validation (compiled C)
│   ├── Model caching (in-memory)
│   └── Connection pooling
├── ML Level
│   ├── Vectorized operations (NumPy)
│   ├── Optimized algorithms (XGBoost)
│   ├── Feature pre-computation
│   └── Batch prediction support
├── Infrastructure Level
│   ├── Container optimization
│   ├── Memory management
│   ├── CPU utilization
│   └── Network optimization
└── Monitoring Level
    ├── Performance metrics
    ├── Resource tracking
    ├── Bottleneck identification
    └── Auto-scaling triggers
```

---

## 🔧 **Configuration Management**

### **Environment-based Configuration**

```python
Configuration Hierarchy:
├── Default Settings (config.py)
├── Environment Variables (Railway)
├── Runtime Parameters (API)
└── Feature Flags (Dashboard)

Production Environment:
├── ENVIRONMENT=production
├── API_URL=https://credit-card-fraud-api.up.railway.app
├── STREAMLIT_SERVER_HEADLESS=true
├── MODEL_CACHE_TTL=3600
└── LOG_LEVEL=INFO
```

---

## 📈 **Monitoring & Observability**

### **Key Metrics Tracked**

```python
System Metrics:
├── Application Performance
│   ├── Response time (p50, p95, p99)
│   ├── Throughput (requests/second)
│   ├── Error rate (4xx, 5xx responses)
│   └── Uptime percentage
├── Model Performance  
│   ├── Prediction accuracy
│   ├── Fraud detection rate
│   ├── False positive rate
│   └── Model confidence scores
├── Business Metrics
│   ├── Fraud prevented ($)
│   ├── False alarms (count)
│   ├── Customer impact
│   └── ROI calculation
└── Infrastructure Metrics
    ├── CPU utilization
    ├── Memory usage
    ├── Network I/O
    └── Container health
```

---

## 🔄 **Disaster Recovery**

### **Resilience Strategy**
- **Health Checks**: Automatic service health monitoring
- **Graceful Degradation**: System continues with reduced functionality
- **Model Fallbacks**: Multiple model availability for redundancy
- **Auto-restart**: Container recovery on failures
- **Backup Strategy**: Model versioning and rollback capabilities

---

*This architecture supports enterprise-scale fraud detection with 99%+ uptime and sub-100ms response times.*