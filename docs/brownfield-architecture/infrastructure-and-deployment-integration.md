# Infrastructure and Deployment Integration

### Existing Infrastructure

**Current Deployment:** Railway Cloud with automatic deployment from main branch, Docker containerization using existing Dockerfile and requirements.txt
**Infrastructure Tools:** Railway CLI, Docker, Git-based deployment pipeline, automatic HTTPS and domain management
**Environments:** Production on Railway Cloud, local development environment, automatic environment variable management

### Enhancement Deployment Strategy

**Deployment Approach:** Zero-downtime rolling deployment leveraging Railway's existing container management, enhanced health checks for new AML/velocity endpoints

**Infrastructure Changes:**
- **Enhanced Health Checks:** Extend existing `/health` endpoint to validate AML and velocity model loading
- **Memory Monitoring:** Add tracking for new model artifacts loading within Railway's 500MB free tier limit
- **Environment Variables:** Add new configuration for AML thresholds and velocity parameters:
  ```
  AML_RISK_THRESHOLD=0.7
  VELOCITY_HIGH_RISK_THRESHOLD=0.8
  VELOCITY_ANALYSIS_WINDOWS=1h,24h,7d
  AML_SUSPICIOUS_AMOUNT_THRESHOLD=10000
  ```

**Pipeline Integration:** 
- Maintain existing automatic deployment on git push to main
- Enhance existing Docker build process to include new model artifacts
- Extend current Railway environment configuration with new variables
- Preserve existing Railway service monitoring and logging

### AWS-Ready Architecture Documentation

**AWS ECS Deployment Option:**
```yaml
# infrastructure/aws/ecs-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: payment-risk-api
spec:
  taskDefinition:
    family: payment-risk-scoring
    cpu: 512
    memory: 1024
    containers:
      - name: api-service
        image: payment-risk-api:latest
        portMappings:
          - containerPort: 8080
            protocol: tcp
        environment:
          - name: AML_RISK_THRESHOLD
            value: "0.7"
          - name: VELOCITY_HIGH_RISK_THRESHOLD
            value: "0.8"
```

**AWS Lambda Serverless Option:**
```yaml
# infrastructure/aws/serverless.yaml
service: payment-risk-scoring
provider:
  name: aws
  runtime: python3.9
  memorySize: 1024
  timeout: 30
functions:
  fraudDetection:
    handler: app.main.lambda_handler
    events:
      - http:
          path: /predict
          method: post
  amlCheck:
    handler: app.main.aml_lambda_handler
    events:
      - http:
          path: /aml_check
          method: post
```

**Cost-Optimized AWS Architecture:**
- **Development:** AWS Free Tier with t3.micro EC2 instances
- **Production:** ECS Fargate with auto-scaling based on CPU/memory usage
- **Storage:** S3 for model artifacts, CloudWatch for monitoring
- **Estimated Monthly Cost:** $15-50 for low-medium traffic (vs Railway free tier)

### Rollback Strategy

**Rollback Method:** 
- Railway automatic rollback capability preserved
- Git-based rollback to previous commit automatically deploys previous version
- Feature flags for gradual AML/velocity feature activation
- Model artifact versioning allows fallback to previous models

**Risk Mitigation:**
- **Blue-Green Deployment:** Use Railway's preview deployments for testing before main deployment
- **Circuit Breaker Pattern:** New features degrade gracefully if models fail to load
- **Monitoring Alerts:** Enhanced monitoring for memory usage, response times, error rates
- **Gradual Rollout:** Feature flags allow enabling AML/velocity features for subset of traffic

**Monitoring:**
- **Enhanced Metrics:** Extend existing monitoring with AML processing time, velocity calculation performance
- **Memory Tracking:** Monitor model loading impact on Railway's 500MB limit
- **Performance Monitoring:** Track API response times to ensure sub-150ms requirement maintained
- **Error Tracking:** Enhanced logging for new feature failures with automatic alerting
