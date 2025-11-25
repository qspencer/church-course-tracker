# Documentation Deployment Monitoring

## Automatic Deployment Script

The `wait-and-deploy-docs.sh` script is now running and will:

1. ✅ Check certificate status every 30 seconds
2. ⏳ Wait for ACM certificate to become `ISSUED`
3. 🚀 Automatically run `terraform apply` once validated
4. 📋 Display deployment summary when complete

## Monitor Progress

### Option 1: View the Log File (Recommended)

```bash
cd infrastructure
tail -f wait-and-deploy-docs.log
```

Press `Ctrl+C` to stop following the log.

### Option 2: Quick Status Check

```bash
cd infrastructure
./check-cert-status.sh
```

### Option 3: Check the Process

```bash
ps aux | grep wait-and-deploy-docs
```

### Option 4: View Recent Log Output

```bash
cd infrastructure
tail -20 wait-and-deploy-docs.log
```

## Expected Timeline

- **Certificate Validation**: 5-45 minutes (usually completes within 15 minutes)
- **Terraform Apply**: ~5-10 minutes (creates CloudFront + Route 53)
- **CloudFront Deployment**: 10-15 minutes (after Terraform completes)
- **DNS Propagation**: 5-60 minutes

**Total**: ~30-120 minutes from script start

## What Happens Next

Once the certificate validates (`ISSUED` status), the script will:

1. Run `terraform apply -auto-approve`
2. Create:
   - CloudFront distribution for `docs.quentinspencer.com`
   - Route 53 A record pointing to CloudFront
   - Certificate validation resource (completes)
3. Display deployment outputs:
   - S3 Bucket name
   - CloudFront Distribution ID
   - CloudFront Domain
   - Documentation URL

## Check Certificate Status Manually

If you want to check manually:

```bash
aws acm describe-certificate \
  --certificate-arn arn:aws:acm:us-east-1:334581603621:certificate/78e18b2c-69c8-4e4a-b8c6-e35e5d865b70 \
  --region us-east-1 \
  --query 'Certificate.Status' \
  --output text
```

Expected values:
- `PENDING_VALIDATION` - Still waiting (normal)
- `ISSUED` - Ready for deployment
- `FAILED` - Validation failed (check DNS records)
- `VALIDATION_TIMED_OUT` - DNS didn't propagate in time

## If Script Fails

If the script stops or encounters an error:

1. Check the log: `tail -50 infrastructure/wait-and-deploy-docs.log`
2. Check certificate status: `./check-cert-status.sh`
3. If certificate is `ISSUED`, run manually:
   ```bash
   cd infrastructure
   terraform apply -auto-approve
   ```

## Stop the Monitoring Script

If you need to stop the script:

```bash
pkill -f wait-and-deploy-docs.sh
```

Then you can check status manually or restart it.

## After Deployment Completes

Once Terraform apply succeeds:

1. **CloudFront will be deploying** (10-15 minutes)
   - Check status: `aws cloudfront get-distribution --id <DIST_ID> --query 'Distribution.Status' --output text`

2. **Deploy documentation content**:
   ```bash
   cd docs-site
   export DOCS_S3_BUCKET="docs.quentinspencer.com"
   export DOCS_CLOUDFRONT_DIST_ID="<from terraform output>"
   ./scripts/deploy.sh
   ```

3. **Test the site**:
   - Wait for CloudFront to deploy
   - Visit: `https://docs.quentinspencer.com/churchcoursetracker/`


