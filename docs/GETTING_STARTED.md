# 🚀 Getting Started - Credit Card Fraud Detection System

[![Quick Start](https://img.shields.io/badge/Quick%20Start-Live%20System-brightgreen?style=for-the-badge)](https://fraud-dashboard-production.up.railway.app)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Try%20Now-blue?style=for-the-badge)](https://fraud-api-production.up.railway.app/docs)

> **Experience the live fraud detection system or set up your own development environment**

---

## ⚡ **Quick Demo (30 seconds)**

### **Try the Live System Right Now**
1. **📊 View Dashboard**: [fraud-dashboard-production.up.railway.app](https://fraud-dashboard-production.up.railway.app)
2. **🔍 Test API**: [Interactive API Docs](https://fraud-api-production.up.railway.app/docs)
3. **💗 Check Health**: [System Status](https://fraud-api-production.up.railway.app/health)

### **Quick API Test**
```bash
# Test fraud detection on a suspicious transaction
curl -X POST "https://fraud-api-production.up.railway.app/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_amount": 2500,
    "transaction_hour": 3,
    "transaction_weekend": 1,
    "is_business_hours": 0,
    "merchant_risk_score": 0.9,
    "amount_zscore": 4.2,
    "is_amount_outlier": 1
  }'

# Expected response: High fraud probability
```

---

## 🎯 **System Overview**

### **What's Currently Live**
- ✅ **API Service**: Fully operational at `fraud-api-production.up.railway.app`
- ✅ **Dashboard**: Connected and running at `fraud-dashboard-production.up.railway.app`
- ✅ **4 ML Models**: Ensemble, Random Forest, Logistic Regression, Isolation Forest
- ✅ **Performance**: 92.3% fraud detection rate, ~150ms response time
- ✅ **Features**: 82 engineered features for fraud detection

### **Key Metrics Achieved**
| Metric | Value | Status |
|--------|-------|--------|
| Detection Rate | 92.3% | ✅ Meets target |
| Response Time | 89ms | ✅ Under 100ms target |
| False Positives | 0.1% | ✅ Industry leading |
| Models Loaded | 4 | ✅ All models active |
| Test Coverage | 15/15 | ✅ 100% passing |

---

## 🛠️ **Local Development Setup**

### **Prerequisites**
- **Python**: 3.8+ (3.9 recommended)
- **Git**: For version control
- **RAM**: 4GB+ (8GB recommended for model training)
- **Storage**: 2GB free space

### **Quick Setup (5 minutes)**

#### **1. Clone Repository**
```bash
git clone https://github.com/DiazSk/credit-card-fraud-detection-system
cd credit-card-fraud-detection-system
```

#### **2. Create Virtual Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

#### **3. Install Dependencies**
```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
python -c "import fastapi, streamlit, xgboost; print('✅ All packages installed!')"
```

#### **4. Use Pre-trained Models**
The repository includes pre-trained models in the `models/` directory:
- `ensemble_model.pkl` - Main production model
- `random_forest_model.pkl` 
- `logistic_regression_model.pkl`
- `isolation_forest_model.pkl`
- `model_metadata.json` - Performance metrics

#### **5. Test the System**
```bash
# Test the complete pipeline
python tests/test_complete_pipeline.py

# Expected output:
# ✅ All tests passed! (15/15)
# 📊 Dataset: 10,000 transactions with 82 features  
# 🎯 Fraud rate: 0.17%
# 🎯 Ready for API deployment!
```

---

## 🚀 **Running the System Locally**

### **Start API Server**
```bash
# Start the API
python app/main.py

# Expected output:
# 🚀 Starting server on port 8080
# ✅ Loaded model metadata from models/model_metadata.json
# 📊 Found 4 models: ['isolation_forest', 'random_forest', 'logistic_regression', 'ensemble']
# INFO: Uvicorn running on http://0.0.0.0:8080
```

### **Start Dashboard (New Terminal)**
```bash
# Set API URL for local development
export API_URL=http://localhost:8080  # On Windows: set API_URL=http://localhost:8080

# Start dashboard
streamlit run dashboard/app.py

# Expected output:
# 🔗 Dashboard connecting to API: http://localhost:8080
# You can now view your Streamlit app in your browser.
# Local URL: http://localhost:8501
```

### **Access Your Local System**
- **🏠 API Homepage**: http://localhost:8080
- **📖 API Documentation**: http://localhost:8080/docs  
- **📊 Dashboard**: http://localhost:8501
- **💗 Health Check**: http://localhost:8080/health

---

## 🧪 **Testing Your Setup**

### **API Testing**
```bash
# Test health endpoint
curl http://localhost:8080/health

# Expected response:
{
  "status": "healthy",
  "models_loaded": true,
  "available_models": ["ensemble", "random_forest", "logistic_regression", "isolation_forest"]
}

# Test fraud prediction
curl -X POST "http://localhost:8080/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_amount": 156.78,
    "transaction_hour": 14,
    "transaction_day": 15,
    "transaction_weekend": 0,
    "is_business_hours": 1
  }'
```

### **Dashboard Testing**
1. **Open Dashboard**: http://localhost:8501
2. **Check API Connection**: Sidebar shows "✅ API Connected"
3. **View API URL**: Shows connection to your local API
4. **Test Prediction**: Use the Real-time Prediction page

---

## 📊 **Understanding the System**

### **Architecture Overview**
```
┌─────────────────┐     ┌─────────────────┐
│   Dashboard     │────▶│   FastAPI       │
│  (Streamlit)    │     │   Backend       │
└─────────────────┘     └─────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │   ML Models         │
                    │  - Ensemble         │
                    │  - Random Forest    │
                    │  - Logistic Reg.    │
                    │  - Isolation Forest │
                    └─────────────────────┘
```

### **Key Components**

#### **1. API Backend (FastAPI)**
- Serves predictions via REST API
- Loads and manages ML models
- Provides health monitoring
- Auto-generates documentation

#### **2. Dashboard (Streamlit)**
- Real-time fraud detection interface
- Model performance visualization
- System status monitoring
- Connected to API via environment variable

#### **3. ML Models**
- **Ensemble**: Combination of all models (95.6% F1-score)
- **Random Forest**: Tree-based classifier (98.7% accuracy)
- **Logistic Regression**: Linear model (96.8% accuracy)
- **Isolation Forest**: Anomaly detection (94.3% accuracy)

---

## 🎯 **Common Use Cases**

### **1. Testing Fraud Detection**
```python
import requests

# Test with normal transaction
normal_transaction = {
    "transaction_amount": 50.0,
    "transaction_hour": 14,
    "merchant_risk_score": 0.1
}

response = requests.post(
    "https://fraud-api-production.up.railway.app/predict",
    json=normal_transaction
)
print(response.json())
# Expected: Low fraud probability

# Test with suspicious transaction
suspicious_transaction = {
    "transaction_amount": 5000.0,
    "transaction_hour": 3,
    "merchant_risk_score": 0.9,
    "amount_zscore": 5.0
}

response = requests.post(
    "https://fraud-api-production.up.railway.app/predict",
    json=suspicious_transaction
)
print(response.json())
# Expected: High fraud probability
```

### **2. Batch Processing**
```python
# Process multiple transactions
batch_request = {
    "transactions": [
        {"transaction_amount": 100, "transaction_hour": 10},
        {"transaction_amount": 5000, "transaction_hour": 3},
        {"transaction_amount": 75, "transaction_hour": 15}
    ]
}

response = requests.post(
    "https://fraud-api-production.up.railway.app/batch_predict",
    json=batch_request
)
results = response.json()
print(f"Fraud detected in {results['summary']['fraud_detected']} transactions")
```

---

## 🔧 **Configuration Guide**

### **Environment Variables**

#### **For Local Development**
```bash
# .env file
ENVIRONMENT=development
API_URL=http://localhost:8080
PORT=8080
```

#### **For Production (Railway)**
```bash
# API Service
PORT=8080  # Set by Railway
ENVIRONMENT=production
SERVICE_TYPE=api

# Dashboard Service
PORT=8080  # Set by Railway
API_URL=https://fraud-api-production.up.railway.app
SERVICE_TYPE=dashboard
```

---

## 🚂 **Deploying Your Own Instance**

### **Deploy to Railway**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Create new project
railway init

# Deploy API
railway up

# Add dashboard service
railway add
# Choose: Empty Service
# Name: dashboard

# Set environment variable
API_URL=https://your-api-url.railway.app

# Deploy dashboard
railway up
```

---

## 🆘 **Troubleshooting**

### **Common Issues and Solutions**

#### **Issue: Models Not Loading**
```bash
# Check models directory
ls -la models/

# Should see:
# ensemble_model.pkl
# random_forest_model.pkl
# logistic_regression_model.pkl
# isolation_forest_model.pkl
# model_metadata.json
```

#### **Issue: Dashboard Can't Connect to API**
```bash
# Check API_URL environment variable
echo $API_URL

# For local development, should be:
# http://localhost:8080

# For production, should be:
# https://fraud-api-production.up.railway.app
```

#### **Issue: Port Already in Use**
```bash
# Change port for API
python app/main.py --port 8081

# Or kill existing process
# On Mac/Linux:
lsof -i :8080
kill -9 <PID>

# On Windows:
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

---

## 📚 **Learning Resources**

### **Project Documentation**
- [README.md](README.md) - Project overview and features
- [API.md](API.md) - Complete API documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design details
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guide

### **Key Technologies**
- **FastAPI**: Modern Python web framework for APIs
- **Streamlit**: Python framework for data apps
- **scikit-learn**: Machine learning library
- **XGBoost**: Gradient boosting framework
- **Railway**: Cloud deployment platform

---

## 🎉 **Next Steps**

### **Explore the Live System**
1. Visit the [Dashboard](https://fraud-dashboard-production.up.railway.app)
2. Try the [Interactive API Docs](https://fraud-api-production.up.railway.app/docs)
3. Test different transaction scenarios

### **Extend the System**
1. Add new features to the feature engineering pipeline
2. Implement additional ML models
3. Create custom visualizations in the dashboard
4. Add authentication and user management

### **Deploy Your Own Version**
1. Fork the repository
2. Modify as needed
3. Deploy to Railway or another platform
4. Share your improvements!

---

## 📞 **Getting Help**

### **Resources**
- **GitHub Issues**: Report bugs or ask questions
- **API Documentation**: https://fraud-api-production.up.railway.app/docs
- **Email**: zaid07sk@gmail.com
- **LinkedIn**: [zaidshaikhscientist](https://linkedin.com/in/zaidshaikhscientist)

---

<div align="center">

**🎯 Ready to Detect Fraud?**

*The system is live and ready for you to explore!*

**🚀 Start with the [live dashboard](https://fraud-dashboard-production.up.railway.app) or dive into the code!**

</div>

*Last Updated: August 18, 2025*