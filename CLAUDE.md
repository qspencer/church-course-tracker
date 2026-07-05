# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this is

Church Course Tracker — a learning-management system for churches. Live production system:

- **Frontend**: Angular 21 SPA at https://apps.quentinspencer.com/churchcoursetracker (S3 + CloudFront; note the `/churchcoursetracker` base path)
- **API**: FastAPI on ECS Fargate behind API Gateway HTTP API (no ALB) at https://api.quentinspencer.com
- **Docs site**: MkDocs at docs.quentinspencer.com (S3 + CloudFront)
- **Database**: RDS PostgreSQL in production; SQLite locally
- **Infra**: Terraform in `infrastructure/` (S3 remote state + DynamoDB locking — never commit state or plan files)

## Layout

```
backend/                        # FastAPI app (routers → services → SQLAlchemy models, Pydantic schemas)
frontend/church-course-tracker/ # Angular 21, standalone components, inject() DI, @if/@for control flow
infrastructure/                 # Terraform (AWS)
tests/e2e/                      # THE real Playwright e2e suite (own package.json + config)
docs/                           # Engineering docs + RUNBOOKS/ (rollback, secrets rotation)
docs/archive/                   # Historical status reports — do NOT trust as current
docs-site/                      # MkDocs source for the published user docs
scripts/                        # Deploy and utility scripts
```

## Traps — read before touching tests or docs

- **e2e tests live in `tests/e2e/` only** (own package.json + config): `cd tests/e2e && npm ci && npm test`. A broken legacy Playwright layer at the repo root was deleted in July 2026 — don't recreate a root-level test setup or root package.json.
- **e2e runs against production.** Never add destructive or data-mutating tests without explicit cleanup. Credentials come from `E2E_ADMIN_USERNAME` / `E2E_ADMIN_PASSWORD` env vars (locally via `tests/e2e/.env.e2e`, untracked) — never hardcode them.
- **`docs/archive/` is historical.** It once contained committed credentials (removed 2026-07-05, password rotated). Never write credentials into any tracked file — this includes session notes, status reports, and test docs.
- **Changing `ADMIN_PASSWORD` in Secrets Manager does not change the live admin password.** The seeding migration is idempotent and skips existing users. See `docs/RUNBOOKS/SECRETS_UPDATE.md`.
- **Terraform's `secrets.tf` values are bootstrap placeholders.** The live Secrets Manager value diverges by design (`ignore_changes`). Update secrets via the runbook, not Terraform.

## Commands

```bash
# Backend (Python 3.11+; prod image is 3.12)
cd backend && source venv/bin/activate
uvicorn main:app --reload          # dev server on :8000
pytest                             # unit/integration tests (uses /tmp test DB via conftest safeguards)

# Frontend (Node 22, Angular 21)
cd frontend/church-course-tracker
npm start                          # dev server on :4200
npm test                           # Karma/Jasmine unit tests
npm run build -- --configuration production

# E2E (Playwright)
cd tests/e2e && npm ci && npm test # requires E2E_* env vars; targets production

# Infrastructure
cd infrastructure && terraform plan   # remote state; never commit *.tfstate* or *.tfplan
```

## Conventions

- **Versioning is automated**: `scripts/increment-version.sh` + `version.txt`; CI commits bumps with `[skip ci]`. Don't bump versions manually.
- **Deploys are immutable**: deploy.yml pushes a SHA-tagged image (ECR is tag-immutable, no `:latest`) and registers a new ECS task-definition revision. Terraform ignores task-definition/service drift via `lifecycle` blocks in `ecs.tf` — to change container env vars or resources, edit `ecs.tf`, temporarily comment out the `ignore_changes` block, apply, then let the next CI deploy re-pin the image.
- **Frontend**: standalone components only, `inject()` over constructor DI, functional guards, `@if`/`@for` control flow. New subscriptions should use `takeUntilDestroyed()` or the `async` pipe.
- **Backend**: keep HTTP-client and business logic in `app/services/`, not endpoints. Role checks belong on the endpoint via dependencies. Never log or return raw exception text to clients.
- **Secrets**: AWS Secrets Manager (`church-course-tracker-secrets`) injected via ECS task definition. GitHub Actions authenticates via OIDC — no long-lived AWS keys anywhere.
- **Seed data**: `backend/data/csv/` CSVs load when `LOAD_CSV_DATA=true`. The users CSV must not contain a password column; seed passwords come from env (see `app/core/csv_loader.py`).

## Key docs

- `docs/RUNBOOKS/` — rollback, RDS password rotation, secrets updates (current and accurate)
- `docs/DEVELOPER_QUICKSTART.md` — fresh-clone setup (may lag on versions; the code is the source of truth)
- `tests/e2e/README.md` — e2e suite usage
