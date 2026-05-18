# Developer Quickstart

**Last updated:** 2026-05-18
**Audience:** Engineer joining the project for the first time
**Goal:** Get to a green local test run in under 1 hour.

For end-user documentation (using the deployed app), see
[GETTING_STARTED.md](GETTING_STARTED.md). This document is for engineers
who will be modifying the codebase.

---

## Prerequisites

| Tool | Version | Used for |
|---|---|---|
| Python | 3.12 | Backend |
| Node | 18 or 20 | Frontend, e2e tests |
| Git | any recent | Source control |
| AWS CLI | v2 | Production debugging (optional for local dev) |
| Docker | any recent | Local prod-like containers (optional) |
| Terraform | 1.6.6 | Infrastructure changes (optional for app-only dev) |

You do **not** need AWS credentials to develop the application locally — the
backend can run against SQLite and the frontend can point at the local
backend. AWS credentials are only needed for production debugging or
Terraform changes.

---

## Repository tour

```
.
├── backend/                          # FastAPI/SQLAlchemy backend
│   ├── app/
│   │   ├── api/v1/endpoints/         # HTTP route handlers
│   │   ├── core/                     # Config, security, database
│   │   ├── models/                   # SQLAlchemy ORM models
│   │   ├── schemas/                  # Pydantic request/response schemas
│   │   └── services/                 # Business logic between endpoints and models
│   ├── migrations/versions/          # Alembic migrations
│   ├── tests/                        # pytest suite (574 tests)
│   ├── main.py                       # FastAPI app entrypoint
│   ├── start.sh                      # Container start script
│   ├── env.example                   # Copy to .env
│   └── requirements.txt
├── frontend/church-course-tracker/   # Angular 18 frontend
│   ├── src/app/                      # Angular components, services, guards
│   ├── src/environments/             # version + API URL config (auto-synced)
│   └── package.json
├── tests/e2e/                        # Playwright e2e suite (19 specs / 183 tests)
├── infrastructure/                   # Terraform (119 AWS resources)
├── scripts/                          # Operational scripts
├── docs/                             # Project documentation
│   └── RUNBOOKS/                     # Operator runbooks (rollback, etc.)
└── .github/workflows/                # CI/CD (5 workflows)
```

Recently-touched files worth reading first:
- [docs/EVALUATION_2026-05-18.md](EVALUATION_2026-05-18.md) — most recent
  full-codebase audit; lists known issues and ongoing work
- [docs/PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) — high-level structure
- [README.md](../README.md) — public-facing project overview

---

## Backend local setup

```bash
cd backend

# 1. Virtualenv + dependencies
python3 -m venv venv
source venv/bin/activate         # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Config
cp env.example .env
# Edit .env. The minimum required values for local dev:
#   ADMIN_PASSWORD=<anything you can remember>  (creates the seed admin)
#   SECRET_KEY=<any random 32+ char string>     (JWT signing key)
# The default DATABASE_URL uses SQLite at ./data/church_course_tracker.db
# — no Postgres setup required.

# 3. Run migrations (creates schema + seeds the admin user)
alembic upgrade head

# 4. Start the dev server
uvicorn main:app --reload
# Backend now listening on http://localhost:8000
# Swagger UI: http://localhost:8000/docs
```

Sanity check:

```bash
curl http://localhost:8000/health
# Should return {"status": "healthy", ...}
```

To log in via the API:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d "{\"username\":\"Admin\",\"password\":\"$ADMIN_PASSWORD\"}"
# Returns {"access_token": "eyJ...", ...}
```

**Time to here from a fresh clone:** ~10 min.

---

## Frontend local setup

```bash
cd frontend/church-course-tracker
npm install                       # ~3 min the first time
npm start                         # Starts ng serve at http://localhost:4200
```

The frontend proxies API calls to `http://localhost:8000`. Open
http://localhost:4200 in a browser, click "Login", and use the credentials
from your backend `.env`.

**Time to here from a fresh clone (after backend):** ~5 min.

---

## Running the test suites

### Backend (pytest, 574 tests, ~7 min)

```bash
cd backend
source venv/bin/activate
pytest                            # Full suite
pytest tests/test_security.py     # One file
pytest -k "admin"                 # By keyword
pytest --cov=app --cov-report=term-missing   # With coverage report
```

The test suite uses SQLite (separate from your dev database) and creates
fresh fixtures per test. No external dependencies; runs offline.

### Frontend (Karma/Jasmine, ~3 min)

```bash
cd frontend/church-course-tracker
npm test                          # Watch mode
ng test --watch=false             # Single run
ng test --watch=false --browsers=ChromeHeadless   # Headless (CI mode)
```

Coverage report is written to `coverage/church-course-tracker/index.html`.

### E2E (Playwright, ~8 min in CI, ~38 min locally)

