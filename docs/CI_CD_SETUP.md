# CI/CD Pipeline Setup Guide

## Overview

The Church Course Tracker now has a complete CI/CD pipeline using GitHub Actions that automatically tests and deploys your code to AWS.

## 🔄 Workflows

### 1. Backend Tests (`backend-tests.yml`)

**Triggers:**
- Push to `main` or `develop` branches (when backend files change)
- Pull requests to `main` (when backend files change)

**What it does:**
- Sets up Python 3.11 environment
- Installs dependencies
- Runs linting (flake8, black, isort)
- Runs tests with coverage
- Uploads coverage reports to Codecov

**Duration:** ~3-5 minutes

### 2. Frontend Tests (`frontend-tests.yml`)

**Triggers:**
- Push to `main` or `develop` branches (when frontend files change)
- Pull requests to `main` (when frontend files change)

**What it does:**
- Sets up Node.js 18 environment
- Installs dependencies
- Runs linting
- Runs Angular tests
- Builds production bundle

**Duration:** ~5-7 minutes

### 3. E2E Tests (`e2e-tests.yml`)

**Triggers:**
- Push to `main` branch
- Pull requests to `main`
- Daily at 2 AM UTC (scheduled)
- Manual trigger

**What it does:**
- Sets up Playwright
- Runs end-to-end tests against production
- Uploads test reports and screenshots
- Stores results for 30 days

**Duration:** ~10-15 minutes

### 4. Deployment (`deploy.yml`)

**Triggers:**
- Push to `main` branch
- Manual trigger

**What it does:**
**Backend Deployment:**
- Builds Docker image
- Pushes to Amazon ECR
- Runs database migrations
- Updates ECS service
- Waits for deployment to stabilize

**Frontend Deployment:**
- Builds production Angular app
- Uploads to S3
- Invalidates CloudFront cache

**Duration:** ~10-15 minutes

## 🔐 Required Secrets

To enable CI/CD, add these secrets to your GitHub repository:

### AWS Credentials
- `AWS_ACCESS_KEY_ID` - AWS access key for deployment
- `AWS_SECRET_ACCESS_KEY` - AWS secret key for deployment

### Database
- `DATABASE_URL` - PostgreSQL connection string for migrations

### S3 and CloudFront
- `S3_STATIC_BUCKET` - S3 bucket name for frontend (e.g., `church-course-tracker-static-xyz`)
- `CLOUDFRONT_DISTRIBUTION_ID` - CloudFront distribution ID (e.g., `E1234ABCD5678`)

### How to Add Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret**
4. Add each secret with the appropriate value

## 🚀 How to Use

### Automatic Deployment

Simply push your code to the `main` branch:

```bash
git add .
git commit -m "Your commit message"
git push origin main
```

The CI/CD pipeline will:
1. ✅ Run backend tests
2. ✅ Run frontend tests
3. 🚀 Deploy backend to ECS
4. 🚀 Deploy frontend to S3/CloudFront
5. ✅ Verify deployment

### Manual Deployment

You can trigger deployment manually:

1. Go to **Actions** tab in GitHub
2. Select **Deploy to AWS** workflow
3. Click **Run workflow**
4. Select branch (usually `main`)
5. Click **Run workflow** button

### Running Tests Only

Tests run automatically on every push, but you can also:

**Run specific test suite:**
1. Go to **Actions** tab
2. Select the test workflow you want
3. Click **Run workflow**

**Local testing before push:**
```bash
# Backend tests
cd backend && pytest tests/ -v

# Frontend tests
cd frontend/church-course-tracker && npm test

# E2E tests
npm test
```

## 📊 Monitoring Deployments

### View Deployment Status

1. Go to **Actions** tab in GitHub
2. Click on the workflow run
3. View logs and status for each job

### Deployment Stages

The deployment workflow shows:
- ✅ Checkout code
- ✅ Build Docker image
- ✅ Push to ECR
- ✅ Run migrations
- ✅ Update ECS service
- ✅ Wait for stability
- ✅ Build frontend
- ✅ Deploy to S3
- ✅ Invalidate CloudFront

