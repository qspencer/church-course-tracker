# Documentation Site Deployment Guide

This guide explains how to deploy the documentation site to AWS and set up CI/CD.

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **Terraform** installed (for infrastructure setup)
3. **AWS CLI** configured with credentials
4. **GitHub Actions** access (for CI/CD)

## Step 1: Set Up AWS Infrastructure

### Option A: Using Terraform (Recommended)

1. **Navigate to infrastructure directory:**
   ```bash
   cd infrastructure
   ```

2. **Update `terraform.tfvars`** (or create it from `terraform.tfvars.example`):
   ```hcl
   docs_certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/your-cert-id"
   # Or leave empty to create a new certificate
   ```

3. **Initialize and apply Terraform:**
   ```bash
   terraform init
   terraform plan
   terraform apply
   ```

4. **Get the outputs:**
   ```bash
   terraform output docs_s3_bucket
   terraform output docs_cloudfront_distribution_id
   ```

### Option B: Manual Setup

If you prefer to set up resources manually:

1. **Create S3 Bucket:**
   - Name: `docs.quentinspencer.com`
   - Block all public access
   - Enable versioning

2. **Create CloudFront Distribution:**
   - Origin: S3 bucket (with OAI)
   - Domain: `docs.quentinspencer.com`
   - SSL Certificate: ACM certificate for `docs.quentinspencer.com`
   - Default root object: `index.html`

3. **Create Route 53 Record:**
   - Type: A (Alias)
   - Name: `docs.quentinspencer.com`
   - Alias to: CloudFront distribution

## Step 2: Configure GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

1. **`AWS_DEPLOY_ROLE_ARN`** (Required for OIDC)
   - ARN of IAM role with deployment permissions
   - Must trust GitHub OIDC provider

2. **`DOCS_S3_BUCKET`** (Optional)
   - Default: `docs.quentinspencer.com`
   - S3 bucket name for documentation

3. **`DOCS_CLOUDFRONT_DIST_ID`** (Optional)
   - CloudFront distribution ID
   - Will be auto-detected if not provided

## Step 3: Set Up IAM Role for GitHub Actions

Create an IAM role that GitHub Actions can assume:

1. **Create IAM Role:**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
         },
         "Action": "sts:AssumeRoleWithWebIdentity",
         "Condition": {
           "StringEquals": {
             "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
           },
           "StringLike": {
             "token.actions.githubusercontent.com:sub": "repo:qspencer/church-course-tracker:*"
           }
         }
       }
     ]
   }
   ```

2. **Attach Policies:**
   - `AmazonS3FullAccess` (or custom policy for docs bucket only)
   - `CloudFrontFullAccess` (or custom policy for docs distribution only)

3. **Add Trust Relationship:**
   - Trust GitHub OIDC provider: `token.actions.githubusercontent.com`

## Step 4: Manual Deployment (Testing)

Before setting up CI/CD, test manual deployment:

```bash
cd docs-site

# Set environment variables
export DOCS_S3_BUCKET="docs.quentinspencer.com"
export DOCS_CLOUDFRONT_DIST_ID="your-distribution-id"

# Deploy
./scripts/deploy.sh
```

## Step 5: CI/CD Setup

The GitHub Actions workflow (`.github/workflows/deploy-docs.yml`) will automatically:

1. **Trigger on:**
   - Pushes to `main` branch that modify `docs-site/**`
   - Manual workflow dispatch

2. **Build:**
   - Install Python dependencies
   - Build MkDocs site

3. **Deploy:**
   - Upload to S3
   - Set appropriate cache headers
   - Invalidate CloudFront cache

## Step 6: Verify Deployment

After deployment:

1. **Check S3 bucket:**
   ```bash
   aws s3 ls s3://docs.quentinspencer.com/churchcoursetracker/
   ```

2. **Test the site:**
   - Visit: https://docs.quentinspencer.com/churchcoursetracker/
   - Verify all pages load
   - Test navigation
   - Check search functionality

3. **Monitor CloudFront:**
   - Check invalidation status in AWS Console
   - Verify cache headers

## Troubleshooting

### Deployment Fails

- **Check AWS credentials:** `aws sts get-caller-identity`
- **Verify S3 bucket exists:** `aws s3 ls s3://docs.quentinspencer.com`
- **Check IAM permissions:** Ensure role has S3 and CloudFront access

### CloudFront Not Updating

- **Check invalidation status:** AWS Console → CloudFront → Invalidations
- **Wait 5-15 minutes:** Invalidations take time to propagate
- **Clear browser cache:** Hard refresh (Ctrl+Shift+R)

### 404 Errors

- **Verify path prefix:** Files should be in `churchcoursetracker/` subdirectory
- **Check S3 structure:** `aws s3 ls s3://docs.quentinspencer.com/churchcoursetracker/`
- **Verify CloudFront origin path:** Should point to S3 bucket root

## Cost Estimation

- **S3 Storage:** ~$0.023/GB/month (minimal for documentation)
- **S3 Requests:** ~$0.005 per 1,000 requests
- **CloudFront:** ~$0.085/GB for first 10TB (free tier: 1TB/month)
- **Route 53:** ~$0.50/hosted zone/month

**Estimated monthly cost:** < $5 for typical documentation traffic

## Maintenance

- **Update documentation:** Just push changes to `docs-site/`, CI/CD handles deployment
- **Monitor usage:** Check CloudWatch metrics for CloudFront
- **Review costs:** AWS Cost Explorer
- **Update screenshots:** Run `./scripts/capture-screenshots.sh` and commit

## Security

- **S3 bucket:** Private (only CloudFront can access via OAI)
- **CloudFront:** HTTPS only (redirects HTTP to HTTPS)
- **IAM:** Least privilege (only S3 and CloudFront permissions needed)
- **OIDC:** Secure authentication without long-lived credentials

