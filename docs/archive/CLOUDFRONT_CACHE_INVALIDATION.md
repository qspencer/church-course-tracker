# CloudFront Cache Invalidation Guide

## Overview
CloudFront caches content at edge locations to improve performance. When you deploy new frontend builds, you need to invalidate the cache so users get the latest version.

## Quick Invalidation (Recommended)

### Method 1: AWS CLI (Fastest)
```bash
# Find your CloudFront distribution ID
CLOUDFRONT_ID=$(aws cloudfront list-distributions \
  --query "DistributionList.Items[?contains(Origins.Items[0].DomainName, 'church-course-tracker-static')].Id" \
  --output text)

# Create invalidation for all files
aws cloudfront create-invalidation \
  --distribution-id $CLOUDFRONT_ID \
  --paths "/*"
```

**Output**: Returns an invalidation ID (e.g., `I7Y0AV86R8P7JJSFYLPE13JN1Z`)

**Status**: Usually completes in 1-5 minutes (can take up to 15 minutes)

### Method 2: AWS Console (Manual)

1. **Log in to AWS Management Console**
   - Navigate to: https://console.aws.amazon.com/cloudfront/

2. **Select Your Distribution**
   - Find the distribution for your frontend (look for S3 bucket origin)
   - Distribution ID format: `E1KF8RVKW7M0VB` (alphanumeric)

3. **Go to Invalidations Tab**
   - Click on the distribution
   - Click the **"Invalidations"** tab

4. **Create Invalidation**
   - Click **"Create Invalidation"** button
   - In the **"Object paths"** field, enter:
     - `/*` (to invalidate all files)
     - Or specific paths like `/index.html`, `/main.*.js` (for specific files)

5. **Submit**
   - Click **"Invalidate"**
   - The invalidation will appear in the list with status "InProgress"

6. **Wait for Completion**
   - Status changes from "InProgress" to "Completed"
   - Usually takes 1-5 minutes, can take up to 15 minutes

## Checking Invalidation Status

### AWS CLI
```bash
# Check status of a specific invalidation
aws cloudfront get-invalidation \
  --distribution-id <DISTRIBUTION_ID> \
  --id <INVALIDATION_ID>

# List recent invalidations
aws cloudfront list-invalidations \
  --distribution-id <DISTRIBUTION_ID>
```

### AWS Console
1. Go to CloudFront console
2. Select your distribution
3. Click "Invalidations" tab
4. View status in the list:
   - **InProgress**: Still processing
   - **Completed**: Cache cleared successfully

## Finding Your Distribution ID

### From Terraform
```bash
cd infrastructure
terraform output cloudfront_distribution_id
```

### From AWS CLI
```bash
# List all distributions
aws cloudfront list-distributions \
  --query "DistributionList.Items[*].[Id,Comment,Origins.Items[0].DomainName]" \
  --output table

# Find specific distribution
aws cloudfront list-distributions \
  --query "DistributionList.Items[?contains(Origins.Items[0].DomainName, 'church-course-tracker-static')].Id" \
  --output text
```

### From AWS Console
1. Go to CloudFront console
2. Distribution ID is shown in the list (first column)

## Common Path Patterns

- `/*` - Invalidate all files (most common)
- `/index.html` - Invalidate just the index file
- `/main.*.js` - Invalidate all main.js files (with hash)
- `/assets/*` - Invalidate all files in assets folder
- `/main.*.js` `/styles.*.css` - Multiple specific patterns

## When to Invalidate

### Always Invalidate After:
- ✅ Frontend deployment (new build)
- ✅ Environment configuration changes
- ✅ New feature releases
- ✅ Bug fixes deployed

### May Not Need Invalidation:
- ⚠️ Backend-only changes (API changes)
- ⚠️ Database changes (no frontend impact)

## Invalidation Costs

**Free Tier**: 
- First 1,000 paths per month: **FREE**

**After Free Tier**:
- $0.005 per path after the first 1,000 paths per month

**Note**: Using `/*` counts as 1 path, not per-file

## Best Practices

1. **Use `/*` for Full Deployments**
   - Simple and ensures everything is fresh
   - Only counts as 1 path (cost-effective)

2. **Specific Paths for Quick Fixes**
   - If you only changed one file, invalidate just that path
   - Faster and cheaper if you're over the free tier

3. **Wait for Completion**
   - Don't immediately redeploy if invalidation is in progress
   - Wait for "Completed" status

4. **Automate in CI/CD**
   - Include cache invalidation in deployment scripts
   - Reduces manual steps

## Troubleshooting

### Invalidation Takes Too Long
- **Normal**: 1-5 minutes
- **Long**: Up to 15 minutes is normal
- **Very Long**: If > 15 minutes, check AWS status page

### Cache Not Clearing
- Verify invalidation status is "Completed"
- Clear browser cache (Ctrl+Shift+R)
- Try a different browser or incognito mode
- Check if you're using the correct distribution ID

### Distribution ID Not Found
- Verify you're in the correct AWS region
- Check CloudFront console for active distributions
- Ensure distribution is not disabled

## Example: Full Deployment Workflow

```bash
# 1. Build frontend
cd frontend/church-course-tracker
npm run build -- --configuration=production

# 2. Deploy to S3
cd ../../infrastructure
S3_BUCKET=$(terraform output -raw s3_static_bucket)
cd ..
aws s3 sync frontend/church-course-tracker/dist/church-course-tracker/ \
  s3://$S3_BUCKET --delete

# 3. Invalidate CloudFront cache
CLOUDFRONT_ID=$(aws cloudfront list-distributions \
  --query "DistributionList.Items[?contains(Origins.Items[0].DomainName, 'church-course-tracker-static')].Id" \
  --output text)

INVALIDATION_ID=$(aws cloudfront create-invalidation \
  --distribution-id $CLOUDFRONT_ID \
  --paths "/*" \
  --query 'Invalidation.Id' \
  --output text)

echo "Invalidation created: $INVALIDATION_ID"
echo "Status: InProgress (wait 5-15 minutes)"
```

## Verification

After invalidation completes:

1. **Hard Refresh Browser**
   - Chrome/Edge: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
   - Firefox: `Ctrl+F5`
   - Safari: `Cmd+Option+R`

2. **Check Version**
   - Open DevTools > Network tab
   - Reload page
   - Check file hashes in loaded JS/CSS files
   - Should match new build hash

3. **Test Functionality**
   - Verify new features work
   - Check for any console errors
   - Test critical user flows

## Related Documentation

- [Frontend Deployment Fix](./FRONTEND_DEPLOYMENT_FIX.md)
- [Mixed Content Error Analysis](./MIXED_CONTENT_ERROR_ANALYSIS.md)
- [Auth Error Handling Improvements](./AUTH_ERROR_HANDLING_IMPROVEMENTS.md)


