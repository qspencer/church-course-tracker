# AWS Deployment Guide for Church Course Tracker

This guide provides step-by-step instructions for deploying the Church Course Tracker application to AWS.

## 🏗️ Architecture Overview

The application is deployed using the following AWS services:

- **Frontend**: S3 + CloudFront (Static website hosting)
- **Backend**: ECS Fargate (Containerized FastAPI)
- **Database**: RDS PostgreSQL (Managed database)
- **File Storage**: S3 (Course content and uploads)
- **CDN**: CloudFront (Global content delivery)
- **API Gateway**: HTTP API with VPC Link (replacing ALB for cost optimization)
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

⚠️ **CRITICAL**: Database migration issues are the most common cause of deployment failures. Follow these steps carefully.

1. **Verify database credentials and connectivity:**
   ```bash
   # Get database credentials from AWS Secrets Manager
   aws secretsmanager get-secret-value --secret-id church-course-tracker-db-password --query 'SecretString' --output text
   
   # Test connection to RDS instance
   psql -h <rds-endpoint> -p 5432 -U postgres -d church_course_tracker
   ```

2. **Check for migration conflicts:**
   ```bash
   # Connect to database and check alembic version table
   psql -h <rds-endpoint> -p 5432 -U postgres -d church_course_tracker -c "SELECT * FROM alembic_version;"
   ```

3. **If migration conflicts exist (multiple heads), use the database fix script:**
   ```bash
   # This script will reset the database completely and create a clean schema
   python3 fix_database_docker.py
   ```

4. **Verify database schema:**
   ```bash
   # Check that all required tables exist
   psql -h <rds-endpoint> -p 5432 -U postgres -d church_course_tracker -c "\dt"
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
   
   # Check application health via API Gateway
   curl https://tinev5iszf.execute-api.us-east-1.amazonaws.com/health
   
   # Check application logs for any errors
   aws logs tail /ecs/church-course-tracker-backend --follow --region us-east-1
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
- **API Gateway HTTP API**: ~$3 (replaces ALB for significant cost savings)
- **S3 Storage (10GB)**: ~$2
- **CloudFront (100GB transfer)**: ~$8
- **Data Transfer**: ~$5
- **Total**: ~$41/month (savings of ~$16/month vs ALB)

### Cost Optimization Tips
1. **Reserved Instances**: Save 30-50% on RDS with 1-year commitment
2. **S3 Intelligent Tiering**: Automatic cost optimization
3. **CloudWatch**: Monitor and optimize resource usage
4. **Auto Scaling**: Scale down during low usage periods

## 🚨 Troubleshooting

### Common Issues

#### 503/504 Gateway Errors (Most Common Issue)

**Symptoms:**
- API returns 503 Service Temporarily Unavailable or 504 Gateway Timeout
- Application logs show "relation 'users' does not exist"
- Migration logs show "corrupted migration history"

**Root Cause:** Database migration conflicts or missing schema

**Solution:**
```bash
# 1. Check application logs for specific errors
aws logs tail /ecs/church-course-tracker-backend --follow --region us-east-1

# 2. If you see migration errors, check database schema
aws rds describe-db-instances --db-instance-identifier church-course-tracker-db --query 'DBInstances[0].Endpoint.Address' --output text

# 3. Connect to database and check for missing tables
psql -h <rds-endpoint> -p 5432 -U postgres -d church_course_tracker -c "\dt"

# 4. If tables are missing, run the database fix script
python3 fix_database_docker.py

# 5. Or deploy the fix via ECS (recommended for production)
# Build and push the fix image
docker build -f Dockerfile.fix-and-start -t fix-and-start:latest .
docker tag fix-and-start:latest 334581603621.dkr.ecr.us-east-1.amazonaws.com/church-course-tracker:fix-and-start
docker push 334581603621.dkr.ecr.us-east-1.amazonaws.com/church-course-tracker:fix-and-start

# Update ECS service to use the fix image
aws ecs update-service --cluster church-course-tracker-cluster --service church-course-tracker-service --task-definition <new-task-definition> --force-new-deployment
```

#### ECS Service Won't Start

**Symptoms:**
- Service shows no running tasks
- Service events show "failed to assume role" errors

**Solution:**
```bash
# Check service events for specific errors
aws ecs describe-services --cluster church-course-tracker-cluster --services church-course-tracker-service --query 'services[0].events[0:3].[createdAt,message]' --output table

# Verify IAM roles exist and are correctly named
aws iam list-roles --query 'Roles[?contains(RoleName, `ecs`)].{RoleName:RoleName,Arn:Arn}' --output table

