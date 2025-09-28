# AWS Deployment Guide for Church Course Tracker

This guide provides step-by-step instructions for deploying the Church Course Tracker application to AWS.

## 🏗️ Architecture Overview

The application is deployed using the following AWS services:

- **Frontend**: S3 + CloudFront (Static website hosting)
- **Backend**: ECS Fargate (Containerized FastAPI)
- **Database**: RDS PostgreSQL (Managed database)
- **File Storage**: S3 (Course content and uploads)
- **CDN**: CloudFront (Global content delivery)
- **Load Balancer**: Application Load Balancer (ALB)
- **Monitoring**: CloudWatch (Logs, metrics, and alarms)

## 📋 Prerequisites

### Required Tools
- [AWS CLI](https://aws.amazon.com/cli/) (v2.0+)
- [Terraform](https://www.terraform.io/downloads.html) (v1.0+)
- [Docker](https://www.docker.com/get-started)
- [Node.js](https://nodejs.org/) (v18+)
- [Python](https://www.python.org/) (v3.12+)

### AWS Account Setup
1. Create an AWS account
2. Set up billing alerts
3. Configure IAM user with appropriate permissions
4. Install and configure AWS CLI

## 🚀 Deployment Steps

### Step 1: Infrastructure Setup

1. **Clone the repository and navigate to the project directory:**
   ```bash
   git clone <repository-url>
   cd church-course-tracker
   ```

2. **Configure AWS credentials:**
   ```bash
   aws configure
   ```

3. **Set up infrastructure:**
   ```bash
   ./scripts/setup-infrastructure.sh
   ```

4. **Edit terraform.tfvars with your values:**
   ```bash
   cd infrastructure
   cp terraform.tfvars.example terraform.tfvars
   # Edit terraform.tfvars with your configuration
   ```

### Step 2: Database Migration

1. **Run database migration script:**
   ```bash
   ./scripts/migrate-database.sh
   ```

2. **Verify database connection:**
   ```bash
   # Test connection to RDS instance
   psql -h <rds-endpoint> -p 5432 -U postgres -d church_course_tracker
   ```

### Step 3: Application Deployment

1. **Deploy the application:**
   ```bash
   ./scripts/deploy-aws.sh
   ```

2. **Verify deployment:**
   ```bash
   # Check ECS service status
   aws ecs describe-services --cluster church-course-tracker-cluster --services church-course-tracker-service
   
   # Check application health
   curl https://your-domain.com/health
   ```

## 🔧 Configuration

### Environment Variables

The application uses the following environment variables:

#### Backend (ECS Task Definition)
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `PLANNING_CENTER_APP_ID`: Planning Center API app ID
- `PLANNING_CENTER_SECRET`: Planning Center API secret
- `AWS_S3_BUCKET`: S3 bucket for file uploads
- `AWS_REGION`: AWS region

#### Frontend (Build-time)
- `API_URL`: Backend API URL
- `ENVIRONMENT`: Production environment flag

### Secrets Management

Sensitive configuration is stored in AWS Secrets Manager:

```bash
# Update secrets
aws secretsmanager update-secret \
  --secret-id church-course-tracker-secrets \
  --secret-string '{"SECRET_KEY":"your-new-secret-key"}'
```

## 📊 Monitoring and Logging

### CloudWatch Dashboard
Access the monitoring dashboard at:
```
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=church-course-tracker-dashboard
```

### Key Metrics
- **ECS Service**: CPU and memory utilization
- **Application Load Balancer**: Response time, request count, error rates
- **RDS Database**: CPU, connections, storage
- **S3**: Storage usage and request metrics

### Logs
- **Application Logs**: `/ecs/church-course-tracker-backend`
- **ALB Logs**: `/aws/applicationloadbalancer/church-course-tracker`
- **Database Logs**: RDS logs in CloudWatch

## 🔒 Security Considerations

### Network Security
- VPC with private and public subnets
- Security groups restricting access
- ALB with SSL/TLS termination
- CloudFront with HTTPS enforcement

### Data Security
- RDS encryption at rest
- S3 server-side encryption
- Secrets Manager for sensitive data
- IAM roles with least privilege

### Application Security
- JWT-based authentication
- Role-based access control
- Input validation and sanitization
- CORS configuration

## 💰 Cost Optimization

### Estimated Monthly Costs
- **RDS PostgreSQL (db.t3.micro)**: ~$15
- **ECS Fargate (0.5 vCPU, 1GB RAM)**: ~$8
- **Application Load Balancer**: ~$18
- **S3 Storage (10GB)**: ~$2
- **CloudFront (100GB transfer)**: ~$8
- **Data Transfer**: ~$5
- **Total**: ~$57/month

### Cost Optimization Tips
1. **Reserved Instances**: Save 30-50% on RDS with 1-year commitment
2. **S3 Intelligent Tiering**: Automatic cost optimization
3. **CloudWatch**: Monitor and optimize resource usage
4. **Auto Scaling**: Scale down during low usage periods

## 🚨 Troubleshooting

### Common Issues

#### ECS Service Won't Start
```bash
# Check service events
aws ecs describe-services --cluster church-course-tracker-cluster --services church-course-tracker-service

# Check task definition
aws ecs describe-task-definition --task-definition church-course-tracker-backend
```

#### Database Connection Issues
```bash
# Test database connectivity
aws rds describe-db-instances --db-instance-identifier church-course-tracker-db

# Check security groups
aws ec2 describe-security-groups --group-ids <security-group-id>
```

#### Frontend Not Loading
```bash
# Check S3 bucket
aws s3 ls s3://church-course-tracker-static

# Check CloudFront distribution
aws cloudfront get-distribution --id <distribution-id>
```

### Health Checks

#### Application Health
```bash
# Backend health
curl https://api.your-domain.com/health

# Frontend
curl https://your-domain.com
```

#### Infrastructure Health
```bash
# ECS service status
aws ecs describe-services --cluster church-course-tracker-cluster --services church-course-tracker-service --query 'services[0].deployments[0].status'

# RDS status
aws rds describe-db-instances --db-instance-identifier church-course-tracker-db --query 'DBInstances[0].DBInstanceStatus'
```

## 🔄 Updates and Maintenance

### Application Updates
1. **Code changes**: Push to main branch triggers automatic deployment
2. **Database migrations**: Run via ECS exec command
3. **Configuration changes**: Update via AWS Secrets Manager

### Infrastructure Updates
1. **Terraform changes**: Update infrastructure code and apply
2. **Security updates**: Regular security group and IAM policy reviews
3. **Monitoring**: Regular review of CloudWatch metrics and alarms

## 📞 Support

For deployment issues:
1. Check CloudWatch logs for error messages
2. Verify all environment variables are set correctly
3. Ensure all AWS services are in the same region
4. Check IAM permissions for all services

## 🔗 Useful Links

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Angular Deployment](https://angular.io/guide/deployment)
