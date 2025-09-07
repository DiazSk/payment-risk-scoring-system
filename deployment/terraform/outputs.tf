# Terraform Outputs for Fraud Detection System AWS Deployment

# VPC Information
output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "availability_zones" {
  description = "List of availability zones"
  value       = local.azs
}

# Subnet Information
output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = aws_subnet.private[*].id
}

output "database_subnet_ids" {
  description = "IDs of the database subnets"
  value       = aws_subnet.database[*].id
}

# Security Group Information
output "alb_security_group_id" {
  description = "ID of the ALB security group"
  value       = aws_security_group.alb.id
}

output "api_security_group_id" {
  description = "ID of the API security group"
  value       = aws_security_group.api.id
}

output "dashboard_security_group_id" {
  description = "ID of the dashboard security group"
  value       = aws_security_group.dashboard.id
}

output "database_security_group_id" {
  description = "ID of the database security group"
  value       = aws_security_group.database.id
}

output "redis_security_group_id" {
  description = "ID of the Redis security group"
  value       = var.enable_redis ? aws_security_group.redis.id : null
}

# Database Information
output "database_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true
}

output "database_port" {
  description = "RDS instance port"
  value       = aws_db_instance.main.port
}

output "database_name" {
  description = "Database name"
  value       = aws_db_instance.main.db_name
}

output "database_username" {
  description = "Database username"
  value       = aws_db_instance.main.username
  sensitive   = true
}

# Redis Information
output "redis_endpoint" {
  description = "Redis cluster endpoint"
  value       = var.enable_redis ? aws_elasticache_replication_group.main[0].primary_endpoint_address : null
}

output "redis_port" {
  description = "Redis cluster port"
  value       = var.enable_redis ? aws_elasticache_replication_group.main[0].port : null
}

# Load Balancer Information
output "load_balancer_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.main.dns_name
}

output "load_balancer_zone_id" {
  description = "Zone ID of the load balancer"
  value       = aws_lb.main.zone_id
}

output "load_balancer_arn" {
  description = "ARN of the load balancer"
  value       = aws_lb.main.arn
}

# Target Group Information
output "api_target_group_arn" {
  description = "ARN of the API target group"
  value       = aws_lb_target_group.api.arn
}

output "dashboard_target_group_arn" {
  description = "ARN of the dashboard target group"
  value       = aws_lb_target_group.dashboard.arn
}

# S3 Information
output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.fraud_detection.id
}

output "s3_bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.fraud_detection.arn
}

output "s3_bucket_region" {
  description = "Region of the S3 bucket"
  value       = aws_s3_bucket.fraud_detection.region
}

# IAM Information
output "ec2_instance_profile_name" {
  description = "Name of the EC2 instance profile"
  value       = aws_iam_instance_profile.ec2_profile.name
}

output "ec2_role_arn" {
  description = "ARN of the EC2 IAM role"
  value       = aws_iam_role.ec2_role.arn
}

# CloudWatch Information
output "api_log_group_name" {
  description = "Name of the API CloudWatch log group"
  value       = aws_cloudwatch_log_group.api.name
}

output "dashboard_log_group_name" {
  description = "Name of the dashboard CloudWatch log group"
  value       = aws_cloudwatch_log_group.dashboard.name
}

# Application URLs
output "api_url" {
  description = "URL for the API"
  value       = "http://${aws_lb.main.dns_name}"
}

output "dashboard_url" {
  description = "URL for the dashboard"
  value       = "http://${aws_lb.main.dns_name}:8501"
}

# Environment Information
output "environment" {
  description = "Environment name"
  value       = var.environment
}

output "aws_region" {
  description = "AWS region"
  value       = var.aws_region
}

output "account_id" {
  description = "AWS account ID"
  value       = data.aws_caller_identity.current.account_id
}

# Connection Strings
output "database_connection_string" {
  description = "Database connection string"
  value       = "postgresql://${var.database_username}:${var.database_password}@${aws_db_instance.main.endpoint}/${aws_db_instance.main.db_name}"
  sensitive   = true
}

output "redis_connection_string" {
  description = "Redis connection string"
  value       = var.enable_redis ? "redis://${aws_elasticache_replication_group.main[0].primary_endpoint_address}:${aws_elasticache_replication_group.main[0].port}" : null
  sensitive   = true
}

# Network Configuration
output "internet_gateway_id" {
  description = "ID of the Internet Gateway"
  value       = aws_internet_gateway.main.id
}

output "nat_gateway_ids" {
  description = "IDs of the NAT Gateways"
  value       = var.enable_nat_gateway ? aws_nat_gateway.main[*].id : []
}

output "public_route_table_id" {
  description = "ID of the public route table"
  value       = aws_route_table.public.id
}

output "private_route_table_ids" {
  description = "IDs of the private route tables"
  value       = aws_route_table.private[*].id
}

# Resource Tags
output "common_tags" {
  description = "Common tags applied to resources"
  value       = local.common_tags
}

# Security Configuration Summary
output "security_summary" {
  description = "Summary of security configurations"
  value = {
    database_encrypted     = aws_db_instance.main.storage_encrypted
    s3_encryption_enabled = true
    redis_encryption      = var.enable_redis ? aws_elasticache_replication_group.main[0].at_rest_encryption_enabled : null
    multi_az_enabled      = aws_db_instance.main.multi_az
    backup_retention      = aws_db_instance.main.backup_retention_period
  }
}

# Cost Estimation Information
output "cost_estimation" {
  description = "Estimated monthly costs (approximate)"
  value = {
    environment = var.environment
    instance_types = {
      database = var.db_instance_class
      redis    = var.enable_redis ? var.redis_node_type : "disabled"
    }
    estimated_monthly_cost_usd = var.environment == "development" ? "30-60" : var.environment == "staging" ? "100-200" : "300-500"
    note = "Costs vary based on usage, data transfer, and additional services"
  }
}

# Deployment Information
output "deployment_info" {
  description = "Information for deployment and configuration"
  value = {
    vpc_id                = aws_vpc.main.id
    public_subnet_ids     = aws_subnet.public[*].id
    private_subnet_ids    = aws_subnet.private[*].id
    database_subnet_group = aws_db_subnet_group.main.name
    s3_bucket            = aws_s3_bucket.fraud_detection.id
    load_balancer_dns    = aws_lb.main.dns_name
    api_target_group     = aws_lb_target_group.api.arn
    dashboard_target_group = aws_lb_target_group.dashboard.arn
    instance_profile     = aws_iam_instance_profile.ec2_profile.name
    log_groups = {
      api       = aws_cloudwatch_log_group.api.name
      dashboard = aws_cloudwatch_log_group.dashboard.name
    }
  }
}

# Quick Setup Commands
output "setup_commands" {
  description = "Quick setup commands for application deployment"
  value = {
    database_setup = "psql ${aws_db_instance.main.endpoint} -U ${var.database_username} -d ${aws_db_instance.main.db_name}"
    s3_model_upload = "aws s3 cp model.pkl s3://${aws_s3_bucket.fraud_detection.id}/models/production/"
    log_monitoring = "aws logs tail ${aws_cloudwatch_log_group.api.name} --follow"
    health_check = "curl http://${aws_lb.main.dns_name}/health"
  }
  sensitive = true
}