# Check task definition for correct role ARNs
aws ecs describe-task-definition --task-definition church-course-tracker-backend --query 'taskDefinition.{ExecutionRoleArn:executionRoleArn,TaskRoleArn:taskRoleArn}' --output table
```

#### Database Connection Issues

**Symptoms:**
- "connection timed out" errors
- "password authentication failed" errors
- "no pg_hba.conf entry" errors

**Solution:**
```bash
# 1. Verify database credentials
aws secretsmanager get-secret-value --secret-id church-course-tracker-db-password --query 'SecretString' --output text

# 2. Check database is using correct user (should be 'postgres', not 'church_course_tracker')
aws rds describe-db-instances --db-instance-identifier church-course-tracker-db --query 'DBInstances[0].{MasterUsername:MasterUsername,Endpoint:Endpoint.Address}' --output table

# 3. Verify security groups allow connections
aws ec2 describe-security-groups --group-ids <db-security-group-id> --query 'SecurityGroups[0].IpPermissions[*].{FromPort:FromPort,ToPort:ToPort,UserIdGroupPairs:UserIdGroupPairs[*].GroupId}' --output table

# 4. Test connectivity from ECS subnet
aws ec2 describe-subnets --subnet-ids <ecs-subnet-id> --query 'Subnets[0].{AvailabilityZone:AvailabilityZone,CidrBlock:CidrBlock}' --output table
```

#### Migration Conflicts (Multiple Heads)

**Symptoms:**
- "Multiple heads detected" error in alembic
- "corrupted migration history" in application logs

**Solution:**
```bash
# 1. Check current migration state
psql -h <rds-endpoint> -p 5432 -U postgres -d church_course_tracker -c "SELECT * FROM alembic_version;"

# 2. If multiple versions exist, reset completely
python3 fix_migrations_comprehensive.py

# 3. Or manually reset the database
psql -h <rds-endpoint> -p 5432 -U postgres -d church_course_tracker -c "DROP TABLE IF EXISTS alembic_version CASCADE; DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
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

## 🛠️ Database Fix Scripts

### Emergency Database Reset Script

If you encounter database migration conflicts or corrupted schema, use the provided fix scripts:

#### `fix_database_docker.py`
Complete database reset script that:
- Drops all existing tables
- Creates a clean schema with all required tables
- Sets up alembic version tracking
- Creates the admin user with default credentials

**Usage:**
```bash
# Run locally (requires database access)
python3 fix_database_docker.py

# Or deploy via ECS for production use
docker build -f Dockerfile.fix-and-start -t fix-and-start:latest .
# ... (see ECS deployment steps above)
```

#### `fix_and_start.py`
Combined script that fixes the database and then starts the application.

#### `fix_migrations_comprehensive.py`
Handles alembic migration conflicts by resetting migration history.

### Admin User Credentials

After running the database fix, the default admin user is created with:
- **Email:** `course.tracker.admin@eastgate.church`
- **Username:** `admin`
- **Password:** `Matthew778*`

⚠️ **Security Note:** Change these credentials immediately after deployment!

## 🔄 Updates and Maintenance

### Application Updates
1. **Code changes**: Push to main branch triggers automatic deployment
2. **Database migrations**: Run via ECS exec command or use fix scripts if conflicts occur
3. **Configuration changes**: Update via AWS Secrets Manager

### Infrastructure Updates
1. **Terraform changes**: Update infrastructure code and apply
2. **Security updates**: Regular security group and IAM policy reviews
3. **Monitoring**: Regular review of CloudWatch metrics and alarms

## 🚀 Quick Reference

### Most Common Deployment Issues

| Issue | Symptoms | Quick Fix |
|-------|----------|-----------|
| **503/504 Errors** | API returns service unavailable | Run `python3 fix_database_docker.py` |
| **ECS Won't Start** | No running tasks, IAM errors | Check task definition role ARNs |
| **DB Connection Failed** | Timeout or auth errors | Verify security groups and credentials |
| **Migration Conflicts** | Multiple heads error | Reset database schema completely |

### Essential Commands

```bash
# Check application status
aws ecs describe-services --cluster church-course-tracker-cluster --services church-course-tracker-service --query 'services[0].{RunningCount:runningCount,DesiredCount:desiredCount,TaskDefinition:taskDefinition}' --output table

# View application logs
aws logs tail /ecs/church-course-tracker-backend --follow --region us-east-1

# Test API endpoint
curl -s -o /dev/null -w "%{http_code}" https://tinev5iszf.execute-api.us-east-1.amazonaws.com/health

# Reset database (emergency)
python3 fix_database_docker.py
```

## 📞 Support

For deployment issues:
1. Check CloudWatch logs for error messages
2. Verify all environment variables are set correctly
3. Ensure all AWS services are in the same region
4. Check IAM permissions for all services
5. **Most importantly**: Check for database migration issues first - they cause 90% of deployment failures

## 🔗 Useful Links

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Angular Deployment](https://angular.io/guide/deployment)
