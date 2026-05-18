# Evaluation 2026-05-18 — Church Course Tracker

**Audit date:** 2026-05-18
**Prior audit:** [`docs/EVALUATION_2026-05-09.md`](EVALUATION_2026-05-09.md) (9 days ago)
**Scope:** Code quality, automated tests, deployment scripts, documentation, and outstanding work.
**Method:** Five parallel investigation streams (per [`/home/ubuntu/Documents/church-course-tracker/EVALUATION_PLAN_2026-05-18.md`](../../../Documents/church-course-tracker/EVALUATION_PLAN_2026-05-18.md)). Full per-area findings retained at `/tmp/eval_2026-05-18/`. Read-only audit — no files modified.

---

## 0. Executive Summary

**Headline:** The May-9 hardening landed cleanly for the *named* findings, but a broader re-sweep reveals the original audit was narrower than it should have been. The auth gap was 10× larger than reported, the e2e suite has been silently red for ~7 weeks, and Terraform state has been local-only this whole time. Today's verdict is **not "worse than May-9"** — it's "more of the iceberg is visible now."

| Theme | What's true today |
|---|---|
| **Auth** ❌ | `GET /users` fix held, but **9 other endpoint modules are still entirely unauthenticated**, including PII (`people.py`), reports (CSV/PDF export), and writes (`enrollments.py` POST/PUT/DELETE, `system_settings.py` POST/PATCH). |
| **Tests** ⚠️ | 574 backend pytest (56% coverage) + 49 frontend Karma (62%) + 183 e2e — sizable suites. But e2e has **failed every run since 2026-03-30** and is not a required check; lint and coverage uploads are `continue-on-error`. |
| **Infra** ⚠️ | Drift-clean (`terraform plan: No changes`). But state is **local-only on one workstation**, OIDC exists yet `deploy.yml` still uses long-lived AWS keys, and there's **no `.dockerignore`** so `.env` + 827 KB SQLite dev DB + `htmlcov/` ship into the prod image. |
| **Boot-time DDL** ❌ | `backend/start.sh` runs **22 `ALTER TABLE` + 2 `CREATE TABLE`** on every container start, with `# Don't exit` on failure — schema corruption can pass `/health`. |
| **Documentation** ⚠️ | README **actively misleads** new devs: `python create_default_admin.py` (script deleted in this session), `.env.example` (file doesn't exist — it's `env.example`), Swagger UI at `/docs` (returns 404). Onboarding composite: **5/10**. |
| **Secrets sweep** ⚠️ | The May-9 `Matthew778*` cleanup held in active code paths, but **`scripts/create_admin_remote.py` still hardcodes `ADMIN_PASSWORD = "admin123"`** posted at the live API. |
| **Dependencies** ⚠️ | **10 high-severity frontend CVEs**: triple XSS in `@angular/core <=18.2.14` (needs 18→19 migration), three lodash-es CVEs (fix is non-breaking, ship today). Backend `passlib==1.7.4` unmaintained since 2019, still imported. |
| **Architecture** ⚠️ | `planning_center_sync_service.py` is **3,473 LOC** at 22% coverage — biggest single-file risk. `programs.py` endpoint module is 1,326 LOC and reaches directly into ORM models. Two dead config files (`config_prod.py`, `config_aws.py`) still ship. |
| **Tooling gap** ⚠️ | `ruff`, `bandit`, `mypy`, `pip-audit`, `eslint`, `tflint`, `tfsec`, `checkov`, `trivy` — **none** installed in this environment. Static analysis surface is shallow until that's fixed. |
| **Closures from May-9** ✅ | `/users` auth, hardcoded README password, SNS placeholder email, version drift (3→2 files), ENVIRONMENT=production + DEBUG=False, DATABASE_URL in Secrets Manager. **6 of 9 substantive findings fully closed.** |

