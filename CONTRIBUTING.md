# 🏗️ System Architecture - Credit Card Fraud Detection

## 📋 **Architecture Overview**

The Credit Card Fraud Detection System is deployed as a microservices architecture on Railway Cloud, with two separate services communicating via REST API.

---

## 🎯 **Live Production Architecture**

```
┌─────────────────────────────────────────────────────┐
│                   Internet Users                     │
└─────────────┬───────────────────┬───────────────────┘
              │                   │
              ▼                   ▼
┌──────────────────────┐  ┌──────────────────────────┐
│  Dashboard Service   │  │     API Service          │
│  fraud-dashboard     │  │     fraud-api            │
│  Port: 8080         │  │     Port: 8080           │
│  Streamlit UI       │──▶│     FastAPI Backend      │
└──────────────────────┘  └──────────┬───────────────┘
                                     │
                          ┌──────────▼───────────────┐
                          │    ML Models (4)         │
                          │  - Ensemble (95.6%)      │
                          │  - Random Forest         │
                          │  - Logistic Regression   │
                          │  - Isolation Forest      │
                          └──────────────────────────┘
```

### **Service URLs**
- **API**: https://fraud-api-production.up.railway.app
- **Dashboard**: https://fraud-dashboard-production.up.railway.app

---

## 🔄 **Data Flow Architecture**

### **Real-time Prediction Flow**
```
User Input (Dashboard) 
    ↓
HTTP POST Request
    ↓
FastAPI Router (/predict)
    ↓
Feature Validation (Pydantic)
    ↓
Feature Engineering (82 features)
    ↓
Model Ensemble Prediction
    ↓
Risk Classification
    ↓
JSON Response (89ms avg)
    ↓
Dashboard Display
```

### **Model Loading Flow**
```
Application Startup
    ↓
Load model_metadata.json
    ↓
Load 4 pickle files:
  - ensemble_model.pkl (Primary)
  - random_forest_model.pkl
  - logistic_regression_model.pkl
  - isolation_forest_model.pkl
    ↓
Models cached in memory
    ↓
Ready for predictions
```

---

## 🧠 **Machine Learning Pipeline**

### **Feature Engineering (82 Features)**
```
Transaction Input
├── Temporal Features (9)
│   ├── transaction_hour
│   ├── transaction_day
│   ├── transaction_weekend
│   └── is_business_hours
├── Velocity Features (12)
│   ├── card_txn_count_recent
│   └── time_since_last_txn
├── Amount Features (15)
│   ├── transaction_amount
│   ├── amount_zscore
│   └── is_amount_outlier
├── Risk Features (18)
│   ├── merchant_risk_score
│   └── card_amount_mean
├── Behavioral Features (20)
└── Interaction Features (8)
```

### **Ensemble Model Strategy**
```python
Ensemble Composition:
├── XGBoost (40% weight)
│   └── Best for: Complex non-linear patterns
├── Random Forest (30% weight)
│   └── Best for: Robust predictions
├── Logistic Regression (20% weight)
│   └── Best for: Linear relationships
└── Isolation Forest (10% weight)
    └── Best for: Anomaly detection

Final Prediction = Weighted Average (Soft Voting)
```

---

## 🌐 **API Architecture**

### **FastAPI Application Structure**
```
app/main.py
├── Application Setup
│   ├── FastAPI() initialization
│   ├── CORS middleware
│   └── Model loading on startup
├── Endpoints
│   ├── GET /              # Homepage
│   ├── GET /health        # Health check
│   ├── GET /model_info    # Model metadata
│   ├── GET /metrics       # Performance metrics
│   ├── POST /predict      # Single prediction
│   └── POST /batch_predict # Batch predictions
└── Model Management
    ├── ModelManager class
    ├── Prediction logic
    └── Error handling
```

### **Request/Response Cycle**
```
1. Request arrives at Railway load balancer
2. Routed to FastAPI application (Port 8080)
3. Pydantic validates input data
4. Features processed through pipeline
5. Model ensemble makes prediction
6. Response formatted as JSON
7. Returned to client (avg 89ms)
```

---

## 📊 **Dashboard Architecture**

### **Streamlit Application Structure**
```
dashboard/app.py
├── Configuration
│   ├── Page config
│   └── API connection (via API_URL env var)
├── Sidebar
│   ├── Navigation menu
│   ├── API status indicator
│   └── System info
├── Pages
│   ├── Overview (KPIs, metrics)
│   ├── Real-time Prediction
│   ├── Model Performance
│   └── System Status
└── API Integration
    ├── APIClient class
    ├── Connection management
    └── Real-time updates
```

### **Dashboard-API Communication**
```python
# Connection flow
API_URL = os.getenv('API_URL', 'http://localhost:8080')
    ↓
Check /health endpoint
    ↓
If successful: "✅ API Connected"
If failed: "❌ API Disconnected"
    ↓
Enable/disable features based on connection
```

