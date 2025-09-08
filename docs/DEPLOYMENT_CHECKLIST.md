# ✅ Deployment Checklist - Render.com & Streamlit Cloud

## 📋 **Pre-Deployment Checklist**

### **Repository Setup**
- [x] All code committed to GitHub
- [x] `render.yaml` configuration file created
- [x] `requirements-render.txt` optimized for deployment
- [x] Environment variables configured in app code
- [x] Health endpoint available at `/health`
- [x] CORS properly configured for cross-origin requests

### **API Configuration (app/main.py)**
- [x] Port reading from environment: `PORT = int(os.getenv("PORT", "8080"))`
- [x] Host binding to 0.0.0.0: `host="0.0.0.0"`
- [x] Environment detection: `ENVIRONMENT = os.getenv("ENVIRONMENT", "development")`
- [x] CORS middleware configured for dashboard connection

### **Dashboard Configuration (dashboard/app.py)**
- [x] API URL from environment: `os.getenv("API_URL", "http://localhost:8080")`
- [x] Streamlit headless mode support
- [x] Error handling for API connection failures

---

## 🚀 **Deployment Steps**

### **Step 1: Deploy API to Render.com**

#### **Quick Deploy (Recommended)**
1. **Visit**: https://render.com/deploy
2. **Connect GitHub**: Link your repository
3. **Auto-Deploy**: Render detects `render.yaml` and deploys automatically
4. **Wait**: Build takes 2-5 minutes
5. **Verify**: Check `https://fraud-api.onrender.com/health`

#### **Manual Deploy (Alternative)**
1. **Dashboard**: Go to https://dashboard.render.com
2. **New Service**: Click "New +" → "Web Service"
3. **Connect Repo**: Link your GitHub repository
4. **Configure**:
   ```
   Name: fraud-api
   Runtime: Python 3
   Build Command: pip install -r requirements-render.txt
   Start Command: python app/main.py
   ```
5. **Environment Variables**:
   ```
   PORT=10000
   ENVIRONMENT=production
   ```

### **Step 2: Deploy Dashboard to Streamlit Cloud**

1. **Visit**: https://share.streamlit.io
2. **Deploy**: Click "Deploy an app"
3. **Connect**: Link your GitHub repository
4. **Configure**:
   - **Main file path**: `dashboard/app.py`
   - **Python version**: 3.9+ (recommended)
5. **Environment Variables**:
   ```
   API_URL=https://fraud-api.onrender.com
   ```
6. **Deploy**: Click "Deploy!"

### **Step 3: Verify Deployment**

#### **API Tests**
```bash
# Health check
curl https://fraud-api.onrender.com/health

# API documentation
curl https://fraud-api.onrender.com/docs

# Test prediction
curl -X POST "https://fraud-api.onrender.com/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_amount": 500,
    "transaction_hour": 23,
    "merchant_risk_score": 0.8,
    "customer_id": "TEST_001"
  }'
```

#### **Dashboard Tests**
1. **Open**: Your Streamlit Cloud URL
2. **API Status**: Should show "Connected" in green
3. **Make Prediction**: Use the prediction form
4. **Check Metrics**: Verify real-time data updates

---

## 🔧 **Troubleshooting**

### **Common Issues & Solutions**

#### **❌ API Build Fails**
**Symptom**: Build fails during pip install
**Solution**: 
```bash
# Check requirements-render.txt for conflicts
pip install -r requirements-render.txt
# If local install works, issue is with Render
```

#### **❌ API Crashes on Startup**
**Symptom**: Service starts but immediately crashes
**Solutions**:
1. Check Render logs for error messages
2. Verify `PORT` environment variable is set
3. Ensure models directory exists with trained models

#### **❌ Dashboard Can't Connect to API**
**Symptom**: Dashboard shows "API Disconnected"
**Solutions**:
1. Verify API URL environment variable: `API_URL=https://fraud-api.onrender.com`
2. Check API is responding: `curl https://fraud-api.onrender.com/health`
3. Verify CORS is configured in API

#### **❌ Dashboard Times Out**
**Symptom**: Streamlit shows loading spinner indefinitely
**Solutions**:
1. Check API response time (should be <30 seconds)
2. Verify dashboard timeout settings
3. Check Streamlit Cloud resource limits

#### **❌ Health Check Fails**
**Symptom**: Render shows service as unhealthy
**Solutions**:
1. Ensure `/health` endpoint returns 200 status
2. Check if health check timeout is too short
3. Verify app binds to correct port and host

### **Performance Issues**

#### **⚠️ Slow Cold Starts**
**Expected**: First request after inactivity may take 10-30 seconds
**Solution**: Keep service warm with uptime monitoring tools

#### **⚠️ Memory Limits**
**Free Tier Limit**: 512MB RAM
**Monitor**: Check Render dashboard for memory usage
**Optimize**: Use requirements-render.txt for minimal dependencies

---

## 📊 **Post-Deployment Monitoring**

### **Daily Checks**
- [ ] API health endpoint responding
- [ ] Dashboard loading and connecting to API
- [ ] No errors in Render/Streamlit logs

### **Weekly Checks**
- [ ] Response times within acceptable limits
- [ ] Memory usage not approaching limits
- [ ] SSL certificates valid and renewing

### **Monthly Checks**
- [ ] Dependencies up to date (security patches)
- [ ] Free tier usage within limits
- [ ] Performance metrics review

---

## 🎯 **Success Metrics**

### **API Performance**
- ✅ **Uptime**: >99% (Render free tier)
- ✅ **Response Time**: <200ms (excluding cold starts)
- ✅ **Health Check**: Always returns 200
- ✅ **Memory Usage**: <400MB (80% of free tier limit)

### **Dashboard Performance**
- ✅ **Load Time**: <10 seconds (excluding cold starts)
- ✅ **API Connection**: Consistent green status
- ✅ **Interactive Elements**: All forms and charts working
- ✅ **Real-time Updates**: Metrics updating properly

### **Integration Testing**
- ✅ **End-to-End**: Prediction request from dashboard to API
- ✅ **AML Features**: Compliance checks working
- ✅ **Velocity Monitoring**: Real-time transaction analysis
- ✅ **Error Handling**: Graceful failure modes

---

## 🔗 **Final URLs**

After successful deployment, you'll have:

- **🔧 API**: `https://fraud-api.onrender.com`
- **📖 API Docs**: `https://fraud-api.onrender.com/docs`
- **🏥 Health Check**: `https://fraud-api.onrender.com/health`
- **📊 Dashboard**: `https://[your-app].streamlit.app`

### **Update Portfolio Links**
Update your portfolio/resume with these live demo links!

---

## 💡 **Pro Tips**

1. **Custom Domains**: Both Render and Streamlit Cloud support custom domains
2. **Monitoring**: Set up uptime monitoring with services like UptimeRobot
3. **Backups**: Keep a backup of your trained models in cloud storage
4. **Scaling**: Ready to upgrade to paid tiers for production use
5. **Documentation**: Keep this deployment guide for future reference

---

**🎉 Congratulations! Your fraud detection system is now live and accessible worldwide!**

*Total deployment cost: $0/month on free tiers*  
*Estimated deployment time: 10-15 minutes*  
*Professional portfolio piece: ✅ Ready for interviews*