**Bottom line:** Three P0 themes deserve immediate attention this week — close the **unauthenticated-endpoint gap** (cross-cutting, 9 modules), fix or kill the **broken e2e suite** (it's been a no-op for 7 weeks), and add the **missing `.dockerignore` + Terraform state backend** (one bad rm or laptop failure away from real loss).

---

## 1. Code Quality (§3.1)

**One-paragraph summary.** Static analysis ran only as `tsc --noEmit` (0 errors) and `npm audit`; `ruff`, `bandit`, `mypy`, `pip-audit`, `eslint` were absent. Manual review surfaced 33 findings — dominated by a cross-cutting authentication-gap pattern across 9 endpoint modules, plus token-preview logging in `auth.py`, a typo-mounted route at `/api/v1/authrefresh`, JWT in `localStorage` paired with permissive CSP, and 3 dead-code config files still shipping in the image. Full report: `/tmp/eval_2026-05-18/3.1_code_quality.md`.

**Top findings:**

| ID | File:Line | Severity | Issue |
|---|---|---|---|
| B1–B6 / S1 | `people.py`, `reports.py`, `courses.py` (reads), `enrollments.py`, `progress.py`, `system_settings.py` | **P0** | Entire modules unauthenticated. Includes PII reads, anonymous CSV/PDF export, anonymous write paths for enrollments and system config. |
| B7–B9 | `sync.py`, `autocomplete_suggestions.py`, `mock_planning_center.py` | **P1**/P2 | Sync trigger anon-callable; mock module unconditionally mounted in `api.py:70-73`. |
| B10 / S2 | `auth.py:46-54` | **P1** | `logger.info` logs `Authorization` header preview and JWT token preview on every request → ships to CloudWatch. |
| B11 | `auth.py:210` | **P1** | Real bug: `@router.post("refresh")` (missing leading slash) registered alongside `@router.post("/refresh")`. FastAPI silently mounts both → `POST /api/v1/authrefresh` is reachable. |
| B12 | `main.py:191-251` | **P1** | Rate limiter is `defaultdict(list)` — per-process, lost on restart, useless across ECS tasks. Same May-9 finding §2.3, **not closed**. |
| B16 / S6 | `backend/app/core/config_prod.py:21`, `config_aws.py` | **P2** | Two dead config files, neither imported anywhere. `config_prod.py:21` defaults `SECRET_KEY="change-this-in-production"`. Risk: someone "fixes" it and wires it up. |
| B17 | `main.py:253-259` | **P2** | `TrustedHostMiddleware` commented out — the `ALLOWED_HOSTS` list is decorative. |
| B22 | `planning_center_sync_service.py` (3,473 LOC) | **P2** | Single-file God object mixing HTTP client + mappers + persistence + webhook handling. |
| F3 / S7 | `auth.service.ts:14,:100` + `main.py:118-129` (CSP) | **P1** | JWT in localStorage; CSP allows `'unsafe-inline' 'unsafe-eval'`. One XSS = full token theft. |
| F1 | `environment.dev.ts:5` | **P2** | Version still `'0.65'` while `version.txt` is `0.74`. Sentry breadcrumbs report wrong version in dev. |

**Dependencies:** 10 high-severity CVEs in frontend production deps:
- `@angular/core <=18.2.14`: GHSA-jrmj-c5cx-3cw6, GHSA-prjf-86w9-mfqv, GHSA-g93w-mfhg-p222 (XSS triple). Fix requires Angular 18→19.
- `lodash-es <=4.17.23`: GHSA-xxjr-mmjv-4gpg, GHSA-r5fr-rjxr-66jc, GHSA-f23m-r3pf-42rh. Fix non-breaking — `npm audit fix` ships today.
- Backend `passlib==1.7.4` last released 2019, still imported in `user_service.py:178`. `fastapi-cors==0.0.6` is dead (CORS handled by Starlette).

**Architectural smells:** 9 backend files and 4 frontend files exceed 500 LOC. Two endpoint modules (`programs.py`, `planning_center_sync.py`) reach directly into SQLAlchemy models — layering violation.

---

## 2. Automated Tests (§3.2)

**One-paragraph summary.** The suite is materially larger than May-9 acknowledged: **574 backend tests (56% coverage), 49 frontend specs (62% lines / 49.5% branches), 183 e2e tests**. Backend performance is healthy (slowest test 2.79s). But the e2e suite has **failed every run for ~7 weeks (since 2026-03-30)** because of a `PLAYWRIGHT_BASE_URL` config mismatch in `audit-and-security.spec.ts:351`, and nothing gates on it — alarm fatigue is total. 174 `waitForTimeout()` calls across 11 spec files (55 in `course-content-advanced.spec.ts` alone) are latent flake debt. Frontend has **zero specs** for 6 user-facing component trees (`enrollments`, `programs`, `audit`, `profile`, `members`, `activity-logs`). Full report: `/tmp/eval_2026-05-18/3.2_tests.md`.

**Top findings:**

| ID | File:Line | Severity | Issue |
|---|---|---|---|
| Q1 | `audit-and-security.spec.ts:351` + `utils/auth.ts:46` + `e2e-tests.yml:42` | **P0** | URL base-href mismatch: `PLAYWRIGHT_BASE_URL=https://apps.quentinspencer.com` (no `/churchcoursetracker`), but the helper at `utils/auth.ts:46` prefers PLAYWRIGHT_BASE_URL over the suffixed default. Test has failed every run for ~7 weeks. |
| Q2 | E2E workflow status | **P0** | 10/10 most-recent E2E runs failed; not gating merges; daily 02:00 UTC cron alarms ignored. |
| Q3 | `course-content-advanced.spec.ts` | **P1** | ~55 `waitForTimeout` calls (300ms–3000ms each). Flake time-bomb. |
| Q5 | `planning_center_sync_service.py` (1,907 LOC) | **P1** | 22% coverage; 1,484 lines uncovered. The critical external integration is largely untested. |
| Q6 | `enrollment_service.py` | **P1** | 29% coverage of a core data path. |
| Q7 | `user_service.py` / `users.py` endpoint | **P1** | 34% / 39% coverage; consistent with the recent e2e `/users` flake (Q14). |
| Q8 | 6 component trees | **P1** | No Karma/Jasmine specs for `enrollments`, `programs`, `audit`, `profile`, `members`, `activity-logs`. |
| Q10 | Multiple e2e files | **P2** | Many tests gate assertions behind `if (status === 200)` — they silently pass on regressions. |
| Q11 | `backend/tests/conftest.py.bak` | **P2** | Stale backup file checked into the test tree. |
| Q13 | `backend-tests.yml:42-46,60` | **P2** | Lint failures and codecov upload silently swallowed by `continue-on-error: true`. |
| Q14 | `/users` e2e tests in 4 spec files | **P2** | Confirmed flake: failed in run `25999361995`, passed in `26003358514`, no code change. Token race after the `getApiAuthToken` refactor (`376bc92`). |

**Critical-path coverage matrix:**

| Workflow | Backend | Frontend | E2E |
|---|---|---|---|
| Login/Auth | ✅ | ✅ | ✅ |
| Course CRUD | ✅ | ✅ | ✅ |
| **Enrollment** | partial (svc 29%) | ❌ **no spec** | ✅ |
| Content upload | ✅ | ✅ | ✅ |
| Role assignment | ✅ | ✅ | ✅ |
| Audit log | ✅ | ❌ **no spec** | ⚠️ broken (Q1) |
| Password change | ✅ | partial | indirect |
| User profile | ✅ | ❌ **no spec** | indirect |
| **Planning Center sync** | partial (svc 22%) | n/a | ❌ no e2e |
| Progress | partial (svc 25%) | ✅ | ✅ |

---

## 3. Deployment Scripts (§3.3)

**One-paragraph summary.** Terraform is drift-clean and well-organized (119 resources, 2,290 LOC across 11 files). The big findings are *not* in HCL — they are in (1) the **missing `.dockerignore`** which ships 827 KB of dev SQLite + `.env` + 3.4 MB `htmlcov/` into production, (2) **`deploy.yml` still using long-lived AWS access keys** despite OIDC infra existing and working for `deploy-docs.yml`, (3) **`backend/start.sh` running 22 `ALTER TABLE` + 2 `CREATE TABLE` at boot** with `# Don't exit` on failure, (4) **Terraform state stored locally** on one workstation (no S3 backend), and (5) **`scripts/create_admin_remote.py` hardcoding `ADMIN_PASSWORD = "admin123"`** — a leaked credential we missed in this session's sweep. Full report: `/tmp/eval_2026-05-18/3.3_deployment.md`.

**Top findings:**

| ID | File:Line | Severity | Issue |
|---|---|---|---|
| TF-01 | (no `backend "s3"` block) | **P0** | Terraform state is local-only on one workstation. State contains `random_password.db.result` (RDS master password). Laptop loss = state loss. |
| GH-01 | `deploy.yml:26-30,158-163` | **P0** | Production deploy uses long-lived AWS access keys. OIDC infra (`github_actions_oidc.tf`) exists and `deploy-docs.yml` already uses it. Half-migration. |
| DK-01 | `backend/Dockerfile.prod` (no `.dockerignore`) | **P0** | `COPY . .` pulls `.env`, `church_course_tracker.db` (827 KB), `backend.log`, `.coverage*`, `htmlcov/` (3.4 MB), `venv*/`, `tests/`. All ships to prod image. |
| SC-01 | `scripts/create_admin_remote.py:13,28` | **P0** | `ADMIN_PASSWORD = "admin123"` hardcoded, POSTed at live API. The May-18 credential sweep missed this script. |
| SS-01 | `backend/start.sh:99-786,788-797` | **P0** | 22 inline `ALTER TABLE` + 2 `CREATE TABLE` at every boot. `# Don't exit` on failure → schema corruption can pass `/health`. |
| TF-02 | `secrets.tf:57-63`, `main.tf:62-63` | **P1** | RDS master password lives in 3 places (TF state, Secrets Manager, RDS) instead of `manage_master_user_password = true`. Manual three-step rotation ritual. |
| GH-02 | `deploy.yml` (top of file) | **P1** | No top-level `permissions:` block. Default `GITHUB_TOKEN` permissions are write-all. |
| DK-05 | `frontend/.../Dockerfile:11` | **P1** | `npm ci --only=production` + `npm run build --prod` — wrong (Angular CLI is a devDependency; `--prod` is invalid). Build would fail. Likely dead file. |
| TF-03 | `secrets.tf:30-42` | **P2** | `app_secrets` bootstrap holds placeholder strings; `lifecycle.ignore_changes` mitigates but the foot-gun remains. |
| TF-04 | `main.tf` (758 LOC) | **P2** | Mixes VPC, RDS, three S3 buckets, CloudFront, Route 53, ACM, NAT. Split into `vpc.tf`/`rds.tf`/`s3.tf`/etc. |
| GH-04 | `deploy.yml:58-91` | **P2** | "Wait for service stable" can exit 0 even when `aws ecs wait` fails, if `runningCount == desiredCount` at the fallback check. |
| DK-03 | `backend/Dockerfile.prod` | **P2** | Single-stage build leaves `gcc`, `g++`, `libpq-dev` in the runtime image. |
| SS-03 | `backend/start.sh` (no locking) | **P2** | Per-task DDL has no transactional locking. Breaks the first time `desired_count > 1`. |

**`backend/start.sh` inline DDL catalog (estimated 8–10 Alembic revisions to factor out):**

```
people: campus_id + campus_assigned_date + FK + index
courses: 7 columns (planning_center_event_*, event_*_date, max_capacity, current_registrations, content_unlock_mode, max_file_size_mb)
course_enrollment: course_instance_id, assigned_teacher_id + 2 FKs
role: created_by, updated_by
course_modules: title
course_content: multiple columns + module_name nullable + content_audit_logs, content_access_logs (CREATE TABLE)
users: username, last_login
audit_log: changed_by, changed_at, ip_address, user_agent
8 tables: data_source, csv_loaded_at (looped)
```

**scripts/ audit:** 47 files; ~7 active, ~32 orphan candidates (~15 cleanly removable, ~17 worth moving to `scripts/ops/`).

**Missing tooling:** `tflint`, `tfsec`, `checkov`, `trivy` all absent. A future pass should re-run with these for security-scan severity counts.

---

## 4. Documentation (§3.4)

**One-paragraph summary.** 17 live `docs/*.md` + 148 archived + README + 7 infra status memos + 21 `docs-site/*.md` + 13 e2e work-logs. **No `CLAUDE.md` anywhere.** The single P0 is in README: it tells new devs to run `python create_default_admin.py` (deleted in this session's cleanup) and `cp .env.example .env` (file is `env.example`). The README also advertises Swagger UI at `/docs` which returns HTTP 404. Three P1 runbooks are missing: rollback, RDS password rotation, secrets-manager update. Onboarding composite: **5/10** (frontend dev server 8/10, e2e first-run 3/10). Inline Python docstring coverage is **>90%** on services and endpoints — the drift is in `.md` files, not in source. Full report: `/tmp/eval_2026-05-18/3.4_documentation.md`.

**Top findings:**

| ID | Path:Line | Severity | Issue |
|---|---|---|---|
| 1 | `README.md:135` | **P0** | `python create_default_admin.py` — script deleted in this session. New devs blocked. |
| 2 | `README.md:133` | **P1** | `cp .env.example .env` — file is `env.example`. Silent `cp` failure. |
| 3 | `README.md:207` | **P1** | Advertises `https://api.quentinspencer.com/docs` → HTTP 404. Only `/openapi.json` is reachable (149 endpoints). |
| 4 | `README.md:300` | **P1** | Links to non-existent `docs/CI_CD_SETUP.md`. |
| 5 | `README.md:567` | **P1** | Claims MIT LICENSE; no `LICENSE` file in repo. |
| 6 | `docs/PROJECT_STRUCTURE.md:59-69` | **P1** | Lists 6 docs that don't exist (`CURRENT_STATUS_AND_NEXT_STEPS.md`, `IMPLEMENTATION_PROGRESS.md`, etc.). The May-10 patch was incomplete. |
| 12–14 | (missing) | **P1** | No rollback runbook, no RDS-password-rotation runbook, no secrets-manager-update runbook. |
| 17 | (missing) | **P1** | No engineer-facing developer quickstart (vs. the end-user `GETTING_STARTED.md`). |
| 8 | `README.md:198-201` | **P2** | "Backend 95%+ / Frontend 90%+" coverage claims — unsupported. Real numbers (§3.2): 56% / 62%. |
| 9 | `README.md:614-620` | **P2** | "Version: 1.0.0 / Last Updated: January 2025" — wrong version (real: 0.74) + 16 months stale. |
| 10 | `docs/DOCUMENTATION_INDEX.md` | **P2** | Internal contradictions: 18 / 16 / sum-to-15 active doc counts; 125+ archives vs actual 148. |
| 15 | (missing) | **P2** | No incident response checklist. |
| 16 | (missing) | **P2** | No architecture diagram (only debug screenshots in `docs/images/`). |
| 19 | (missing) | **P3** | No root `CLAUDE.md` for LLM tooling. |
| 21 | `README.md:322-374` | **P3** | 50+ lines of Sentry setup duplicate `docs/LOGGING.md`. |

**Onboarding score:**

| Stage | Score | Notes |
|---|---|---|
| Local backend | 4/10 | README path broken (M-1, P0; `.env.example` rename) |
| Frontend dev server | 8/10 | Standard Angular flow; no `.nvmrc` |
| First backend test | 6/10 | README says `pytest`; `backend/tests/README.md` has detail but isn't linked |
| First e2e test | 3/10 | Top-level README doesn't mention env vars, browser install, or `tests/e2e/README.md` |
| **Composite** | **5/10** | ~1–2 hrs of friction for a careful new dev |

---

## 5. Outstanding Work (§3.5)

### 5.1 Closure status vs `EVALUATION_2026-05-09.md`

| Prior finding | Status | Evidence |
|---|---|---|
| §2.1 `GET /users` unauthenticated | ✅ **Closed** | `users.py:157,:188` adds `Depends(get_current_active_user)` |
| §2.2 Hardcoded admin password in README + `config.py:145` | ✅ **Closed** | `config.py:150` → `"CHANGE_ME_DEV_ONLY"` + production validator `:208-220`; README line 9 rewritten |
| §2.3 In-memory rate limiter | ❌ **Open** | `main.py:191-251` still `defaultdict(list)` |
| §3.1 Three version numbers | 🟡 **Partial** | `version.txt`, `environment.ts`, `environment.prod.ts` all `0.74`. `environment.dev.ts:5` still `0.65`. No build-time single source. |
| §3.2 Frontend subscription cleanup | 🟡 **Partial** | Mechanical sweep not done. 62 `subscribe()` sites vs 7 components with `destroy$`/`ngOnDestroy`. |
| §3.3 No `OnPush` change detection | ❌ **Open** | 0 occurrences across 16k LOC of frontend |
| §3.4 `httpx.Client()` per-request | ❌ **Open** | `users.py:318` + 4 sites in `planning_center_sync_service.py` |
| §3.5 `passlib==1.7.4` unused | ❌ **Open** | Still pinned, still imported in `user_service.py:178` |
| §4 SNS placeholder email | ✅ **Closed** | `cloudwatch.tf:157-161` uses `var.alert_email` with regex validation |
| §4 NAT instance AMI churn / hardcoded domains | ✅ **Closed** | `9882670` "stop terraform plan churning the NAT instances on every AMI release"; `terraform.tfvars` cleartext password removed |
| §5 E2E flakiness | 🟡 **Partial** | `getApiAuthToken` helper added (`376bc92`); flake debt persists (174 `waitForTimeout` calls) |
| §6 Doc archival follow-through | 🟡 **Partial** | `DOCUMENTATION_INDEX.md` says archive happened; `PROJECT_STRUCTURE.md:59-69` still references deleted docs |
| §6 README coverage claims | ❌ **Open** | "95%/90%" still in README:198-201 with no committed report (real: 56%/62%) |

**Net:** **6 closed / 4 open / 3 partial** out of 13 substantive prior findings. The closed set covers all the active production risks the prior audit named. The remaining open items are tech-debt class.

### 5.2 New since the May-9 audit (this session's work)

| Commit | Effect |
|---|---|
| `bd01a01` | Switch live deployment to `ENVIRONMENT=production` |
| `e947b39` | Force `DEBUG=False` in production instead of just warning |
| `94f8b3c` | Move `DATABASE_URL` from plaintext env to Secrets Manager reference |
| `63d275a` / `d9823fd` | Replace `var.db_password` with `random_password.db`; remove cleartext from `terraform.tfvars` |
| `0711ef0` | `ignore_changes` on `app_secrets` to prevent clobbering live values |
| `fd2cf2b` | Retire the now-redundant service-discovery lambdas |
| `9882670` | Stop terraform plan churning the NAT instances on every AMI release |
| `c1c275a` | Remove standalone admin/test-user scripts and their callers |
| `921c0c2` | Scrub leaked credentials from one-off scripts and e2e fallbacks |
| `d51bc45` | Pipe E2E credentials from repository secrets to playwright |
| `376bc92` | Authenticate `/users` requests via shared `getApiAuthToken` helper |

### 5.3 In-code TODO/FIXME sweep

Repo-wide `git grep -nE "TODO|FIXME|XXX|HACK"` against `*.py` `*.ts` `*.tf` `*.sh` (excluding `venv`, `node_modules`, `docs/archive`, the `EVALUATION_2026-05-09.md` snapshot, and `scripts/{,backend-}get-pip.py` (whose compressed payloads contain stray `XXX` byte sequences)) returns **exactly one real TODO**:

```
backend/app/services/content_service.py:95: # TODO: Implement separate module audit logging if needed
```

The codebase carries essentially no in-code TODO debt. The deferred-work backlog comes entirely from this audit's per-area findings.

### 5.4 Open GitHub issues

`gh issue list --repo qspencer/church-course-tracker --state open` returned no open issues at audit time.

---

## 6. Recommended Next Steps

Total findings across all sections: **~90** (33 in §3.1, 18 in §3.2, 30 in §3.3, 23 in §3.4). The list below collapses them into themed work items with priority and effort.

### 6.1 P0 — This week

| # | Item | Effort | Sources |
|---|---|---|---|
| 1 | **Add auth to 9 unauthenticated endpoint modules.** `Depends(get_current_active_user)` on every route in `people.py`, `reports.py`, `courses.py` (reads), `enrollments.py`, `progress.py`, `system_settings.py`, `sync.py`, `autocomplete_suggestions.py`. Conditionally include `mock_planning_center.py` only in non-prod. | 4–6 hrs + careful integration test | §3.1 B1–B9 |
| 2 | **Delete `auth.py:210`** (the `@router.post("refresh")` typo registering `POST /api/v1/authrefresh`). | 5 min | §3.1 B11 |
| 3 | **Fix the e2e suite.** Address `audit-and-security.spec.ts:351` URL base-href mismatch (set `PLAYWRIGHT_BASE_URL` to the suffixed URL in `e2e-tests.yml:42`, or change `utils/auth.ts:46` to always append `/churchcoursetracker` for `apps.quentinspencer.com` host). Then make the workflow a required check on `main`. | 30 min code + 5 min admin setting | §3.2 Q1, Q2 |
| 4 | **Add `backend/.dockerignore`** excluding `.env*`, `*.db`, `*.log`, `.coverage*`, `htmlcov/`, `__pycache__/`, `venv*/`, `tests/`, `data/`, `*.md`. Rebuild and verify image shrinks. | 30 min | §3.3 DK-01 |
| 5 | **Delete `scripts/create_admin_remote.py`** (hardcoded `admin123`). Verify nothing references it. | 10 min | §3.3 SC-01 |
| 6 | **Move Terraform state to S3 backend** with DynamoDB locking + KMS encryption. `terraform init -migrate-state` from the current local file. | 1 hr | §3.3 TF-01 |
| 7 | **Migrate `deploy.yml` to OIDC** — drop long-lived `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` secrets in favor of the existing OIDC role (`deploy-docs.yml` is the reference pattern). Add a sibling `aws_iam_role.github_actions_app_deploy`. | 2 hrs + careful test | §3.3 GH-01 |
| 8 | **Fix README** — replace `python create_default_admin.py` with the actual admin-seeding instruction (Alembic migration runs at boot, but document the env vars). Fix `cp .env.example .env` → `cp env.example .env`. Update Swagger URL to `/openapi.json` or enable Swagger UI in prod. Remove unsupported 95%/90% coverage claims. | 1 hr | §3.4 #1–3, 8 |
| 9 | **Demote `auth.py:46-54` to `logger.debug`** — stop logging Authorization header / JWT preview at INFO. | 5 min | §3.1 B10 |

**P0 total effort: ~12 hrs of focused work.** Item 1 is the dominant cost; items 2/5/9 are 5–15 min each.

### 6.2 P1 — Within two weeks

| # | Item | Effort |
|---|---|---|
| 10 | **Run `npm audit fix`** in frontend to close the 3 lodash-es CVEs (non-breaking). Schedule Angular 18→19 migration for the XSS triple. | 30 min for lodash; 2–3 days for Angular 19 |
| 11 | **Add `manage_master_user_password = true` to RDS**; let AWS own rotation; remove `random_password.db` from Terraform. | 2 hrs |
| 12 | **Replace in-memory rate limiter** with Redis-backed (slowapi+Redis or fastapi-limiter). Multi-instance scaling becomes safe. | 1 day |
| 13 | **Move JWT from localStorage to HttpOnly cookie**; tighten CSP to nonce-based; remove `'unsafe-inline'` `'unsafe-eval'`. | 2 days |
| 14 | **Refactor `backend/start.sh`** — convert the 22 ALTER + 2 CREATE TABLE blocks into 8–10 Alembic revisions. Remove the `# Don't exit` failure-suppress. Move schema validation to CI. | 2–3 days |
| 15 | **Add Karma specs** for the 6 untested component trees: `enrollments`, `programs`, `audit`, `profile`, `members`, `activity-logs`. Smoke level (render + 1 happy + 1 error). | 3–5 days |
| 16 | **Add backend coverage** for `planning_center_sync_service.py` (22%→60%), `enrollment_service.py` (29%→70%), `user_service.py` (34%→70%). | 3–5 days |
| 17 | **Write three runbooks**: `docs/RUNBOOKS/ROLLBACK.md`, `RDS_PASSWORD_ROTATION.md`, `SECRETS_UPDATE.md`. | 4 hrs |
| 18 | **Write `docs/DEVELOPER_QUICKSTART.md`** distinct from the end-user `GETTING_STARTED.md`. | 2 hrs |
| 19 | **Fix `docs/PROJECT_STRUCTURE.md:59-69`** — drop the 6 non-existent doc references. | 15 min |
| 20 | **Fix `frontend/Dockerfile`** (`npm ci` not `--only=production`; `npm run build -- --configuration=production`). Or delete it if confirmed unused. | 30 min |
| 21 | **Drop `passlib` dependency** — replace `pwd_context.hash(...)` in `user_service.py:178` with `get_password_hash` from `app/core/security.py`. Remove from `requirements.txt`. | 1 hr |
| 22 | **Add top-level `permissions:` blocks** to all GH Actions workflows (least-privilege). | 30 min |
| 23 | **Fix sync of `environment.dev.ts:5`** — version 0.65 should be 0.74. Either wire the increment script to all three files, or read `version.txt` at build time. | 1 hr |

### 6.3 P2 — Within sprint

| # | Item | Effort |
|---|---|---|
| 24 | **Lift per-request `httpx.Client()`** to a module-level singleton or FastAPI lifespan-scoped `httpx.AsyncClient` (`users.py:318` + 4 sites in `planning_center_sync_service.py`). | 4 hrs |
| 25 | **Replace 174 `waitForTimeout()` calls** in e2e with `waitForSelector` / `waitForResponse` / `expect.poll`. Start with `course-content-advanced.spec.ts` (55 occurrences). | 1 week |
| 26 | **Split `planning_center_sync_service.py`** (3,473 LOC) into `pc_http_client.py`, `pc_mappers.py`, `pc_sync_jobs.py`, `pc_webhook.py`. | 3–5 days |
| 27 | **Split `programs.py`** (1,326 LOC) endpoint module into sub-routers. | 2 days |
| 28 | **Split `infrastructure/main.tf`** (758 LOC) into `vpc.tf`/`rds.tf`/`s3.tf`/`cloudfront.tf`/`dns.tf`/`nat.tf`. | 1 day |
| 29 | **Delete `config_prod.py` and `config_aws.py`** (dead code). | 15 min |
| 30 | **Re-enable `TrustedHostMiddleware`** behind ALB with appropriate health-check exception. | 4 hrs |
| 31 | **Move 32 orphan scripts** out of `scripts/`: ~15 delete cleanly, ~17 move to `scripts/ops/`. | 2 hrs |
| 32 | **Add `OnPush` change detection** to dashboard + long-list components. | 2 days |
| 33 | **Add subscription cleanup** to remaining 55 components using `subscribe()`. | 3 days |
| 34 | **Multi-stage `backend/Dockerfile.prod`** — drop `gcc`/`g++`/`libpq-dev` from runtime. | 2 hrs |
| 35 | **Remove `continue-on-error` from `backend-tests.yml` lint step**; gate merges on black/isort. | 30 min |
| 36 | **Fix `deploy.yml` "wait for stable"** — poll deployment rolloutState, not just running/desired counts. | 2 hrs |
| 37 | **Delete `backend/tests/conftest.py.bak`** and fix bare `except: pass` blocks in fixtures. | 1 hr |
| 38 | **Move fixture setup to `scope="session"`** in `backend/tests/conftest.py` (currently ~1.5s/test). | 4 hrs |
| 39 | **Tighten `if (status === 200)`-guarded assertions** in 12 e2e test sites. | 2 hrs |
| 40 | **Architecture diagram** — Mermaid in README showing CloudFront → API Gateway → ECS → RDS. | 2 hrs |
| 41 | **Move 7 `infrastructure/*.md` status memos to `docs/archive/`.** | 15 min |
| 42 | **Recompute and fix `docs/DOCUMENTATION_INDEX.md` counts**; add a CI doc-stats check. | 1 hr |
| 43 | **Bump base images**: pin `python:3.12-slim` by digest; bump `node:18-alpine` → `node:20-alpine` if frontend Dockerfile is retained. | 1 hr |
| 44 | **Sweep 149 `except Exception` sites** for the worst offenders (start with service-layer code). | 1 week |
| 45 | **Add `incident-response.md` runbook.** | 2 hrs |

### 6.4 P3 — Quarter

| # | Item |
|---|---|
| 46 | RDS `deletion_protection = true`, `skip_final_snapshot = false`, backup_retention >= 7 days. |
| 47 | NAT instance IMDSv2-required (`metadata_options { http_tokens = "required" }`). |
| 48 | Configure `aws_secretsmanager_secret_rotation` once `manage_master_user_password` is in place. |
| 49 | Add `LICENSE` file (README claims MIT). |
| 50 | Add root `CLAUDE.md` for LLM tooling. |
| 51 | Replace `: any` / `<any>` in 11 service-level sites with concrete schema types. |
| 52 | Drop `fastapi-cors==0.0.6` (dead dep). |
| 53 | Bump `fastapi`/`uvicorn`/`sqlalchemy`/`pydantic`/`httpx` from late-2023 versions. |
| 54 | Refresh archive: move January 2026 docs (`CODE_REVIEW_AND_IMPROVEMENTS.md`, `TEST_REVIEW_AND_IMPROVEMENTS.md`, `IMPROVEMENT_RECOMMENDATIONS.md`, `MISSING_FEATURES_IMPLEMENTATION_PLAN.md`) to `docs/archive/`. |
| 55 | Add `backend/README.md` and `frontend/.../README.md` pointer files. |
| 56 | Drop `:latest` ECR image tag push from `deploy.yml`. |
| 57 | Use `getpass()` instead of `input()` for password prompts in `scripts/setup-rds-env.py`. |
| 58 | Stale-doc archival: `backend/TEST_COVERAGE_ANALYSIS.md`, `TEST_COVERAGE_REVIEW_SUMMARY.md` → `docs/archive/`. |
| 59 | Replace `course-content-advanced.spec.ts` (1,946-line mega-spec) by splitting feature areas. |
| 60 | Install missing dev tooling: `ruff`, `bandit`, `mypy`, `pip-audit`, `eslint`, `tflint`, `tfsec`, `checkov`, `trivy`. Document in developer-quickstart. |

---

## 7. Appendix

### 7.1 Methodology

Per the [evaluation plan](../../../Documents/church-course-tracker/EVALUATION_PLAN_2026-05-18.md) §4: four parallel investigation streams (§3.1–§3.4) executed by general-purpose subagents writing findings to dedicated files in `/tmp/eval_2026-05-18/`. §3.5 synthesis and final composition executed in the main session after all four reports landed. Each finding required: file path + line (or command + output), severity (P0/P1/P2/P3), and a 1-sentence remediation.

Total elapsed time: ~30 minutes wall-clock for the four parallel investigations (longest agent: §3.2 at ~27 min due to two full pytest invocations), plus synthesis. The sequential alternative was estimated at 10–13 hours.

### 7.2 Tool commands run

| Tool | Where | Outcome |
|---|---|---|
| `terraform plan -no-color` | `infrastructure/` | "No changes" — clean |
| `terraform state list` | `infrastructure/` | 119 resources |
| `npx tsc --noEmit -p tsconfig.json` | `frontend/church-course-tracker/` | 0 errors |
| `npm audit --production --omit=dev` | `frontend/church-course-tracker/` | 10 high, 0 critical |
| `npm audit` | `tests/e2e/` | 0 vulnerabilities |
| `npm audit --omit=dev` | repo root | 0 vulnerabilities |
| `pytest --collect-only -q` | `backend/` | 574 tests collected |
| `pytest --cov=app --cov-report=term-missing` | `backend/` | 574 passed, 56% coverage in 460s |
| `pytest --durations=15` | `backend/` | Slowest test 2.79s; no test > 5s |
| `gh run list --workflow "E2E Tests" --limit 10` | repo root | 10/10 most-recent = failure |
| `gh run view 26003358514 --log-failed` | — | 1 failed, 123 passed, 60 skipped |
| `gh issue list --state open` | repo root | (none) |
| `git grep -nE "TODO|FIXME|XXX|HACK"` | repo root | 1 real TODO |

### 7.3 Tools that should have run but weren't installed

`ruff`, `bandit`, `mypy`, `pip-audit`, `flake8`, `eslint`, `tflint`, `tfsec`, `checkov`, `trivy`. Recommendation: add these to the dev-container image and to CI so the next audit cycle has security-scan severity counts. Listed as P3 item 60.

### 7.4 Per-area report files

All retained for future reference:

- `/tmp/eval_2026-05-18/3.1_code_quality.md` (22 KB, 165 lines, 33 findings)
- `/tmp/eval_2026-05-18/3.2_tests.md` (28 KB, 188 lines, 18 findings)
- `/tmp/eval_2026-05-18/3.3_deployment.md` (29 KB, 237 lines, 30 findings)
- `/tmp/eval_2026-05-18/3.4_documentation.md` (22 KB, 240 lines, 23 findings)
- `/tmp/eval_2026-05-18/tf_state.txt` (working file — terraform state listing)

### 7.5 Comparison to `EVALUATION_2026-05-09.md`

| Aspect | May-9 | May-18 |
|---|---|---|
| Audit scope | Backend code + secrets + infra | All five areas (code, tests, deploy, docs, outstanding) |
| Findings count | ~20 | ~90 |
| Method | Single-pass manual review | Five parallel agents + synthesis |
| Closure verification | n/a | 6/9 substantive findings closed |
| Tooling coverage | Manual review + grep | + `tsc`, `npm audit`, `pytest --cov`, `gh run list` |

The increased finding count is **not** evidence the codebase got worse; it's evidence the May-9 audit was narrower than ideal. The auth-gap finding alone (9 endpoint modules) was already true on May-9 but was not surfaced because the audit looked only at `/users`. The new evaluation pattern (parallel agents per area with explicit "verify what's there, find what's not" prompts) should be the template for the next cycle.

---

*Audit conducted 2026-05-18. Read-only — no files modified during the audit itself. Subsequent fixes informed by this report should reference the per-area files in `/tmp/eval_2026-05-18/` for finding-level detail.*