### Success/Failure Notifications

- ✅ **Success:** Green checkmark on commit
- ❌ **Failure:** Red X on commit - click to see logs
- 🟡 **In Progress:** Yellow dot

## 🐛 Troubleshooting

### Deployment Fails

**Check AWS Credentials:**
```bash
# Verify secrets are set correctly
# Go to Settings > Secrets and variables > Actions
```

**Check ECS Service:**
```bash
aws ecs describe-services \
  --cluster church-course-tracker-cluster \
  --services church-course-tracker-service
```

**Check Logs:**
```bash
# View CloudWatch logs
aws logs tail /ecs/church-course-tracker-backend --follow
```

### Tests Fail

**Backend tests:**
- Check Python version compatibility
- Verify all dependencies are in requirements.txt
- Run tests locally first

**Frontend tests:**
- Check Node.js version compatibility
- Clear cache: `npm cache clean --force`
- Run tests locally first

**E2E tests:**
- Verify production site is accessible
- Check for breaking changes in UI
- Review test screenshots in artifacts

### Migration Fails

**Check database connection:**
```bash
# Test connection to RDS
psql -h <rds-endpoint> -p 5432 -U postgres -d church_course_tracker
```

**Rollback migration:**
```bash
cd backend
alembic downgrade -1
```

## 🔄 Rollback Procedure

If deployment fails or causes issues:

### Rollback Backend

```bash
# Get previous task definition
aws ecs describe-task-definition \
  --task-definition church-course-tracker-backend:PREVIOUS_REVISION

# Update service to use previous revision
aws ecs update-service \
  --cluster church-course-tracker-cluster \
  --service church-course-tracker-service \
  --task-definition church-course-tracker-backend:PREVIOUS_REVISION
```

### Rollback Frontend

```bash
# Re-deploy previous version from backup
aws s3 sync s3://backup-bucket/previous-version/ s3://church-course-tracker-static/

# Invalidate CloudFront
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*"
```

## 📈 Best Practices

### Branch Protection

Enable branch protection on `main`:
1. Go to **Settings** > **Branches**
2. Add rule for `main` branch
3. Enable:
   - ✅ Require pull request reviews
   - ✅ Require status checks to pass
   - ✅ Require branches to be up to date

### Code Review Process

1. Create feature branch: `git checkout -b feature/new-feature`
2. Make changes and commit
3. Push: `git push origin feature/new-feature`
4. Create Pull Request
5. Wait for CI/CD tests to pass
6. Request code review
7. Merge after approval

### Testing Strategy

1. **Write tests first** (TDD)
2. **Run tests locally** before pushing
3. **Fix failing tests** immediately
4. **Maintain test coverage** above 90%
5. **Review test results** in CI/CD

## 🔔 Notifications

### Slack Integration (Optional)

Add Slack notifications to workflows:

```yaml
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Email Notifications

GitHub sends email notifications for:
- Failed workflow runs
- Successful deployments (if enabled)
- Security alerts

## 📝 Workflow Customization

### Modify Test Timeout

Edit `.github/workflows/e2e-tests.yml`:
```yaml
jobs:
  e2e-tests:
    timeout-minutes: 30  # Increase if needed
```

### Add New Environment

Create new workflow file:
```yaml
# .github/workflows/deploy-staging.yml
on:
  push:
    branches: [ develop ]
```

### Skip CI/CD

Add to commit message:
```bash
git commit -m "docs: Update README [skip ci]"
```

## 🎯 Next Steps

1. ✅ Set up GitHub secrets
2. ✅ Enable branch protection
3. ✅ Configure Slack notifications (optional)
4. ✅ Set up staging environment (optional)
5. ✅ Review and customize workflows

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS ECS Deployment](https://docs.aws.amazon.com/ecs/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Playwright Documentation](https://playwright.dev/)

