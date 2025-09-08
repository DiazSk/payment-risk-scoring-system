# 🚀 Render.com & Vercel Deployment Guide

[![Render Deploy](https://img.shields.io/badge/Deploy%20to-Render-brightgreen?style=for-the-badge&logo=render)](https://render.com/deploy)
[![Vercel Deploy](https://img.shields.io/badge/Deploy%20to-Vercel-black?style=for-the-badge&logo=vercel)](https://vercel.com/import/project)

> **Complete guide for deploying the Fraud Detection System on Render.com (API) and Vercel (Dashboard)**

---

## 📋 **Deployment Overview**

### **Architecture**
- **🔧 API Backend**: Render.com (Free tier - 750 hours/month)
- **📊 Dashboard**: Vercel (Free tier - unlimited static sites)
- **🔗 Integration**: Dashboard connects to Render API via HTTPS

### **Benefits**
- ✅ **Cost**: Both platforms offer generous free tiers
- ✅ **Performance**: Global CDN and fast cold starts
- ✅ **Reliability**: Built-in health monitoring and auto-recovery
- ✅ **Simplicity**: Git-based deployment with automatic builds

---

## 🔧 **Part 1: Deploy API to Render.com**

### **Step 1: Prepare Repository**
```bash
# Ensure you have the render.yaml file in your repo root
git add render.yaml
git commit -m "Add Render deployment configuration"
git push origin main
```

### **Step 2: Deploy to Render**

#### **Option A: Deploy via render.yaml (Recommended)**
1. **Visit**: [render.com/deploy](https://render.com/deploy)
2. **Connect Repository**: Link your GitHub repo
3. **Auto-detection**: Render will find and use `render.yaml`
4. **Deploy**: Click "Apply" to deploy both services

#### **Option B: Manual Setup**
1. **Create New Web Service**:
   - Go to [dashboard.render.com](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure API Service**:
   ```
   Name: fraud-api
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python app/main.py
   ```

3. **Environment Variables**:
   ```
   PORT=10000
   HOST=0.0.0.0
   ENVIRONMENT=production
   ```

### **Step 3: Verify API Deployment**
```bash
# Check health endpoint
curl https://fraud-api.onrender.com/health

# Test prediction endpoint
curl -X POST "https://fraud-api.onrender.com/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_amount": 500,
    "transaction_hour": 23,
    "merchant_risk_score": 0.8,
    "customer_id": "TEST_001"
  }'
```

---

## 📊 **Part 2: Deploy Dashboard to Vercel**

### **Step 1: Install Vercel CLI**
```bash
# Install Vercel CLI
npm install -g vercel

# Or use yarn
yarn global add vercel
```

### **Step 2: Login to Vercel**
```bash
vercel login
```

### **Step 3: Deploy Dashboard**

#### **Option A: CLI Deployment**
```bash
# Navigate to project root
cd payment-risk-scoring-system

# Deploy to Vercel
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? (your username)
# - Link to existing project? No
# - Project name: fraud-detection-dashboard
# - Directory: ./
```

#### **Option B: GitHub Integration**
1. **Import Project**:
   - Go to [vercel.com/import](https://vercel.com/import)
   - Click "Import Git Repository"
   - Select your repository

2. **Configure Build Settings**:
   ```
   Framework Preset: Other
   Root Directory: ./
   Build Command: pip install -r requirements.txt
   Output Directory: (leave empty)
   Install Command: pip install -r requirements.txt
   ```

3. **Environment Variables**:
   ```
   API_URL=https://fraud-api.onrender.com
   STREAMLIT_SERVER_HEADLESS=true
   STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
   ```

### **Step 4: Recommended Dashboard Deployment - Streamlit Cloud**

Since Streamlit apps work best on platforms designed for them, **Streamlit Cloud** is the recommended option:

1. **Streamlit Cloud Deployment** (Recommended):
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "Deploy an app"
   - Connect GitHub and select repo
   - Set main file path: `dashboard/app.py`
   - Uses `dashboard/requirements.txt` automatically

2. **Environment Variables**:
   ```
   API_URL=https://fraud-api.onrender.com
   ```

### **Alternative: Render for Dashboard**

You can also deploy the dashboard to Render alongside the API:

1. **Add Dashboard Service** to `render.yaml`:
   ```yaml
   - type: web
     name: fraud-dashboard
     runtime: python
     buildCommand: "pip install -r dashboard/requirements.txt"
     startCommand: "streamlit run dashboard/app.py --server.port $PORT --server.address 0.0.0.0"
     envVars:
       - key: PORT
         value: 10000
       - key: API_URL
         value: https://fraud-api.onrender.com
   ```

### **Vercel Limitations for Streamlit**

⚠️ **Note**: Vercel is optimized for static sites and serverless functions, not long-running Streamlit applications. While the `vercel.json` configuration is provided, **Streamlit Cloud or Render are better choices** for the dashboard.

---

## 🔗 **Part 3: Connect Dashboard to API**

### **Dashboard Already Configured**
The dashboard is already configured to read the API URL from environment variables:

```python
# In dashboard/app.py
self.api_base_url = os.getenv("API_URL", "http://localhost:8080").rstrip('/')
```

### **Environment Variables Setup**
Make sure to set these environment variables in your deployment platform:

**For Streamlit Cloud:**
```
API_URL=https://fraud-api.onrender.com
```

**For Vercel:**
```
API_URL=https://fraud-api.onrender.com
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

---

## 🧪 **Part 4: Testing Your Deployment**

### **Test API Endpoints**
```bash
# Health check
curl https://fraud-api.onrender.com/health

# API documentation
curl https://fraud-api.onrender.com/docs

# Prediction test
curl -X POST "https://fraud-api.onrender.com/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_amount": 1500.0,
    "transaction_hour": 2,
    "transaction_day": 15,
    "transaction_weekend": 0,
    "is_business_hours": 0,
    "card_amount_mean": 156.78,
    "card_txn_count_recent": 12,
    "time_since_last_txn": 7200.0,
    "merchant_risk_score": 0.65,
    "amount_zscore": 2.8,
    "is_amount_outlier": 1,
    "customer_id": "TEST_001"
  }'

# AML compliance check
curl -X POST "https://fraud-api.onrender.com/aml_check" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 9500,
    "customer_id": "TEST_001"
  }'

# Velocity monitoring
curl -X POST "https://fraud-api.onrender.com/velocity_check" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "TEST_001",
    "amount": 1000
  }'
```

### **Test Dashboard Connection**
1. **Open Dashboard**: Visit your Vercel/Streamlit Cloud URL
2. **Check API Status**: Should show "API Connected" in green
3. **Test Prediction**: Use the prediction form to test the connection
4. **Monitor Metrics**: Verify real-time data is updating

---

## 📊 **Part 5: Monitoring & Maintenance**

### **Render.com Monitoring**
- **Logs**: View in Render dashboard under "Logs" tab
- **Metrics**: CPU, memory usage available in dashboard
- **Health Checks**: Automatic health monitoring on `/health` endpoint
- **Alerts**: Set up email alerts for service failures

### **Vercel Monitoring**
- **Analytics**: Built-in performance monitoring
- **Function Logs**: Available in Vercel dashboard
- **Error Tracking**: Automatic error collection and reporting

### **Custom Monitoring Script**
```python
# monitor_deployment.py
import requests
import time
from datetime import datetime

def check_api_health():
    try:
        response = requests.get('https://fraud-api.onrender.com/health', timeout=10)
        return response.status_code == 200
    except:
        return False

def check_dashboard():
    try:
        response = requests.get('https://your-dashboard.vercel.app', timeout=10)
        return response.status_code == 200
    except:
        return False

# Run monitoring
if __name__ == "__main__":
    print(f"[{datetime.now()}] API Health: {check_api_health()}")
    print(f"[{datetime.now()}] Dashboard: {check_dashboard()}")
```

---

## 🔧 **Part 6: Troubleshooting**

### **Common Render Issues**

**❌ Build Fails**
```bash
# Solution: Check requirements.txt has all dependencies
pip freeze > requirements.txt
git add requirements.txt && git commit -m "Update requirements" && git push
```

**❌ App Crashes on Startup**
- Check logs in Render dashboard
- Ensure PORT environment variable is set to 10000
- Verify `python app/main.py` command works locally

**❌ Health Check Fails**
- Ensure `/health` endpoint exists in your API
- Check if app is binding to correct host and port

### **Common Vercel Issues**

**❌ Build Timeout**
- Vercel has 5-minute build limit for free tier
- Consider pre-building dependencies or using Docker

**❌ Function Size Limit**
- Free tier has 12MB function size limit
- Optimize dependencies or consider Render for dashboard too

**❌ Environment Variables Not Loading**
- Double-check variable names in Vercel dashboard
- Ensure variables are set for production environment

### **API Connection Issues**

**❌ CORS Errors**
```python
# Ensure CORS is configured in app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**❌ SSL Certificate Issues**
- Render provides automatic SSL
- Ensure you're using `https://` in API_URL

---

## 💡 **Part 7: Best Practices**

### **Security**
```python
# Use environment variables for sensitive data
import os

API_KEY = os.getenv('API_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
```

### **Performance Optimization**
```python
# Cache expensive operations in Streamlit
@st.cache_data
def load_model_data():
    # Expensive data loading
    return data

@st.cache_resource
def load_ml_model():
    # Load ML model once
    return model
```

### **Error Handling**
```python
# Robust API calls with retries
import time
import requests

def api_call_with_retry(url, data, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                st.error(f"API call failed: {e}")
                return None
            time.sleep(2 ** attempt)  # Exponential backoff
```

---

## 🎯 **Summary**

### **Deployment Checklist**
- [x] **API on Render**: `render.yaml` configured and deployed
- [x] **Dashboard Platform**: Choose Vercel, Streamlit Cloud, or Render
- [x] **Environment Variables**: API_URL and Streamlit settings configured
- [x] **Health Monitoring**: Endpoints working and monitored
- [x] **CORS Configuration**: Cross-origin requests enabled
- [x] **Error Handling**: Robust error handling and retries implemented

### **Final URLs**
- **API**: `https://fraud-api.onrender.com`
- **API Docs**: `https://fraud-api.onrender.com/docs`
- **Dashboard**: `https://your-app.vercel.app` or `https://your-app.streamlit.app`

### **Cost Estimate**
- **Render.com**: Free tier (750 hours/month)
- **Vercel**: Free tier (unlimited for personal projects)
- **Total**: $0/month for demo/portfolio use

---

**🎉 Your fraud detection system is now live and accessible worldwide!**

*This deployment setup provides a professional-grade system suitable for portfolio demonstration and technical interviews.*
