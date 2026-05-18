# Rollback Runbook

**Last updated:** 2026-05-18
**Audience:** On-call operator with AWS console + CLI access
**Estimated time:** 5–15 minutes per service

This runbook covers rolling back the **backend** (ECS Fargate) and the
**frontend** (S3 + CloudFront) to the previous known-good revision. Both
rollbacks are independent — you can roll back one without the other.

---

## Quick decision tree

| Symptom | What's broken | Rollback target |
|---|---|---|
| `/health` returns 5xx or times out | Backend (ECS) | Previous ECS task definition revision |
| API endpoints return 5xx but `/health` is OK | Backend application bug | Previous ECS task definition revision |
| Login page is blank / Angular routing 404s | Frontend (S3/CloudFront) | Previous S3 version + CloudFront invalidation |
| Both broken after a deploy | Either | Roll back both, **backend first** so the API is healthy before re-serving the frontend |

---

## Backend rollback (ECS Fargate)

The backend runs as ECS service `church-course-tracker-service` in cluster
`church-course-tracker-cluster`. Task definitions are versioned; rolling back
means pointing the service at the previous revision number.

### 1. Identify the current and previous task definition revisions

```bash
aws ecs describe-services \
  --cluster church-course-tracker-cluster \
  --services church-course-tracker-service \
  --region us-east-1 \
  --query 'services[0].taskDefinition' --output text
# → arn:aws:ecs:us-east-1:334581603621:task-definition/church-course-tracker-backend:<N>

aws ecs list-task-definitions \
  --family-prefix church-course-tracker-backend \
  --status ACTIVE --sort DESC \
  --region us-east-1 --max-items 5 --output table
```

The CURRENT revision is whatever the first command printed (call it `N`).
The previous known-good revision is typically `N-1` — but if the *current
revision is itself broken* you should pick the one before the bad deploy.

### 2. Update the service to the previous revision

```bash
PREV_REVISION=N-1   # set this explicitly; do not use arithmetic blindly
aws ecs update-service \
  --cluster church-course-tracker-cluster \
  --service church-course-tracker-service \
  --task-definition church-course-tracker-backend:$PREV_REVISION \
  --force-new-deployment \
  --region us-east-1
```

### 3. Wait for the rollback to land

```bash
until aws ecs describe-services \
        --cluster church-course-tracker-cluster \
        --services church-course-tracker-service \
        --region us-east-1 \
        --query 'services[0].deployments[0].rolloutState' \
        --output text 2>/dev/null | grep -q COMPLETED; do
  sleep 15
done
echo "Rollover complete"
```

Then verify:

```bash
curl -s https://api.quentinspencer.com/health | python3 -m json.tool
```

Expected:
```json
{"status": "healthy", ..., "checks": {"database": "healthy", ...}}
```

### 4. Tell GitHub Actions to skip the auto-redeploy

The `Deploy to AWS` workflow triggers on every push to `main`. If you push
a hotfix commit while ECS is still serving the rolled-back revision, the
workflow will push the bad image again. To prevent that:

- Add `[skip ci]` to your hotfix commit message, OR
- Disable the workflow temporarily in GitHub Actions UI, OR
- Push the fix to a different branch and open a PR (which doesn't trigger
  the deploy workflow — only pushes to `main` do)

### 5. If a known-good ECR image hash isn't deployable

If the previous task definition still references a corrupted image:

```bash
# List recent images in ECR
aws ecr describe-images \
  --repository-name church-course-tracker-backend \
  --region us-east-1 \
  --query 'sort_by(imageDetails,& imagePushedAt)[-10:].{Tag:imageTags,Pushed:imagePushedAt}' \
  --output table

# Register a new task definition pointing at a specific image SHA
aws ecs describe-task-definition \
  --task-definition church-course-tracker-backend \
  --region us-east-1 \
  > /tmp/td.json
# Edit /tmp/td.json: change the image reference to the SHA you want, then:
aws ecs register-task-definition --cli-input-json file:///tmp/td.json --region us-east-1
# Then update-service to the new revision as in step 2.
```

---

## Frontend rollback (S3 + CloudFront)

The frontend lives in S3 bucket `church-course-tracker-static-hp35od11`
under the `churchcoursetracker/` prefix. S3 versioning is enabled, so the
previous version of every object is preserved.

### 1. Find the version IDs to restore

```bash
# Show the 10 most recent index.html versions
aws s3api list-object-versions \
  --bucket church-course-tracker-static-hp35od11 \
  --prefix churchcoursetracker/index.html \
  --query 'Versions[0:10].{VersionId:VersionId,LastModified:LastModified,IsLatest:IsLatest}' \
  --output table
```

The IsLatest=True version is what's currently served. Pick the most recent
version that was deployed BEFORE the bad deploy.

### 2. Restore each object to the previous version

The frontend is many files (~100 of `*.js`, `*.css`, `*.html`, plus assets).
The simplest reliable rollback is to copy every file from the previous build's
git commit and re-sync:

```bash
# Find the commit SHA of the previous good frontend deploy
git log --oneline --no-merges frontend/church-course-tracker/

# Check out the previous good frontend
git checkout <SHA> -- frontend/church-course-tracker/
cd frontend/church-course-tracker
npm ci
npm run build -- --configuration=production --base-href=/churchcoursetracker/

# Sync the rebuilt bundle to S3 (use the OIDC role if running from CI;
# from a developer machine the local aws creds work)
aws s3 sync dist/church-course-tracker/ \
  s3://church-course-tracker-static-hp35od11/churchcoursetracker/ \
  --delete
```

### 3. Invalidate CloudFront cache

```bash
aws cloudfront create-invalidation \
  --distribution-id <DIST_ID> \
  --paths "/churchcoursetracker/*"
```

The distribution ID is stored in the `CLOUDFRONT_DISTRIBUTION_ID` GitHub
Actions secret. To find it locally:

```bash
aws cloudfront list-distributions \
  --query 'DistributionList.Items[?contains(Aliases.Items[0],`apps.quentinspencer.com`)].Id' \
  --output text
```

### 4. Verify

```bash
curl -s -I https://apps.quentinspencer.com/churchcoursetracker/ | head -5
# Should return HTTP/2 200
```

Open the site in a browser with cache disabled (Chrome DevTools → Network →
Disable cache) to confirm the rolled-back bundle loads.

---

## Post-rollback

1. **Open a postmortem issue** with: what broke, who noticed, when, what the
   rollback did, and what permanent fix is needed.
2. **Don't push to `main`** until the fix is identified and tested — the
   deploy workflow will re-deploy the bad code on the next push.
3. **Check Sentry** for any error fingerprints introduced by the bad deploy.
4. **Check `/health`** for `db: healthy` even after the rollback completes — a
   schema migration that ran during the bad deploy may have left the DB in a
   state the old code doesn't handle. See `docs/RUNBOOKS/` for the
   migration-issue runbook (TODO: not yet written; raise a P1 if you hit this).

---

## Related runbooks

- [RDS_PASSWORD_ROTATION.md](RDS_PASSWORD_ROTATION.md) — rotate the database master password
- [SECRETS_UPDATE.md](SECRETS_UPDATE.md) — update a value in AWS Secrets Manager
