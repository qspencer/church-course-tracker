# Application Evaluation — Church Course Tracker

**Date:** 2026-05-09
**Reviewer:** Code review pass over `main` branch
**Scope:** Backend (FastAPI), Frontend (Angular), Tests, Infrastructure (Terraform/AWS), Documentation
**Branch state:** `main`, with uncommitted changes in `backend/app/api/v1/endpoints/users.py`, `frontend/.../version.txt`, several `infrastructure/*.tf` files, and ~14 e2e specs

---

## TL;DR

The Church Course Tracker is a feature-complete, **production-deployed** Angular + FastAPI LMS with mature CI/CD, AWS infrastructure (ECS Fargate / RDS / CloudFront / API Gateway HTTP API), and a substantial test suite (548 backend tests, 829 frontend tests, ~366 e2e tests). The architecture is sound, and recent (Jan 2026) code-quality work cleared most of the deprecated-API debt.

However, the application is **not** in the "production-ready" state the README claims. Three classes of issue dominate:

1. **Two security findings that must be fixed before further public exposure** — an unauthenticated user-enumeration endpoint in production, and the production admin password committed to the repo *and* published in the README pointing at a live URL.
2. **Doc/code drift** — the docs describe a state ahead of the code in several places (completed phases that aren't, version numbers that disagree across three files), and below the code in others.
3. **E2E flakiness in active firefighting mode** — 14 of 19 specs modified, ~763 `waitForTimeout` calls across the suite. Stabilization work is ongoing rather than complete.

Fix priority order: security findings → version-number reconciliation → e2e stabilization → doc archival → frontend memory hygiene.

---

## 1. Architecture & Project Health

| Area | State | Comment |
|---|---|---|
| Backend layering | ✅ Good | Routes / services / models / schemas cleanly separated; 31 Alembic migrations — stable schema evolution |
| Frontend structure | ✅ Good | 27 components, 18 services, lazy-loaded routes, AuthGuard + AdminGuard properly applied |
| AWS infrastructure | 🟡 OK | Real ECS Fargate + RDS + CloudFront, but personalized to one domain and cost-cut to the edge of operational risk |
| CI/CD | 🟡 OK | 5 workflows, all live; backend lint failures suppressed via `continue-on-error` |
| Tests (unit) | ✅ Good | 68 backend test files, 49 frontend `.spec.ts` files |
| Tests (e2e) | ❌ Brittle | Hardcoded waits, large modified set, "active firefighting" |
| Documentation | 🟡 Bloated | 40+ active docs, much overlap; team's own Jan 2026 review identified 8 to archive |

`★ Insight ─────────────────────────────────────`
The presence of three Pydantic config files (`config.py`, `config_prod.py`, `config_aws.py`) plus three Dockerfiles per side (`Dockerfile`, `.dev`, `.prod`) is a recurring shape in this codebase: every concept gets a dev/prod fork rather than a single config keyed by environment. It works, but it's a doubled surface for drift bugs (e.g., the Sentry properties that went missing from `environment.dev.ts` in commit `206e931`). Keep this in mind when reading findings — most of the "X exists in file A but not file B" issues trace back to this pattern.
`─────────────────────────────────────────────────`

---

## 2. Critical Findings (fix before further public exposure)

### 2.1 Unauthenticated user enumeration — `GET /users`

**File:** `backend/app/api/v1/endpoints/users.py:150-160`

```python
@router.get("", response_model=List[User])
@router.get("/", response_model=List[User])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    role: str = None,
    db: Session = Depends(get_db)
):
    """Get all users, optionally filtered by role"""
    user_service = UserService(db)
    return user_service.get_users(skip=skip, limit=limit, role=role)
```

This endpoint is missing `Depends(get_current_active_user)`. **Verified by counting:** the file has 14 routes, 10 of which use `Depends(get_current_active_user)` — `GET /users` (this one) and `GET /users/{user_id}` (line 183) are not among them. The neighboring `bulk_delete_users` (line 167) and `create_user` (line 200) are properly guarded, which makes the omission look like an oversight rather than intentional.

**Impact:** Any unauthenticated client can enumerate the full user list (with usernames, emails, roles) and fetch any user by ID. Since the API is on a public domain (`api.quentinspencer.com`), this is exploitable today.

**Fix:** Add `current_user: dict = Depends(get_current_active_user)` to both endpoints. If the client truly needs unauthenticated user listing (it shouldn't), at minimum strip the response to non-PII fields.

### 2.2 Hardcoded admin password committed and publicly documented

**File 1 (the default in code):** `backend/app/core/config.py:145`
```python
ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "Matthew778*")
```

**File 2 (the same password in the public README):** `README.md:9`
```
Admin Credentials: Admin / Matthew778*
```
…directly under `Production Frontend: https://apps.quentinspencer.com`.

The README treats this as demo credentials, but `config.py:145` makes the same string the **runtime default** if the `ADMIN_PASSWORD` env var is unset, and `create_default_admin.py` will seed it. Together: the production deployment may already be using this password, and that password is published with the URL.

Other defaults in the same block (`STAFF_PASSWORD: "Staff123!"`, etc., lines 148-164) have the same problem at lower severity.

**Fix (immediate):**
1. Rotate the production admin password now.
2. Remove the README credentials line.
3. Change the `os.getenv(...)` defaults to `None`, then fail-fast at startup if unset (mirroring the `SECRET_KEY` validation that's already in `config.py`). This converts a silent default into a startup error — louder, but safer.

### 2.3 In-memory rate limiter doesn't survive horizontal scaling

**File:** `backend/app/main.py:192-251`

A dict-based rate limiter is configured on the app. It works for a single uvicorn process, but ECS Fargate runs multiple tasks/containers and any restart wipes state. In production this gives the *appearance* of rate limiting without the substance.

**Fix:** Use Redis-backed limiting (`slowapi` + Redis, or `fastapi-limiter`). Acceptable interim: be explicit in the README that rate limiting is per-instance only.

---

## 3. High-Priority Code Quality Issues

### 3.1 Three different version numbers in three files

| File | Version |
|---|---|
| `frontend/church-course-tracker/version.txt` | `0.21` |
| `frontend/church-course-tracker/src/environments/environment.ts` | `0.65` |
| `frontend/church-course-tracker/src/environments/environment.prod.ts` | `0.06` |

The comment in `environment.ts:8` says *"This should match environment.prod.ts — will be replaced during build"*, but the build replacement is clearly not happening, and `version.txt` (auto-incremented by CI) has drifted from both. Sentry breadcrumbs and on-screen `appVersion` will report whichever file the bundle was built from — a debugging hazard.

**Fix:** Single source of truth — read `version.txt` (or `package.json`) at build time and inject. Delete the literal version strings from environment files.

### 3.2 Subscription cleanup is inconsistent in the frontend

**File:** `frontend/church-course-tracker/src/app/app.component.ts:27-31`
```typescript
ngOnInit(): void {
  this.authService.isAuthenticated$.subscribe(isAuth => {
    this.isAuthenticated = isAuth;
  });
  this.authService.currentUser$.subscribe(user => {
    this.currentUser = user;
  });
```

`AppComponent` declares `OnDestroy` but neither `subscribe()` is wrapped with `takeUntil(destroy$)` or async-piped. For the root component this is largely cosmetic (it lives as long as the app does), but the *pattern* is repeated in feature components — `MembersComponent`, `CoursesComponent`, several dialogs — where it does cause leaks across navigation. `DashboardComponent` shows the right pattern with `takeUntil` and is a good template.

**Fix:** Convert template-bound observables to `| async` where possible; add `destroy$` + `takeUntil(this.destroy$)` everywhere else. This is mechanical but worth a single sweep.

### 3.3 No `OnPush` change detection anywhere

Zero components use `ChangeDetectionStrategy.OnPush`. The dashboard with multiple Chart.js instances is the most exposed; perf will degrade with concurrent users or large list views. Not urgent, but worth a tracking ticket.

### 3.4 `httpx` client created per-request

**File:** `backend/app/api/v1/endpoints/users.py:312`

The Planning Center import endpoint instantiates an `httpx.Client()` inline. Each request opens a new connection pool. Should be a module-level (or app-startup) async client that's reused.

### 3.5 `passlib==1.7.4` dependency is unused and abandoned

**File:** `backend/requirements.txt`

`passlib`'s last release was 2019, and the codebase already uses `bcrypt` directly via `app/core/security.py`. Drop the dependency.

---

## 4. Infrastructure Concerns

| File:line | Issue | Severity |
|---|---|---|
| `infrastructure/cloudwatch.tf:158` | SNS alert endpoint = `admin@your-domain.com` (placeholder, never replaced) — alarms will be undeliverable | **High** |
| `infrastructure/main.tf:271, :604-614` | `apps.quentinspencer.com` and `api.quentinspencer.com` hardcoded in CloudFront aliases / Route53 records | Medium |
| `infrastructure/main.tf:38-39, :436-475` | `enable_nat_gateway = false` + DIY NAT instances with iptables `user_data` script — fragile to AMI changes | Medium |
| `infrastructure/main.tf:68, :72, :73` | RDS `backup_retention_period = 3`, `skip_final_snapshot = true`, `deletion_protection = false` | Medium |
| `infrastructure/iam.tf:60-77, :87-108` | S3 task role allows `DeleteObject` on uploads bucket; secrets policy allows `GetSecretValue` on full ARN with no version pin | Medium |
| `infrastructure/ecs.tf:9` | `containerInsights = "disabled"` | Low (cost vs. observability tradeoff) |

**Production posture summary:** the infra runs, but the *defensive* layers (alerting, backups, deletion protection, observability) are all dialled to "dev". A single bad migration plus the placeholder alert email = silent data loss. The placeholder email alone is a 5-minute fix and should be treated as urgent.

---

## 5. Test Suite Status

### Unit tests: healthy
- **Backend:** 68 test files, 14.5K lines. The team's own report (`BACKEND_TEST_RESULTS_SUMMARY.md`) cites 548/548 passing in 3m 48s. Mix of unit + integration; integration tests aren't in a dedicated folder, which makes them hard to run separately.
- **Frontend:** 49 `.spec.ts` files, ~829 cited as passing. Karma coverage thresholds are 80% locally but **0% in CI** (`karma.conf.js:29-44`). That is "coverage theatre" — drop coverage in CI to a real floor (60-70%) or remove the config to be honest.

### E2E tests: in active firefighting
- **19 spec files**, 14 currently modified per `git status`.
- `tests/e2e/utils/auth.ts:84, :159` uses literal `page.waitForTimeout(1000)` / `(500)` waits.
- Approximately 763 `waitForTimeout` calls across the suite (per the survey).
- Tests are credential-skip-aware (skip if `E2E_*_USERNAME` env vars are absent) — secure design, but means CI without secrets is silently skipping coverage.

The team's recent doc trail (`E2E_TEST_FIXES_APPLIED.md`, `E2E_TEST_FIXES_COMPLETE_SUMMARY.md`, `E2E_FINAL_IMPROVEMENTS_SUMMARY.md` — three "complete" reports) suggests stabilization has been declared "done" multiple times and re-opened. A single source-of-truth e2e dashboard or test report would help.

---

## 6. Documentation

The team's own `DOCUMENTATION_REVIEW_REPORT_JAN_2026.md` correctly identifies overlap: **8 historical completion reports flagged for archival**. Today there are ~40 active docs in `docs/` plus another ~25 deployment notes scattered across `infrastructure/`, `docs-site/`, and `session-logs/`. The signal-to-noise is poor.

Key contradictions found between docs:

1. `IMPROVEMENT_RECOMMENDATIONS.md` Phase 3 summary says broad-exception handlers were "Reduced from 138 to <10 instances" — yet the same file's Issue #5 still describes "90+ instances" (line 536). Same document, opposite claims.
2. `MISSING_FEATURES_IMPLEMENTATION_PLAN.md` lists course-content management as "not implemented", but `FRONTEND_TEST_RESULTS_SUMMARY.md` shows 4 course-content test files passing.
3. `CODE_QUALITY_IMPROVEMENTS_JAN_17_2026.md` declares Pydantic `.dict()` migrations done; `DEPRECATION_WARNINGS_ANALYSIS.md` (same date) lists them as still-open.
4. README claims "Test Coverage: Backend 95%+, Frontend 90%+" — there is no coverage report committed that supports either number, and CI thresholds are 0%.

---

## 7. Strengths Worth Preserving

It's a long list of issues, so to balance the picture:

- **Auth core is solid.** `app/core/security.py` uses bcrypt with configurable rounds, JWT validation rejects SHA256 hashes, the login endpoint has account-lockout (`app/api/v1/endpoints/auth.py:107-207`).
- **Migration discipline.** 31 Alembic migrations, server-default timestamps, pool_pre_ping enabled — this codebase has clearly survived real schema evolution.
- **Routing & guards are right.** All protected routes use `[AuthGuard]`, admin routes double-up with `[AdminGuard]`, all 14 lazy-loaded.
- **Real production deployment.** ECS Fargate + RDS + CloudFront + API Gateway HTTP API is genuine, not aspirational.
- **CI runs.** GitHub Actions deploy workflow exists and ships changes through ECR / ECS / S3 / CloudFront invalidation.
- **Recent code-quality work is real.** The `datetime.utcnow()` and TypeScript `any` cleanups (Jan 17, 2026) show up in the code, not just the docs.

---

## 8. Recommended Next Steps (prioritized)

### This week — security & honesty
1. **Add auth dependency to `GET /users` and `GET /users/{user_id}`** (`backend/app/api/v1/endpoints/users.py:150, :183`).
2. **Rotate the production admin password** and remove it from `README.md:9`. Change `config.py:145`-style defaults to `None` + fail-fast.
3. **Replace the SNS placeholder email** in `infrastructure/cloudwatch.tf:158` and `terraform apply`.
4. **Reconcile the three version numbers** to one source of truth.

### Next two weeks — quality
5. **E2E stabilization sprint:** pick *one* spec, replace every `waitForTimeout` with `expect(...).toBeVisible({ timeout })` or explicit network idle, then propagate the pattern. Stop declaring it "complete" until the modified-file count is zero.
6. **Frontend subscription sweep:** apply the `DashboardComponent` `takeUntil(destroy$)` pattern across feature components; convert template-bound observables to `| async`.
7. **Drop unused `passlib`** from `requirements.txt`.
8. **Move external HTTP client construction out of endpoints** into a singleton / lifespan dependency.

### Next month — durability
9. **Real rate limiting** (Redis-backed) before scaling beyond one ECS task.
10. **Tighten infra defaults:** RDS `deletion_protection = true`, longer backup retention, restore Container Insights, narrow IAM policies.
11. **Adopt `OnPush`** on dashboard and reports first.
12. **Documentation triage:** archive the 8 reports the team's own review flagged, plus the duplicates surfaced here. Aim for one canonical doc per topic.

### Ongoing — process
13. **Stop writing dated "completion" reports** as canonical docs. Use commit messages and PR descriptions for moment-in-time work; reserve `docs/` for evergreen content (USER_GUIDE, FEATURES, ERROR_HANDLING, etc.).
14. **Add a CI check** that fails if `README.md` claims, environment versions, and coverage thresholds drift.

---

## 9. Risk Summary (one-line each)

- **Confidentiality risk:** unauthenticated user enumeration + published admin password = pre-auth account compromise on the live site.
- **Integrity risk:** RDS deletion protection off + 3-day backup retention = a single accident is unrecoverable.
- **Availability risk:** in-memory rate limiting + DIY NAT instances + disabled Container Insights = thin operational margin.
- **Velocity risk:** doc volume and contradictions are slowing decisions; e2e flakiness is eroding trust in CI.

None of these are existential — the foundations are good. They are all addressable with bounded, well-defined work.

---

*Generated 2026-05-09 from a fresh read of the `main` branch. Findings cited with `file:line` references; verify against current source before acting.*
