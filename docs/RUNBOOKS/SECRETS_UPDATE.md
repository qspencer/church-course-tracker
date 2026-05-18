# Secrets Manager Value Update Runbook

**Last updated:** 2026-05-18
**Audience:** Operator with AWS CLI access
**Estimated time:** 5 minutes + ~2 min ECS rollover

This runbook covers updating a value inside the `app_secrets` Secrets Manager
entry (`church-course-tracker-secrets`). That secret is consumed at ECS
container start; existing running tasks do **not** refetch, so updates take
effect on the next deployment.

---

## What lives in `app_secrets`

| Key | Used for |
|---|---|
| `DATABASE_URL` | Postgres connection string (see [RDS_PASSWORD_ROTATION.md](RDS_PASSWORD_ROTATION.md) for the safe rotation procedure) |
| `SECRET_KEY` | FastAPI JWT signing key |
| `PLANNING_CENTER_APP_ID` | Planning Center API client ID |
| `PLANNING_CENTER_SECRET` | Planning Center API client secret |
| `USE_MOCK_PLANNING_CENTER` | Toggle the mock Planning Center module (string `"true"` or `"false"`) |
| `ADMIN_PASSWORD` | Bootstrap password for the seeded `Admin` user (read by the `v2w3x4y5z6a7_ensure_admin_user` Alembic migration) |

**Important:** the Terraform-defined `secret_string` in `infrastructure/secrets.tf`
is bootstrap-only and uses placeholder values. The live secret diverges from
the Terraform code by design — `aws_secretsmanager_secret_version.app_secrets`
has `lifecycle { ignore_changes = [secret_string, version_stages] }` to
prevent `terraform apply` from clobbering live values. Always update via
this runbook, not by editing Terraform.

---

## Procedure for adding or updating a key

### 1. Read the current secret into a temp file

```bash
aws secretsmanager get-secret-value \
  --secret-id church-course-tracker-secrets \
  --region us-east-1 \
  --query 'SecretString' --output text \
  > /tmp/app_secrets.json
chmod 600 /tmp/app_secrets.json
```

Verify the keys present:

```bash
python3 -c "import json; print(sorted(json.load(open('/tmp/app_secrets.json')).keys()))"
```

### 2. Edit the value

For a simple string update (e.g., updating `SECRET_KEY`):

```bash
python3 <<PYEOF
import json
d = json.load(open("/tmp/app_secrets.json"))
d["SECRET_KEY"] = "your-new-secret-key-here"   # replace with the real value
json.dump(d, open("/tmp/app_secrets.json", "w"))
PYEOF
```

For interactive input (avoids echoing the value into your shell history):

```bash
python3 <<PYEOF
import json, getpass
d = json.load(open("/tmp/app_secrets.json"))
key = input("Key to update: ")
val = getpass.getpass(f"New value for {key}: ")
d[key] = val
json.dump(d, open("/tmp/app_secrets.json", "w"))
print(f"Updated {key} ({len(val)} chars)")
PYEOF
```

### 3. Write the new version to Secrets Manager

```bash
aws secretsmanager put-secret-value \
  --secret-id church-course-tracker-secrets \
  --region us-east-1 \
  --secret-string file:///tmp/app_secrets.json
```

This creates a new version and moves the `AWSCURRENT` stage to it. The
previous version is retained for 7 days (the `recovery_window_in_days`
setting) and can be restored if needed (see Rollback section below).

### 4. Force ECS to roll so new tasks pick up the new value

```bash
aws ecs update-service \
  --cluster church-course-tracker-cluster \
  --service church-course-tracker-service \
  --force-new-deployment \
  --region us-east-1

# Wait for completion
until aws ecs describe-services \
        --cluster church-course-tracker-cluster \
        --services church-course-tracker-service \
        --region us-east-1 \
        --query 'services[0].deployments[0].rolloutState' \
        --output text 2>/dev/null | grep -q COMPLETED; do
  sleep 15
done
```

### 5. Verify the app started cleanly with the new value

```bash
curl -s https://api.quentinspencer.com/health | python3 -m json.tool
```

### 6. Securely delete the temp file

```bash
shred -u /tmp/app_secrets.json
```

---

## Special cases

### Updating `DATABASE_URL`

Use [RDS_PASSWORD_ROTATION.md](RDS_PASSWORD_ROTATION.md). DATABASE_URL is
generated from the random RDS password and is not edited directly.

### Updating `ADMIN_PASSWORD`

This value is only consumed by the `v2w3x4y5z6a7_ensure_admin_user` Alembic
migration, which runs at container start and is **idempotent**: it skips if
the Admin user already exists. So changing `ADMIN_PASSWORD` here does NOT
change the admin password in the database.

To change the live admin password, log in via the application UI and use
the change-password flow, or use `scripts/update_admin_credentials.py` (note:
this script may have been deleted in the 2026-05-18 cleanup — verify before
referencing).

### Adding a brand-new key

Same procedure as above. After Secrets Manager has the new key, you also
need to:

1. Reference it in `backend/app/core/config.py` (read it via
   `os.getenv("YOUR_NEW_KEY")`)
2. Add a `valueFrom` entry to the ECS task definition (in
   `infrastructure/ecs.tf` under `secrets = [...]`)
3. `terraform apply` to register the new task definition
4. Force ECS rollover

---

## Rollback

To restore the previous version of `app_secrets`:

```bash
# List recent versions
aws secretsmanager list-secret-version-ids \
  --secret-id church-course-tracker-secrets \
  --region us-east-1 \
  --query 'sort_by(Versions,& CreatedDate)[-5:].{VersionId:VersionId,Stages:VersionStages,CreatedDate:CreatedDate}' \
  --output table

# Move AWSCURRENT back to the prior version
PRIOR_VID=<from-above>
CURRENT_VID=<from-above>
aws secretsmanager update-secret-version-stage \
  --secret-id church-course-tracker-secrets \
  --version-stage AWSCURRENT \
  --remove-from-version-id "$CURRENT_VID" \
  --move-to-version-id "$PRIOR_VID" \
  --region us-east-1

# Force ECS rollover
aws ecs update-service \
  --cluster church-course-tracker-cluster \
  --service church-course-tracker-service \
  --force-new-deployment \
  --region us-east-1
```

---

## Related runbooks

- [ROLLBACK.md](ROLLBACK.md) — service-level rollback
- [RDS_PASSWORD_ROTATION.md](RDS_PASSWORD_ROTATION.md) — the specific procedure for DATABASE_URL
