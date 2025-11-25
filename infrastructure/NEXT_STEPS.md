# Documentation Site Deployment - Next Steps

## Current Status

✅ **Infrastructure Created**:
- S3 bucket: `docs.quentinspencer.com`
- CloudFront policies (cache, headers)
- Origin Access Identity
- ACM Certificate: **Recreated** (fresh, pending validation)

⏳ **Waiting**:
- Certificate validation (typically 10-30 minutes for new certs)

❌ **Not Yet Created** (will be created automatically once cert validates):
- CloudFront distribution
- Route 53 A record

---

## Immediate Next Steps

### Step 1: Wait for Certificate Validation ⏳ (AUTOMATIC)

**Status**: Monitoring script is actively checking every 30 seconds

**What happens automatically**:
1. Certificate validates (status changes to `ISSUED`)
2. Script detects validation
3. Runs `terraform apply` automatically
4. Creates CloudFront distribution (~10-15 minutes)
5. Creates Route 53 A record (instant)
6. Displays deployment summary

**Monitor progress**:
```bash
cd infrastructure
tail -f wait-and-deploy-docs.log
```

**Or check status**:
```bash
cd infrastructure
./check-cert-status.sh
```

**Expected time**: 10-30 minutes for new certificates (much faster than the stuck one)

---

### Step 2: Get Deployment Outputs 📋 (After Certificate Validates)

Once the automatic deployment completes, get the CloudFront Distribution ID:

```bash
cd infrastructure
terraform output docs_cloudfront_distribution_id
terraform output docs_url
```

**Note**: CloudFront distribution takes 10-15 minutes to fully deploy after creation.

---

### Step 3: Deploy Documentation Content 📦

Once CloudFront is created and deploying, build and deploy the documentation:

```bash
cd docs-site

# Build the documentation
source venv/bin/activate
mkdocs build --config-file mkdocs.yml

# Deploy to S3
export DOCS_S3_BUCKET="docs.quentinspencer.com"
export DOCS_CLOUDFRONT_DIST_ID="<from terraform output>"
./scripts/deploy.sh
```

This will:
- Build the MkDocs site
- Upload to S3 bucket
- Invalidate CloudFront cache

---

### Step 4: Verify Deployment ✅

**Wait for CloudFront deployment** (~10-15 minutes after creation):
```bash
aws cloudfront get-distribution \
  --id <DISTRIBUTION_ID> \
  --query 'Distribution.Status' \
  --output text
```

**Wait for status to be "Deployed"**, then:

1. **Test the URL**: `https://docs.quentinspencer.com/churchcoursetracker/`
2. **Check DNS propagation**: May take 5-60 minutes
3. **Verify content**: Ensure all pages load correctly
4. **Test navigation**: Check links and search functionality

---

## CI/CD Setup (After Manual Deployment Works)

### Step 5: Configure GitHub Secrets 🔐

The GitHub Actions workflow (`.github/workflows/deploy-docs.yml`) needs these secrets:

**Required Secrets**:
1. `AWS_DEPLOY_ROLE_ARN` - OIDC role ARN for AWS access
   - Create an IAM role with OIDC provider for GitHub Actions
   - Grant permissions: S3 write, CloudFront create-invalidation

2. `DOCS_CLOUDFRONT_DIST_ID` - CloudFront distribution ID
   - Get from `terraform output docs_cloudfront_distribution_id`
   - Add as GitHub repository secret

**Optional Secrets** (for screenshot capture):
3. `DOCS_USERNAME` - Username for authenticated screenshots
4. `DOCS_PASSWORD` - Password for authenticated screenshots

**Set secrets in GitHub**:
- Go to: Repository → Settings → Secrets and variables → Actions
- Add each secret

---

### Step 6: Test CI/CD Workflow 🧪

Once secrets are configured:

1. **Make a test change** to documentation:
   ```bash
   cd docs-site/docs
   # Edit a file (e.g., index.md)
   ```

2. **Commit and push**:
   ```bash
   git add docs-site/
   git commit -m "Test: CI/CD documentation deployment"
   git push origin main
   ```

3. **Watch GitHub Actions**:
   - Go to: Repository → Actions tab
   - Watch the "Deploy Documentation Site" workflow run
   - Verify it builds and deploys successfully

---

## Post-Deployment Checklist

### Content Verification ✅
- [ ] Home page loads correctly
- [ ] Getting Started guide accessible
- [ ] User Guide accessible
- [ ] Features page accessible
- [ ] Documentation Guide accessible
- [ ] Navigation works on all pages
- [ ] Search functionality works
- [ ] Links are correct (internal and external)
- [ ] Images load correctly (if any screenshots added)
- [ ] Mobile responsive design works

### Infrastructure Verification ✅
- [ ] HTTPS works (SSL certificate valid)
- [ ] CloudFront caching working
- [ ] S3 bucket not publicly accessible (CloudFront only)
- [ ] DNS resolves correctly
- [ ] Performance is good (CDN serving content)

### CI/CD Verification ✅
- [ ] GitHub Actions workflow runs on push to `docs-site/`
- [ ] Deployment completes successfully
- [ ] Content updates appear on live site
- [ ] CloudFront cache invalidation works

---

## Summary Timeline

### Right Now (Waiting):
- ⏳ Certificate validation: **10-30 minutes**
- 🔄 Automatic deployment once validated: **~5 minutes**
- ☁️ CloudFront deployment: **10-15 minutes** after creation

### After Certificate Validates:
1. **Automatic** (Script handles):
   - CloudFront distribution creation
   - Route 53 A record creation
   
2. **Manual** (You need to do):
   - Deploy documentation content to S3
   - Verify the site works
   - Set up GitHub secrets for CI/CD
   - Test CI/CD workflow

### Total Estimated Time:
- **Certificate validation**: 10-30 minutes ⏳ (happening now)
- **Infrastructure creation**: ~5 minutes (automatic)
- **CloudFront deployment**: 10-15 minutes
- **Manual content deployment**: ~5 minutes
- **CI/CD setup**: ~15 minutes

**Total**: ~45-70 minutes from now

---

## Current Action Required

**Nothing right now!** The monitoring script is handling everything automatically.

**Just monitor progress**:
```bash
cd infrastructure
tail -f wait-and-deploy-docs.log
```

Once you see "✅ Certificate validated!" and "🎉 Deployment complete!", proceed with Step 3 (deploying content).