---

## ☁️ **Deployment Architecture**

### **Railway Cloud Infrastructure**
```
Railway Platform
├── Project: divine-gentleness
├── Services (2)
│   ├── fraud-api
│   │   ├── Build: Docker container
│   │   ├── Start: python app/main.py
│   │   ├── Port: 8080
│   │   ├── Health check: /health
│   │   └── Domain: fraud-api-production.up.railway.app
│   └── fraud-dashboard
│       ├── Build: Docker container
│       ├── Start: streamlit run dashboard/app.py
│       ├── Port: 8080
│       ├── Env: API_URL=https://fraud-api-production.up.railway.app
│       └── Domain: fraud-dashboard-production.up.railway.app
└── Deployment
    ├── Trigger: Git push to main
    ├── Build time: ~3.5 minutes
    └── Zero-downtime deployment
```

---

## 🔒 **Security Architecture**

### **Current Implementation**
```
Security Layers:
├── Transport Layer
│   └── HTTPS/TLS encryption (Railway managed)
├── Application Layer
│   ├── Input validation (Pydantic)
│   ├── CORS configuration
│   └── Error sanitization
├── Data Layer
│   ├── No PII storage
│   └── Environment variables for secrets
└── Infrastructure Layer
    ├── Railway security
    └── Isolated services
```

---

## 📊 **Performance Architecture**

### **Optimization Strategies**
```
Performance Optimizations:
├── Model Loading
│   ├── Pre-load all models on startup
│   ├── Cache in memory
│   └── No reload during runtime
├── Feature Processing
│   ├── Vectorized operations (NumPy)
│   └── Pre-computed statistics
├── API Response
│   ├── Async FastAPI handlers
│   ├── JSON serialization optimization
│   └── Response compression
└── Infrastructure
    ├── Railway auto-scaling
    ├── CDN for static assets
    └── Geographic optimization (US West)
```

### **Performance Metrics**
```
Current Production Performance:
├── Response Time: 89ms average
├── Throughput: 1,000+ req/min
├── Uptime: 99%+
├── Model Load Time: 2.5s on startup
└── Memory Usage: ~600MB total
```

---

## 🔧 **Configuration Management**

### **Environment Variables**
```yaml
# fraud-api service
PORT: 8080  # Set by Railway
ENVIRONMENT: production

# fraud-dashboard service  
PORT: 8080  # Set by Railway
API_URL: https://fraud-api-production.up.railway.app
```

### **Model Configuration**
```json
// models/model_metadata.json
{
  "best_model": "ensemble",
  "models": {
    "ensemble": {
      "accuracy": 0.992,
      "threshold": 0.5
    }
  },
  "feature_count": 82
}
```

---

## 📈 **Monitoring & Observability**

### **Health Monitoring**
```
Monitoring Stack:
├── Health Checks
│   ├── /health endpoint (every 30s)
│   └── Railway monitoring
├── Metrics Collection
│   ├── /metrics endpoint
│   ├── Response times
│   └── Model performance
├── Logging
│   ├── Application logs (Railway)
│   └── Error tracking
└── Alerting
    └── Railway notifications
```

---

## 🔄 **Data Models**

### **Transaction Features Schema**
```python
class TransactionFeatures(BaseModel):
    # Required fields
    transaction_amount: float
    transaction_hour: int
    transaction_day: int
    transaction_weekend: int
    is_business_hours: int
    
    # Optional fields with defaults
    card_amount_mean: float = 0.0
    card_txn_count_recent: int = 1
    time_since_last_txn: float = 0.0
    merchant_risk_score: float = 0.1
    amount_zscore: float = 0.0
    is_amount_outlier: int = 0
```

### **Prediction Response Schema**
```python
class FraudPredictionResponse(BaseModel):
    is_fraud: bool
    fraud_probability: float
    risk_level: str  # "VERY_LOW", "LOW", "MEDIUM", "HIGH"
    model_used: str
    confidence: float
    prediction_timestamp: str
```

---

## 🚀 **Scaling Architecture**

### **Current Capacity**
- Single instance per service
- Handles 1,000+ requests/minute
- 89ms average response time

### **Scaling Strategy**
```
Horizontal Scaling Plan:
├── Short-term (Ready)
│   ├── Add Railway instances
│   └── Load balancer distribution
├── Medium-term (Planned)
│   ├── Redis caching layer
│   ├── Database for logging
│   └── CDN integration
└── Long-term (Future)
    ├── Kubernetes deployment
    ├── Multi-region setup
    └── GPU acceleration
```

---

<div align="center">

**🏗️ This architecture powers a production fraud detection system**

*Live at: https://fraud-api-production.up.railway.app*  
*Dashboard: https://fraud-dashboard-production.up.railway.app*  
*Performance: 92.3% fraud detection rate, 89ms response time*

</div>