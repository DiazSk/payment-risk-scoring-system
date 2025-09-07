# CloudFormation Deployment

This directory contains AWS CloudFormation templates and deployment scripts for the Fraud Detection System.

## Files

- `fraud-detection-stack.yaml` - Main CloudFormation template
- `parameters.env` - Environment-specific parameters
- `deploy.sh` - Bash deployment script (Linux/macOS)
- `deploy.ps1` - PowerShell deployment script (Windows)

## Prerequisites

1. **AWS CLI**: Install and configure the AWS CLI
   ```bash
   aws configure
   ```

2. **IAM Permissions**: Ensure your AWS credentials have the following permissions:
   - CloudFormation: Full access
   - EC2: Full access
   - RDS: Full access
   - ElastiCache: Full access
   - S3: Full access
   - IAM: Create roles and policies
   - CloudWatch: Create log groups
   - SNS: Create topics

## Quick Start

### Using Bash (Linux/macOS)

1. Configure parameters:
   ```bash
   cp parameters.env my-parameters.env
   # Edit my-parameters.env with your values
   ```

2. Deploy the stack:
   ```bash
   chmod +x deploy.sh
   PARAMETERS_FILE=my-parameters.env ./deploy.sh deploy
   ```

### Using PowerShell (Windows)

1. Configure parameters:
   ```powershell
   Copy-Item parameters.env my-parameters.env
   # Edit my-parameters.env with your values
   ```

2. Deploy the stack:
   ```powershell
   .\deploy.ps1 deploy -ParametersFile my-parameters.env
   ```

## Configuration

### Parameters

Edit the `parameters.env` file to customize your deployment:

| Parameter | Description | Default | Example |
|-----------|-------------|---------|---------|
| `Environment` | Environment name | `development` | `production` |
| `DatabasePassword` | RDS password | (required) | `MySecurePass123!` |
| `DatabaseUsername` | RDS username | `fraud_admin` | `admin` |
| `DatabaseName` | Database name | `fraud_detection` | `fraud_db` |
| `DBInstanceClass` | RDS instance type | `db.t3.micro` | `db.t3.small` |
| `APIInstanceType` | EC2 instance type | `t3.micro` | `t3.small` |
| `EnableMultiAZ` | Multi-AZ RDS | `false` | `true` |
| `EnableRedis` | Redis cache | `true` | `false` |

### Cost Optimization

For **development/testing** environments:
- Use `db.t3.micro` for database
- Use `t3.micro` for API instances
- Set `EnableMultiAZ=false`
- Consider `EnableRedis=false` if not needed

For **production** environments:
- Use `db.t3.small` or larger for database
- Use `t3.small` or larger for API instances
- Set `EnableMultiAZ=true` for high availability
- Keep `EnableRedis=true` for performance

## Architecture

The CloudFormation template creates:

### Networking
- VPC with public and private subnets across 2 AZs
- Internet Gateway and route tables
- Security groups for each tier

### Compute
- Application Load Balancer (ALB)
- Target groups for API and Dashboard
- IAM roles and instance profiles

### Database
- PostgreSQL RDS instance
- Database subnet group
- Optional Multi-AZ deployment

### Caching
- Redis ElastiCache cluster (optional)
- Cache subnet group

### Storage
- S3 bucket for application data
- Versioning and encryption enabled

### Monitoring
- CloudWatch log groups
- SNS topic for notifications

## Deployment Commands

### Deploy Stack
```bash
# Bash
./deploy.sh deploy

# PowerShell
.\deploy.ps1 deploy
```

### Update Stack
The deployment script automatically detects if the stack exists and performs an update instead of create.

### View Outputs
```bash
# Bash
./deploy.sh outputs

# PowerShell
.\deploy.ps1 outputs
```

### Validate Template
```bash
# Bash
./deploy.sh validate

# PowerShell
.\deploy.ps1 validate
```

### Delete Stack
```bash
# Bash
./deploy.sh delete

# PowerShell
.\deploy.ps1 delete
```

## Post-Deployment

After successful deployment, you'll receive outputs including:

- **ApplicationURL**: Load balancer DNS name for accessing the application
- **DatabaseEndpoint**: RDS endpoint for database connections
- **RedisEndpoint**: ElastiCache endpoint (if enabled)
- **S3BucketName**: S3 bucket for application data

### Connect to Resources

1. **Database**: Use the connection string output to connect your application
2. **S3 Bucket**: Configure your application to use the created bucket
3. **Load Balancer**: Point your domain to the ALB DNS name

## Troubleshooting

### Common Issues

1. **Stack creation fails**: Check IAM permissions and parameter values
2. **Template validation errors**: Ensure CloudFormation intrinsic functions are correct
3. **Resource limits**: Verify AWS service limits in your region
4. **Parameter errors**: Check required parameters are provided

### Debugging

1. Check CloudFormation console for detailed error messages
2. Review CloudFormation events for specific resource failures
3. Verify AWS CLI configuration and credentials
4. Check AWS service limits and quotas

### Rollback

CloudFormation automatically rolls back failed stack operations. For manual rollback:
1. Delete the failed stack
2. Fix the issue
3. Redeploy with corrected configuration

## Security Considerations

- Database is placed in private subnets
- Security groups follow least privilege principle
- S3 bucket has public access blocked
- Encryption enabled for RDS and S3
- IAM roles use minimal required permissions

## Cost Monitoring

Monitor costs through:
- AWS Cost Explorer
- CloudWatch billing alarms
- Resource tagging for cost allocation

## Scaling

The template supports scaling through:
- Auto Scaling Groups (can be added)
- RDS read replicas (can be added)
- ElastiCache cluster mode (can be enabled)
- Load balancer target groups (already configured)

## Support

For issues with this CloudFormation template:
1. Check the troubleshooting section above
2. Review AWS CloudFormation documentation
3. Check AWS service health dashboard
4. Contact your AWS support team
