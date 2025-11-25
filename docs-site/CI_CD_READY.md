# CI/CD Pipeline - Ready ✅

## Status

The automated documentation deployment pipeline is now **fully configured and ready**!

## What's Configured

✅ **GitHub Actions Workflow:** `.github/workflows/deploy-docs.yml`
✅ **AWS OIDC Provider:** Configured for GitHub Actions
✅ **IAM Role:** `church-course-tracker-github-actions-docs-deploy`
✅ **GitHub Secret:** `AWS_DEPLOY_ROLE_ARN` (added)

## How It Works

### Automatic Deployment

The workflow automatically triggers when:
- You push changes to files in `docs-site/` directory
- You push to the `main` branch
- You manually trigger it via GitHub Actions UI

### What Happens

1. **Build:** MkDocs builds the documentation site
2. **Deploy:** Files are uploaded to S3 bucket `docs.quentinspencer.com`
3. **Invalidate:** CloudFront cache is invalidated for fresh content
4. **Verify:** Check the Actions tab to see deployment status

## Testing the Pipeline

### Option 1: Make a Small Change

1. Edit any file in `docs-site/docs/` (e.g., add a comment)
2. Commit and push:
   ```bash
   git add docs-site/docs/
   git commit -m "Test documentation deployment"
   git push
   ```
3. Check GitHub Actions: https://github.com/qspencer/church-course-tracker/actions

### Option 2: Manual Trigger

1. Go to: https://github.com/qspencer/church-course-tracker/actions/workflows/deploy-docs.yml
2. Click **Run workflow**
3. Select branch: `main`
4. Click **Run workflow**

## Workflow Details

### Triggers
- **Push to main:** When `docs-site/**` files change
- **Manual:** Via GitHub Actions UI

### Steps
1. Checkout code
2. Set up Python 3.12
3. Install dependencies
4. Build documentation (MkDocs)
5. Configure AWS credentials (OIDC)
6. Get CloudFront distribution ID
7. Deploy to S3
8. Invalidate CloudFront cache
9. Show deployment summary

### Permissions
- **Contents:** Read (to checkout code)
- **ID Token:** Write (for OIDC authentication)

## Monitoring

### View Workflow Runs
- **GitHub Actions Tab:** https://github.com/qspencer/church-course-tracker/actions
- **Filter:** Select "Deploy Documentation" workflow

### Check Deployment Status
- **Success:** Green checkmark ✅
- **Failure:** Red X ❌ (click to see logs)

### Verify Deployment
After a successful run, check:
- **Site:** https://docs.quentinspencer.com/churchcoursetracker/
- **Latest changes:** Should appear within 5-15 minutes (CloudFront propagation)

## Troubleshooting

### Workflow Fails with "Access Denied"
- Verify `AWS_DEPLOY_ROLE_ARN` secret is set correctly
- Check IAM role trust policy allows GitHub Actions
- Ensure OIDC provider is configured

### Workflow Fails to Find CloudFront
- Set `DOCS_CLOUDFRONT_DIST_ID` secret explicitly
- Or verify the distribution exists: `terraform output docs_cloudfront_distribution_id`

### Build Fails
- Check Python dependencies in `docs-site/requirements.txt`
- Verify `mkdocs.yml` is valid
- Review build logs in GitHub Actions

### Deployment Succeeds but Site Not Updated
- CloudFront cache may still be propagating (5-15 minutes)
- Check CloudFront invalidation status in AWS Console
- Try accessing: `https://docs.quentinspencer.com/churchcoursetracker/index.html`

## Security

✅ **No Access Keys:** Uses OIDC (OpenID Connect) for secure authentication
✅ **Least Privilege:** IAM role only has S3 upload and CloudFront invalidation permissions
✅ **Repository Scoped:** Only works for `qspencer/church-course-tracker` repository
✅ **Audit Trail:** All deployments logged in GitHub Actions

## Next Steps

1. **Test the pipeline:** Make a small change and push
2. **Monitor first deployment:** Check GitHub Actions tab
3. **Verify site updates:** Visit the documentation site after deployment
4. **Document workflow:** Team members can now deploy by pushing to main

## Related Documentation

- **GitHub Secrets:** `docs-site/GITHUB_SECRETS.md`
- **Deployment Guide:** `docs-site/DEPLOYMENT.md`
- **Deployment Complete:** `docs-site/DEPLOYMENT_COMPLETE.md`
- **Workflow File:** `.github/workflows/deploy-docs.yml`

---

**Status:** ✅ Ready for use
**Last Updated:** November 23, 2025


