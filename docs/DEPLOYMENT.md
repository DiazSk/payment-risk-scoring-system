# 🚀 Deployment Guide - Credit Card Fraud Detection System

[![Deploy Status](https://img.shields.io/badge/Deploy-Ready-brightgreen?style=for-the-badge)](https://railway.app)
[![Live Demo](https://img.shields.io/badge/Live-Demo-blue?style=for-the-badge)](https://fraud-dashboard-production.up.railway.app/)

> **Complete guide for deploying the Credit Card Fraud Detection System to production**

---

## 📋 **Quick Start Guides**

- 🆓 **[Free-Tier Deployment](FREE_TIER_DEPLOYMENT.md)** - Railway, Render (recommended for portfolios)
- ☁️ **[AWS Deployment](AWS_DEPLOYMENT_GUIDE.md)** - Production-grade cloud architecture  
- 🐳 **Docker Deployment** - Container-based deployment (below)

## 🎯 **Deployment Options**

### **🌟 Recommended: Railway (Used in Production)**
- ✅ **Zero-config deployment** - Automatic detection
- ✅ **Free tier available** - Perfect for portfolios
- ✅ **Professional URLs** - Custom subdomain support
- ✅ **Auto-scaling** - Handles traffic spikes
- ✅ **GitHub integration** - Deploy on git push

### **⚡ Alternative Platforms**
- **Heroku**: Classic PaaS with extensive addon ecosystem
- **Render**: Modern platform with static site generation
- **AWS**: Production-ready with full control (more complex)
- **GCP**: Google Cloud with ML optimization
- **Azure**: Microsoft cloud with integrated AI services

---

## 🚂 **Railway Deployment (Production Method)**

### **Prerequisites**
- ✅ GitHub account with repository
- ✅ Railway account (free signup)
- ✅ Trained ML models in `models/` directory
- ✅ Python 3.8+ compatible requirements.txt

### **🚀 Quick Deploy (5 Minutes)**

#### **Option A: GitHub Integration (Recommended)**

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "feat: Add complete fraud detection system"
   git push origin main
   ```

2. **Connect to Railway**
   - Visit [railway.app](https://railway.app)
   - Click "Start a New Project"
   - Choose "Deploy from GitHub repo"
   - Select your repository

3. **Configure Services**
   ```yaml
   API Service:
     - Name: fraud-api
     - Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
     - Port: 8080
     - Domain: credit-card-fraud-api
   
   Dashboard Service:
     - Name: dashboard  
     - Start Command: streamlit run dashboard/app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
     - Port: 8080
     - Domain: credit-card-fraud-dashboard
   ```

4. **Set Environment Variables**
   ```bash
   # Dashboard service variables
   API_URL=https://credit-card-fraud-api.up.railway.app
   ENVIRONMENT=production
   ```

5. **Deploy & Test**
   - Services auto-deploy on git push
   - Test URLs: API and Dashboard
   - Monitor logs for startup success

#### **Option B: CLI Deployment**

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Create & Deploy API**
   ```bash
   railway init
   # Project name: fraud-api
   railway up --service api
   railway domain
   ```

3. **Create & Deploy Dashboard**
   ```bash
   railway add
   # Service type: Empty Service
   # Service name: dashboard
   railway up --service dashboard
   railway domain
   ```

---

## 🐳 **Docker Deployment**

### **Single Container (Development)**

#### **Build & Run Locally**
```bash
# Build Docker image
docker build -t fraud-detection .

# Run API
docker run -p 8000:8000 \
  -e PORT=8000 \
  fraud-detection

# Run Dashboard (separate container)
docker run -p 8501:8501 \
  -e API_URL=http://localhost:8000 \
  -e PORT=8501 \
  fraud-detection \
  streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0
```

#### **Docker Compose (Full Stack)**
```yaml
# docker-compose.yml
version: '3.8'
services:
  fraud-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PORT=8000
      - ENVIRONMENT=production
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    
  fraud-dashboard:
    build: .
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://fraud-api:8000
      - PORT=8501
    command: streamlit run dashboard/app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
    depends_on:
      - fraud-api

# Deploy with:
docker-compose up -d
```

---

## ☁️ **AWS Deployment**

### **AWS ECS (Container Service)**

#### **Infrastructure Setup**
```bash
# Create ECS cluster
aws ecs create-cluster --cluster-name fraud-detection

# Create task definition
aws ecs register-task-definition \
  --family fraud-detection \
  --network-mode awsvpc \
  --requires-compatibility FARGATE \
  --cpu 1024 \
  --memory 2048 \
  --task-role-arn arn:aws:iam::account:role/ecsTaskRole
```

#### **Service Configuration**
```yaml
# ecs-task-definition.yml
family: fraud-detection
networkMode: awsvpc
requiresCompatibilities:
  - FARGATE
cpu: 1024
memory: 2048
containerDefinitions:
  - name: fraud-api
    image: your-account.dkr.ecr.region.amazonaws.com/fraud-detection:latest
    portMappings:
      - containerPort: 8000
        protocol: tcp
    environment:
      - name: PORT
        value: "8000"
      - name: ENVIRONMENT  
        value: "production"
```

### **AWS Lambda (Serverless)**

#### **API Gateway + Lambda**
```python
# lambda_handler.py
import json
from app.main import app
from mangum import Mangum

handler = Mangum(app)

def lambda_handler(event, context):
    return handler(event, context)
```

#### **Deployment Package**
```bash
# Create deployment package
pip install -r requirements.txt -t ./package
cp -r app/ package/
cp -r models/ package/
cd package && zip -r ../fraud-detection-lambda.zip .

# Deploy to Lambda
aws lambda create-function \
  --function-name credit-card-fraud-detection \
  --runtime python3.9 \
  --role arn:aws:iam::account:role/lambda-execution-role \
  --handler lambda_handler.lambda_handler \
  --zip-file fileb://fraud-detection-lambda.zip
```

---

## 🌐 **Kubernetes Deployment**

### **K8s Manifests**

#### **API Deployment**
```yaml
# k8s/api-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fraud-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fraud-api
  template:
    metadata:
      labels:
        app: fraud-api
    spec:
      containers:
      - name: fraud-api
        image: fraud-detection:latest
        ports:
        - containerPort: 8000
        env:
        - name: PORT
          value: "8000"
        - name: ENVIRONMENT
          value: "production"
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m  
            memory: 1Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### **Service & Ingress**
```yaml
# k8s/api-service.yml
apiVersion: v1
kind: Service
metadata:
  name: fraud-api-service
spec:
  selector:
    app: fraud-api
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP

---
# k8s/ingress.yml  
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fraud-detection-ingress
spec:
  rules:
  - host: api.fraud-detection.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: fraud-api-service
            port:
              number: 80
```

---

## 🔧 **Environment Configuration**

### **Environment Variables Reference**

#### **API Service Variables**
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | ✅ | 8000 | Server port |
| `ENVIRONMENT` | ❌ | development | Deployment environment |
| `LOG_LEVEL` | ❌ | INFO | Logging verbosity |
| `MODEL_CACHE_TTL` | ❌ | 3600 | Model cache duration (seconds) |
| `MAX_BATCH_SIZE` | ❌ | 1000 | Maximum batch prediction size |
| `CORS_ORIGINS` | ❌ | ["*"] | Allowed CORS origins |

#### **Dashboard Service Variables**
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_URL` | ✅ | http://localhost:8000 | Backend API URL |
| `PORT` | ✅ | 8501 | Streamlit port |
| `STREAMLIT_SERVER_HEADLESS` | ❌ | true | Headless mode |
| `STREAMLIT_SERVER_ENABLE_CORS` | ❌ | false | CORS setting |

### **Production Environment Example**
```bash
# .env.production
PORT=8000
ENVIRONMENT=production
LOG_LEVEL=INFO
API_URL=https://credit-card-fraud-api.up.railway.app
STREAMLIT_SERVER_HEADLESS=true
MODEL_CACHE_TTL=7200
```

---

## 🧪 **Deployment Testing**

### **Pre-deployment Checklist**

#### **✅ Code Quality**
- [ ] All tests passing (`python -m pytest`)
- [ ] Type checking clean (`mypy app/ dashboard/`)
- [ ] Code formatting (`black . --check`)
- [ ] Security scan (`bandit -r app/`)
- [ ] Dependency audit (`safety check`)

#### **✅ Model Validation** 
- [ ] Models trained and saved (`models/*.pkl` exist)
- [ ] Metadata file present (`models/model_metadata.json`)
- [ ] Performance metrics acceptable (>95% accuracy)
- [ ] Feature pipeline validated (`python tests/test_complete_pipeline.py`)

#### **✅ API Testing**
- [ ] Local API starts successfully (`python start_api.py`)
- [ ] All endpoints responding (`python tests/test_api.py`)
- [ ] Documentation generated (`/docs` endpoint works)
- [ ] Health checks passing (`curl /health`)

#### **✅ Dashboard Testing**
- [ ] Dashboard loads locally (`streamlit run dashboard/app.py`)
- [ ] API connection works (shows "Connected")
- [ ] Charts render correctly (no JavaScript errors)
- [ ] All pages functional (Overview, Prediction, Performance, etc.)

### **Post-deployment Validation**

#### **Smoke Tests**
```bash
# API health check
curl https://your-api-url.railway.app/health

# Single prediction test
curl -X POST "https://your-api-url.railway.app/predict" \
  -H "Content-Type: application/json" \
  -d '{"transaction_amount": 100, "transaction_hour": 14}'

# Dashboard accessibility
curl -I https://your-dashboard-url.railway.app
```

#### **Load Testing**
```bash
# Install testing tools
pip install locust

# Run load tests
locust -f tests/load_test.py --host https://your-api-url.railway.app
```

---

## 🔄 **CI/CD Pipeline**

### **GitHub Actions Workflow**

#### **Automated Testing & Deployment**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Railway
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest
    - name: Run tests
      run: |
        python -m pytest tests/
        python tests/test_complete_pipeline.py

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    - name: Deploy to Railway
      uses: railway/cli-action@v1
      with:
        railway-token: ${{ secrets.RAILWAY_TOKEN }}
      run: railway up --service api && railway up --service dashboard
```

### **Deployment Automation**
```bash
# Automated deployment script
#!/bin/bash
set -e

echo "🚀 Starting automated deployment..."

# Run tests
python -m pytest tests/ --verbose
echo "✅ All tests passed"

# Deploy API
railway service api
railway up
echo "✅ API deployed"

# Deploy Dashboard  
railway service dashboard
railway up
echo "✅ Dashboard deployed"

# Validate deployment
sleep 30
curl -f https://credit-card-fraud-api.up.railway.app/health
echo "✅ Deployment validated"

echo "🎉 Deployment complete!"
```

---

## 🔧 **Troubleshooting Guide**

### **Common Deployment Issues**

#### **❌ Models Not Loading**
**Symptoms**: API starts but shows "models not loaded" error

**Solutions**:
```bash
# Check models directory exists
ls -la models/

# Verify model files
ls -la models/*.pkl

# Check file sizes (should be >1MB each)
du -h models/*.pkl

# Test model loading locally
python -c "import joblib; print(joblib.load('models/ensemble_model.pkl'))"
```

#### **❌ Port Binding Issues**
**Symptoms**: 502 Bad Gateway or connection refused

**Solutions**:
```bash
# Check PORT environment variable
echo $PORT

# Verify start command uses $PORT
uvicorn app.main:app --host 0.0.0.0 --port $PORT

# Test local binding
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### **❌ Dashboard API Connection Failed**
**Symptoms**: Dashboard shows "API Disconnected"

**Solutions**:
```bash
# Check API_URL environment variable
echo $API_URL

# Test API connectivity
curl $API_URL/health

# Verify CORS settings in API
# Ensure API allows dashboard domain
```

#### **❌ Build Failures**
**Symptoms**: Railway build fails during pip install

**Solutions**:
```bash
# Check requirements.txt format
cat requirements.txt

# Test local installation
pip install -r requirements.txt

# Use specific versions (remove >= constraints)
# Example: numpy==1.24.3 instead of numpy>=1.24.0
```

### **Performance Issues**

#### **🐌 Slow Response Times**
**Diagnosis**:
```bash
# Check API metrics
curl https://your-api-url.railway.app/metrics

# Monitor resource usage in Railway dashboard
# Look for CPU/Memory spikes
```

**Solutions**:
- Optimize model loading (lazy loading)
- Add response caching for repeated requests  
- Increase Railway instance size
- Implement connection pooling

#### **💥 High Error Rates**
**Diagnosis**:
```bash
# Check error logs
railway logs --service api --tail 100

# Test with known good data
curl -X POST "https://your-api-url.railway.app/predict" \
  -H "Content-Type: application/json" \
  -d '{"transaction_amount": 100, "transaction_hour": 14}'
```

**Solutions**:
- Validate input schemas
- Add better error handling
- Implement graceful degradation
- Monitor model performance drift

---

## 📊 **Monitoring & Maintenance**

### **Health Monitoring Setup**

#### **Automated Health Checks**
```bash
# Create monitoring script
#!/bin/bash
# health_monitor.sh

API_URL="https://credit-card-fraud-api.up.railway.app"
DASHBOARD_URL="https://credit-card-fraud-dashboard.up.railway.app"

# Check API health
if curl -f $API_URL/health > /dev/null 2>&1; then
    echo "✅ API healthy"
else
    echo "❌ API unhealthy" 
    # Send alert (email, Slack, etc.)
fi

# Check dashboard accessibility
if curl -f $DASHBOARD_URL > /dev/null 2>&1; then
    echo "✅ Dashboard accessible"
else
    echo "❌ Dashboard inaccessible"
    # Send alert
fi
```

#### **Performance Monitoring**
```python
# monitor_performance.py
import requests
import time
import json

def monitor_api_performance():
    api_url = "https://credit-card-fraud-api.up.railway.app"
    
    # Test response time
    start = time.time()
    response = requests.get(f"{api_url}/health")
    response_time = (time.time() - start) * 1000
    
    # Log metrics
    print(f"Response time: {response_time:.1f}ms")
    
    # Alert if slow
    if response_time > 200:
        send_alert(f"API slow: {response_time:.1f}ms")
    
    return response_time

# Run every 5 minutes
```

### **Log Analysis**
```bash
# Monitor API logs
railway logs --service api --follow

# Monitor dashboard logs  
railway logs --service dashboard --follow

# Search for errors
railway logs --service api | grep ERROR

# Performance analysis
railway logs --service api | grep "Response time"
```

---

## 🔄 **Scaling & Optimization**

### **Horizontal Scaling**

#### **Multi-Instance Deployment**
```bash
# Scale API service
railway scale --service api --replicas 3

# Configure load balancing (automatic in Railway)
# Monitor distributed performance
```

#### **Database Integration (Future)**
```python
# database_config.py
DATABASE_CONFIG = {
    'postgres': {
        'host': os.getenv('PGHOST'),
        'port': os.getenv('PGPORT', 5432),
        'database': os.getenv('PGDATABASE'),
        'user': os.getenv('PGUSER'),
        'password': os.getenv('PGPASSWORD')
    }
}
```

### **Performance Optimization**

#### **Caching Strategy**
```python
# Implement Redis caching
import redis

cache = redis.Redis(
    host=os.getenv('REDIS_HOST'),
    port=6379,
    decode_responses=True
)

# Cache model predictions
def cached_predict(transaction_hash, features):
    cached_result = cache.get(transaction_hash)
    if cached_result:
        return json.loads(cached_result)
    
    result = model.predict(features)
    cache.setex(transaction_hash, 3600, json.dumps(result))
    return result
```

---

## 🛡️ **Security Hardening**

### **Production Security Checklist**

#### **✅ API Security**
- [ ] HTTPS enforced (no HTTP redirects)
- [ ] Rate limiting configured (1000 req/min)
- [ ] Input validation comprehensive (Pydantic)
- [ ] Error messages sanitized (no stack traces)
- [ ] CORS properly configured (specific origins)
- [ ] API keys implemented (for enterprise)

#### **✅ Infrastructure Security**
- [ ] Environment variables secured (no hardcoded secrets)
- [ ] Container security scanned (no vulnerabilities)
- [ ] Network isolation (private subnets)
- [ ] Access logs enabled (audit trail)
- [ ] Backup strategy implemented (model versioning)

### **Security Headers**
```python
# Add security middleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["credit-card-fraud-api.up.railway.app"]
)
```

---

## 📋 **Deployment Checklist**

### **Pre-Deployment**
- [ ] ✅ Code committed and pushed to GitHub
- [ ] ✅ All tests passing locally
- [ ] ✅ Models trained and saved
- [ ] ✅ Requirements.txt updated
- [ ] ✅ Environment variables configured
- [ ] ✅ Documentation updated

### **During Deployment**
- [ ] ✅ Railway services created
- [ ] ✅ Build logs checked (no errors)
- [ ] ✅ Deploy logs monitored
- [ ] ✅ Health checks passing
- [ ] ✅ URLs accessible

### **Post-Deployment**
- [ ] ✅ API endpoints tested
- [ ] ✅ Dashboard functionality verified  
- [ ] ✅ Performance benchmarks run
- [ ] ✅ Monitoring configured
- [ ] ✅ Documentation URLs updated

---

## 🚀 **Production Readiness**

### **Enterprise Deployment Considerations**

#### **Scalability Requirements**
- **Traffic**: 10,000+ requests/minute
- **Availability**: 99%+ uptime SLA
- **Geographic**: Multi-region deployment
- **Compliance**: SOC2, PCI DSS compliance

#### **Infrastructure Upgrades**
```yaml
Production Infrastructure:
├── Load Balancer: HAProxy or AWS ALB
├── API Gateway: Kong or AWS API Gateway  
├── Container Orchestration: Kubernetes or ECS
├── Database: PostgreSQL with read replicas
├── Caching: Redis cluster
├── Monitoring: Prometheus + Grafana
├── Logging: ELK stack or Splunk
└── Alerts: PagerDuty integration
```

---

## 📞 **Support & Maintenance**

### **Ongoing Maintenance Tasks**

#### **Daily**
- Monitor system health and performance
- Review error logs and alerts
- Check API response times

#### **Weekly**  
- Analyze model performance metrics
- Review traffic patterns and scaling needs
- Update dependencies (security patches)

#### **Monthly**
- Model performance evaluation
- Cost optimization review
- Security audit and updates
- Backup validation

#### **Quarterly**
- Model retraining with new data
- Architecture review and optimization
- Disaster recovery testing
- Performance benchmark updates

---

## 🏆 **Deployment Success Metrics**

### **Success Indicators**
- ✅ **API Health**: 200 OK responses from `/health`
- ✅ **Dashboard Loading**: Streamlit UI loads without errors
- ✅ **API Integration**: Dashboard shows "API Connected"
- ✅ **Predictions Working**: Real fraud detection responses
- ✅ **Performance**: Response times <100ms
- ✅ **Availability**: >99% uptime over 24 hours

### **Business Validation**
- ✅ **Fraud Detection**: Model correctly identifies test fraud cases
- ✅ **False Positives**: <1% legitimate transactions flagged
- ✅ **Response Speed**: Interactive user experience
- ✅ **Scalability**: Handles expected production load
- ✅ **Professional URLs**: Suitable for resume and demos

---

<div align="center">

**🎯 Ready for Enterprise Deployment**

*This system has been tested and validated for production use*

**📧 Questions?** Contact: zaid07sk@gmail.com

</div>