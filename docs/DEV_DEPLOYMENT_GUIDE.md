# 🚀 Development Deployment Guide for apps.eastgate.church

This guide will help you deploy the Church Course Tracker to AWS for development using the domain `apps.eastgate.church`.

## 📋 **Prerequisites**

Before starting, you need:

1. **AWS Account** with billing enabled
2. **Domain Access** to `apps.eastgate.church` (for DNS configuration)
3. **Required Tools** (we'll install these)

## 🔧 **Step 1: Install Prerequisites**

Run the prerequisites installation script:

```bash
sudo ./scripts/install-prerequisites.sh
```

This will install:
- AWS CLI
- Terraform
- Docker
- Node.js
- Python dependencies

## 🔐 **Step 2: Configure AWS CLI**

Configure your AWS credentials:

```bash
aws configure
```

You'll need:
- **AWS Access Key ID**: Your AWS access key
- **AWS Secret Access Key**: Your AWS secret key
- **Default region**: `us-east-1`
- **Default output format**: `json`

## 🚀 **Step 3: Deploy Infrastructure**

Run the development deployment setup:

```bash
./scripts/setup-dev-deployment.sh
```

This will:
- Create Terraform configuration for `apps.eastgate.church`
- Deploy AWS infrastructure (VPC, RDS, ECS, ALB, S3, CloudFront)
- Configure cost-optimized settings for development
- Set up SSL certificate via AWS Certificate Manager

**Estimated Cost**: ~$45-55/month (within your $75 budget)

## 📦 **Step 4: Deploy Application**

Deploy the application to AWS:

```bash
./scripts/deploy-dev-application.sh
```

This will:
- Build and push Docker images to ECR
- Deploy frontend to S3
- Update ECS service
- Run database migrations
- Create default admin user

## 🌐 **Step 5: Configure DNS**

Update your DNS settings to point `apps.eastgate.church` to the CloudFront distribution:

1. Get the CloudFront domain from the deployment output
2. Create a CNAME record in your DNS:
   - **Name**: `apps.eastgate.church`
   - **Type**: `CNAME`
   - **Value**: `<cloudfront-domain>`

## 🔐 **Step 6: Access Your Application**

Once DNS propagates (5-15 minutes), access your application:

- **Frontend**: https://apps.eastgate.church
- **API**: https://api.apps.eastgate.church

**Default Admin Credentials:**
- Username: `Admin`
- Email: `course.tracker.admin@eastgate.church`
- Password: `Matthew778*`

## 📊 **Monitoring**

Access your monitoring dashboard:
- **CloudWatch Dashboard**: https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=church-course-tracker-dashboard

## 💰 **Cost Breakdown**

| Service | Monthly Cost |
|---------|--------------|
| RDS PostgreSQL (db.t3.micro) | ~$15 |
| ECS Fargate (1-3 tasks) | ~$8-15 |
| Application Load Balancer | ~$18 |
| S3 Storage (5GB) | ~$1 |
| CloudFront (50GB transfer) | ~$4 |
| Route 53 (hosted zone) | ~$0.50 |
| Data Transfer | ~$2 |
| **Total** | **~$45-55** |

## 🔧 **Development Features**

This development deployment includes:

- **Mock Planning Center API**: No real credentials needed
- **Cost Optimization**: Minimal resources for development
- **Auto-scaling**: 1-3 ECS tasks based on demand
- **SSL/TLS**: Automatic HTTPS via CloudFront
- **Monitoring**: Basic CloudWatch dashboards
- **Backups**: 3-day RDS backup retention

## 🚨 **Troubleshooting**

### **Common Issues:**

1. **DNS not working**: Wait 5-15 minutes for propagation
2. **Application not loading**: Check ECS service status in AWS console
3. **Database connection issues**: Verify RDS security groups
4. **High costs**: Check CloudWatch metrics for resource usage

### **Health Checks:**

```bash
# Check application health
curl https://apps.eastgate.church/health

# Check API health
curl https://api.apps.eastgate.church/health
```

## 🔄 **Updates and Maintenance**

### **Application Updates:**
```bash
# Deploy updates
./scripts/deploy-dev-application.sh
```

### **Infrastructure Updates:**
```bash
cd infrastructure
terraform plan
terraform apply
```

### **Cost Monitoring:**
- Check AWS Cost Explorer
- Set up billing alerts
- Monitor CloudWatch metrics

## 🎯 **Next Steps**

1. **Test the application** with mock data
2. **Configure Planning Center API** when ready
3. **Set up monitoring alerts** for production
4. **Plan production deployment** with higher availability

## 📞 **Support**

If you encounter issues:

1. Check the deployment logs
2. Verify AWS service status
3. Review CloudWatch logs
4. Check DNS propagation

## 🎉 **Success!**

Your Church Course Tracker is now running on AWS at:
- **Frontend**: https://apps.eastgate.church
- **API**: https://api.apps.eastgate.church

The application is ready for development and testing with mock Planning Center data!
