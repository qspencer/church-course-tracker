# Documentation Site Setup Summary

## ✅ What Has Been Created

### 1. Infrastructure (Terraform)
- **File:** `infrastructure/docs.tf`
- **Resources:**
  - S3 bucket: `docs.quentinspencer.com`
  - CloudFront distribution with custom domain
  - Origin Access Identity (OAI) for secure S3 access
  - Route 53 A record for `docs.quentinspencer.com`
  - ACM certificate (optional, can use existing)
  - Cache policies (optimized for static assets)
  - Security headers policy

### 2. CI/CD Workflow
- **File:** `.github/workflows/deploy-docs.yml`
- **Features:**
  - Auto-deploys on pushes to `docs-site/**`
  - Manual trigger option
  - Builds MkDocs site
  - Deploys to S3 with proper cache headers
  - Invalidates CloudFront cache
  - Uses OIDC for secure AWS authentication

### 3. Deployment Script
- **File:** `docs-site/scripts/deploy.sh`
- **Updated:** Better error handling and validation

### 4. Documentation
- **File:** `docs-site/DEPLOYMENT.md`
- **Content:** Complete deployment guide

## 🚀 Next Steps

### Step 1: Set Up AWS Infrastructure

```bash
cd infrastructure

# Add docs_certificate_arn to terraform.tfvars (optional)
# Or leave empty to create a new certificate

terraform init
terraform plan  # Review changes
terraform apply  # Create resources
```

**Note:** If you already have an ACM certificate for `docs.quentinspencer.com`, add it to `terraform.tfvars`:
```hcl
docs_certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/your-cert-id"
```

### Step 2: Get Infrastructure Outputs

After Terraform applies successfully:

```bash
terraform output docs_s3_bucket
terraform output docs_cloudfront_distribution_id
```

Save these values for GitHub secrets.

### Step 3: Set Up GitHub OIDC

1. **Create IAM Role** (see `DEPLOYMENT.md` for details)
2. **Add GitHub Secret:**
   - Go to: Repository Settings → Secrets and variables → Actions
   - Add: `AWS_DEPLOY_ROLE_ARN` = Your IAM role ARN

3. **Optional Secrets:**
   - `DOCS_S3_BUCKET` (defaults to `docs.quentinspencer.com`)
   - `DOCS_CLOUDFRONT_DIST_ID` (auto-detected if not set)

### Step 4: Test Manual Deployment

Before relying on CI/CD, test manually:

```bash
cd docs-site

# Set environment variables
export DOCS_S3_BUCKET="docs.quentinspencer.com"
export DOCS_CLOUDFRONT_DIST_ID="your-distribution-id-from-terraform"

# Deploy
./scripts/deploy.sh
```

### Step 5: Verify

1. **Check S3:**
   ```bash
   aws s3 ls s3://docs.quentinspencer.com/churchcoursetracker/
   ```

2. **Visit site:**
   - https://docs.quentinspencer.com/churchcoursetracker/

3. **Test CI/CD:**
   - Make a small change to `docs-site/docs/`
   - Push to `main` branch
   - Check GitHub Actions tab for deployment status

## 📋 Checklist

- [ ] Terraform infrastructure created (`terraform apply`)
- [ ] S3 bucket exists and is accessible
- [ ] CloudFront distribution created
- [ ] Route 53 record created
- [ ] SSL certificate validated (if new certificate)
- [ ] IAM role for GitHub Actions created
- [ ] GitHub secrets configured
- [ ] Manual deployment tested
- [ ] CI/CD workflow tested
- [ ] Documentation site accessible at production URL

## 🔧 Troubleshooting

### Terraform Issues

- **Certificate validation:** If creating new certificate, add DNS validation records to Route 53
- **Route 53 zone:** Ensure `quentinspencer.com` zone exists in your AWS account
- **Permissions:** Ensure Terraform has permissions to create resources

### Deployment Issues

- **S3 access denied:** Check OAI is configured correctly
- **CloudFront 404:** Verify S3 path structure (`churchcoursetracker/` subdirectory)
- **GitHub Actions fails:** Check IAM role trust relationship and permissions

## 📚 Additional Resources

- **Deployment Guide:** See `docs-site/DEPLOYMENT.md`
- **Documentation Guide:** See `docs-site/docs/DOCUMENTATION_GUIDE.md`
- **Terraform Docs:** https://registry.terraform.io/providers/hashicorp/aws/latest/docs

## 💰 Cost Estimate

- **S3:** < $1/month (minimal storage)
- **CloudFront:** Free tier (1TB/month), then ~$0.085/GB
- **Route 53:** ~$0.50/month per hosted zone
- **Total:** < $5/month for typical documentation traffic

