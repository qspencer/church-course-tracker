# GitHub Secrets Configuration for CI/CD

This document describes the GitHub repository secrets needed for the automated documentation deployment workflow.

## Required Secrets

The GitHub Actions workflow (`.github/workflows/deploy-docs.yml`) requires the following secrets to be configured in your GitHub repository:

### 1. `AWS_DEPLOY_ROLE_ARN` (Required)

**Purpose:** IAM role ARN for GitHub Actions to assume via OIDC for AWS access.

**Value:**
```
arn:aws:iam::334581603621:role/church-course-tracker-github-actions-docs-deploy
```

**How to get it:**
```bash
cd infrastructure
terraform output github_actions_docs_deploy_role_arn
```

**How to set it:**
1. Go to your GitHub repository: https://github.com/qspencer/church-course-tracker
2. Navigate to: **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `AWS_DEPLOY_ROLE_ARN`
5. Value: `arn:aws:iam::334581603621:role/church-course-tracker-github-actions-docs-deploy`
6. Click **Add secret**

### 2. `DOCS_S3_BUCKET` (Optional)

**Purpose:** S3 bucket name for documentation deployment. Defaults to `docs.quentinspencer.com` if not set.

**Value:**
```
docs.quentinspencer.com
```

**Note:** This is optional as the workflow will use the default value if not provided.

### 3. `DOCS_CLOUDFRONT_DIST_ID` (Optional)

**Purpose:** CloudFront distribution ID for cache invalidation. The workflow will attempt to find it automatically if not set.

**Value:**
```
E2MHY4DQIRWUEQ
```

**How to get it:**
```bash
cd infrastructure
terraform output docs_cloudfront_distribution_id
```

**Note:** This is optional as the workflow will attempt to find the distribution automatically.

## Setting Up Secrets

### Via GitHub Web Interface

1. Navigate to your repository on GitHub
2. Go to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** for each secret above
4. Enter the name and value
5. Click **Add secret**

### Via GitHub CLI (Alternative)

```bash
# Install GitHub CLI if needed: https://cli.github.com/
gh secret set AWS_DEPLOY_ROLE_ARN --body "arn:aws:iam::334581603621:role/church-course-tracker-github-actions-docs-deploy"
gh secret set DOCS_S3_BUCKET --body "docs.quentinspencer.com"
gh secret set DOCS_CLOUDFRONT_DIST_ID --body "E2MHY4DQIRWUEQ"
```

## Verifying Secrets

After setting the secrets, you can verify the workflow will work by:

1. Making a small change to any file in `docs-site/`
2. Committing and pushing to the `main` branch
3. Checking the **Actions** tab in GitHub to see if the workflow runs successfully

## Security Notes

- **OIDC Authentication:** The workflow uses OpenID Connect (OIDC) for secure, keyless authentication to AWS
- **No Access Keys:** No AWS access keys or secrets are stored in GitHub
- **Least Privilege:** The IAM role has minimal permissions (only S3 upload and CloudFront invalidation)
- **Repository Scoped:** The role can only be assumed by workflows in the `qspencer/church-course-tracker` repository

## Troubleshooting

### Workflow fails with "Access Denied"

- Verify `AWS_DEPLOY_ROLE_ARN` secret is set correctly
- Check that the IAM role exists and has the correct trust policy
- Ensure the OIDC provider is configured correctly

### Workflow can't find CloudFront distribution

- Set `DOCS_CLOUDFRONT_DIST_ID` secret explicitly
- Verify the distribution ID is correct: `terraform output docs_cloudfront_distribution_id`

### S3 upload fails

- Verify `DOCS_S3_BUCKET` secret is set (or using default)
- Check IAM role has S3 permissions for the bucket
- Verify bucket exists: `aws s3 ls s3://docs.quentinspencer.com`

## Related Documentation

- [Deployment Guide](./DEPLOYMENT.md)
- [GitHub Actions Workflow](../.github/workflows/deploy-docs.yml)
- [Infrastructure OIDC Configuration](../infrastructure/github_actions_oidc.tf)