The e2e suite runs against the **deployed production environment**, not
localhost. It does not require running the backend locally.

```bash
cd tests/e2e
npm install
npx playwright install --with-deps chromium

# Set required env vars (the workflow uses these too)
export APP_BASE_URL=https://apps.quentinspencer.com/churchcoursetracker
export API_BASE_URL=https://tinev5iszf.execute-api.us-east-1.amazonaws.com
export PLAYWRIGHT_BASE_URL=https://apps.quentinspencer.com
export E2E_SKIP_DATA_LOAD=true
export E2E_SKIP_DATA_CLEANUP=true
export CI=true                    # Limits to chromium only, otherwise it'll also run Firefox/WebKit/Mobile (~7x runtime)
export E2E_ADMIN_USERNAME=Admin
# Get the admin password from AWS Secrets Manager:
export E2E_ADMIN_PASSWORD=$(aws secretsmanager get-secret-value \
  --secret-id church-course-tracker-secrets --region us-east-1 \
  --query 'SecretString' --output text \
  | python3 -c "import json,sys;print(json.loads(sys.stdin.read())['ADMIN_PASSWORD'])")

npx playwright test --reporter=line
# Or just one spec:
npx playwright test tests/e2e/auth-route-test.spec.ts
```

If you don't have AWS credentials, tests requiring admin auth will skip
cleanly — the non-auth tests will still run.

**Time to here from a fresh clone (full suite):** ~50 min if you run all
three. Most engineers won't run e2e locally; CI runs it on every push.

---

## Common workflows

### Adding a new endpoint

1. Add the route handler in `backend/app/api/v1/endpoints/<resource>.py`
2. Require authentication: `current_user: dict = Depends(get_current_active_user)`
3. Add an admin/role check if it's a write path
4. Add a test in `backend/tests/test_endpoints.py` (use the `admin_token`
   fixture from `conftest.py`)
5. Register the router in `backend/app/api/v1/api.py` if it's a new file

### Adding a database column

**Don't** add inline ALTER TABLE in `backend/start.sh` (that pattern is
being deprecated — see eval §3.3 SS-01). Instead:

```bash
cd backend
source venv/bin/activate
alembic revision -m "add my_column to my_table"
# Edit the new file in backend/migrations/versions/
alembic upgrade head        # Apply locally
pytest                      # Verify
```

### Adding a Karma test

The convention is `<component-name>.component.spec.ts` next to the component.
Six component trees still lack specs (see eval §3.2 Q8): `enrollments`,
`programs`, `audit`, `profile`, `members`, `activity-logs`. PRs adding any
of these are welcome.

---

## Production reference

| Resource | Value |
|---|---|
| Frontend URL | https://apps.quentinspencer.com |
| API URL | https://api.quentinspencer.com |
| API Swagger schema | https://api.quentinspencer.com/openapi.json |
| AWS account | 334581603621 |
| AWS region | us-east-1 |
| ECS cluster | `church-course-tracker-cluster` |
| ECS service | `church-course-tracker-service` |
| RDS instance | `church-course-tracker-db` (PostgreSQL 15, t4g.micro) |
| S3 static bucket | `church-course-tracker-static-hp35od11` |
| Terraform state bucket | `church-course-tracker-tfstate-334581603621` |
| Terraform lock table (DynamoDB) | `church-course-tracker-tflock` |

For operational procedures (rollback, password rotation, secrets update)
see [docs/RUNBOOKS/](RUNBOOKS/).

---

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `pip install` fails on `psycopg2-binary` | Missing `libpq-dev` system package. `apt install libpq-dev` (Ubuntu) or skip — psycopg2 isn't needed for the SQLite default. |
| `alembic upgrade head` errors with "multiple heads" | Two migrations branched. Run `alembic heads` to see them, then `alembic merge -m "merge heads"` to resolve. |
| Backend returns 422 on every request | You sent an empty body. The endpoints use Pydantic validation; missing required fields produce 422. Check the OpenAPI spec for the schema. |
| `npm start` fails with "ng: command not found" | You ran `npm ci --only=production`. Use `npm ci` (full install) — the Angular CLI is a devDependency. |
| Karma tests fail with "ChromeHeadless has not captured" | Chrome/Chromium not installed. Install via `apt install chromium-browser` or use `--browsers=Firefox` if Firefox is available. |
| Playwright tests skip everything | `ADMIN_PASSWORD` env var not set. See E2E setup above. |

---

## Where to ask for help

- [docs/](.) — start here, especially `EVALUATION_2026-05-18.md` for known issues
- [docs/RUNBOOKS/](RUNBOOKS/) — operational procedures
- `.github/workflows/*.yml` — CI/CD reference for what "correct" looks like
- The project maintainer — for credentials, AWS access, or scope decisions
