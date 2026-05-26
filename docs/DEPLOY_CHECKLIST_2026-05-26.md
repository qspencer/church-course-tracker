# Deploy Checklist — Angular 21 Migration + Route Reorganization

**Cumulative scope of the change:**
- Angular 18 → 21 (zero NgModules remain; full standalone migration)
- Initial bundle: 2.07 MB → 1.45 MB (−30%)
- Routes reorganized: `/users`, `/audit`, `/settings` → `/admin/*`; `/profile`, `/activity-logs` → `/account/*`
- Class-based guards → functional guards (`CanActivateFn`)
- E2E hygiene: `cdk-overlay-backdrop` timeouts bumped, `skipIfMissing` helper introduced

**Commits to deploy** (everything since baseline at start of session):
- Angular major bumps: `5256db8` v19, `b47a2a1` v20, `7ba0d0e` v21
- Standalone migration: `3c0faa7`, `ca1de60`, `d8dd7f1`, `e586d3a`, `baa4673`
- Lazy `loadComponent`: `316631e`, `0607c44`
- Route reorganization: `d7576a0`, `a073af1`, `e3a7f01`
- Tech-debt sweep: `19b62fb`, `d5c1f8f`, `41e411a`

**Note:** Deploys auto-trigger on push to `main` via `.github/workflows/deploy.yml`. This checklist is for verifying the auto-deploy and catching regressions, **not for manually deploying**.

---

## 1. Pre-deploy verification

Run from `main` at the latest commit you intend to deploy.

- [ ] `git status` clean, on `main`, `git pull` up to date
- [ ] Backend tests pass: `cd backend && source venv/bin/activate && pytest` — expect **651 passed**
- [ ] Frontend unit tests pass: `cd frontend/church-course-tracker && CHROME_BIN=$(which chromium) npx ng test --watch=false --browsers=ChromeHeadless` — expect **851 passed**
- [ ] Production build clean: `cd frontend/church-course-tracker && npx ng build --configuration production` — expect 0 errors, 0 warnings
- [ ] Confirm the main chunk size in the build output is **~1.45 MB** (sanity check that the 600 kB win is intact)
- [ ] Optional but recommended: targeted local e2e smoke (~10 min)
  - Start backend (`uvicorn main:app --port 8000`) + frontend (`ng serve --port 4200`)
  - Run: `cd tests/e2e && npx playwright test --project=chromium -g "Admin can create new users|Admin can access system settings|Admin can filter audit logs"` — expect all 3 to pass

## 2. Auto-deploy verification

After `git push origin main`:

- [ ] GitHub Actions `deploy.yml` workflow starts within ~30s
- [ ] Backend tests job passes (`backend-tests.yml`)
- [ ] Frontend tests job passes (`frontend-tests.yml`)
- [ ] `deploy-backend` job: backend image builds, pushes to ECR, ECS service updates
- [ ] `deploy-frontend` job: `aws s3 sync ... --delete` removes old chunk files, new chunks uploaded
- [ ] CloudFront invalidation succeeds (look for `aws cloudfront create-invalidation` step in deploy log)
- [ ] Version-bump commit appears on `main` (auto: `Auto-increment version to X.YY [skip ci]`)

If any job fails, the deploy halts before reaching production. **Do not manually retry** — investigate the failure first.

## 3. Post-deploy smoke (must be done — this is the highest-risk deploy in months)

URL: https://apps.quentinspencer.com/churchcoursetracker

### 3.1 Hard refresh + console
- [ ] Open in **incognito** (avoids stale browser cache from prior session)
- [ ] Open browser DevTools → Console → no red errors on initial page load
- [ ] DevTools → Network → confirm `main.*.js` is ~350 kB transfer / ~1.45 MB raw (the new size)

### 3.2 Login flow per role
- [ ] Log in as **admin** → lands on `/dashboard` → sidebar shows all sections including Administration
- [ ] Log out → log in as **staff** → no Administration section in sidebar
- [ ] Log out → log in as **viewer** → no Administration section, limited features visible

### 3.3 Every top-level route loads
For each, **click the sidebar link** (not just `goto` — verifies routerLink wiring):
- [ ] `/dashboard` — stats render, no console errors
- [ ] `/courses` — course list renders
- [ ] `/programs` — programs list renders
- [ ] `/enrollments` — enrollments table renders
- [ ] `/progress` — progress data renders
- [ ] `/members` — members table renders
- [ ] `/reports` — reports renders

### 3.4 NEW routes (highest regression risk)
These paths didn't exist before this deploy. Test each:
- [ ] `/admin/users` — Users page loads, "Add User" button visible (admin only)
- [ ] `/admin/audit` — Audit log page loads, filters visible
- [ ] `/admin/settings` — Settings page loads, tabs render
- [ ] `/account/profile` — Profile form loads, fields populated
- [ ] `/account/activity-logs` — Activity log table renders

### 3.5 OLD route deprecation (expected behavior, verify it doesn't 404)
These bookmarks **will redirect to `/dashboard`** via the `**` catch-all (per "fully migrate" decision). Verify the redirect is clean (not a 404 page):
- [ ] `/users` → lands on `/dashboard`
- [ ] `/audit` → lands on `/dashboard`
- [ ] `/settings` → lands on `/dashboard`
- [ ] `/profile` → lands on `/dashboard`
- [ ] `/activity-logs` → lands on `/dashboard`

### 3.6 Guard enforcement (the bug that just bit us — explicit re-verification)
- [ ] As **staff** (non-admin), navigate to `/admin/users` directly via URL → should redirect to `/dashboard`
- [ ] As **viewer**, navigate to `/admin/settings` directly via URL → should redirect to `/dashboard`
- [ ] As **logged-out**, navigate to `/dashboard` directly → should redirect to `/auth`

### 3.7 Real-feature smoke
At least one create-update-delete cycle to confirm CRUD works end-to-end:
- [ ] As admin: create a test course → verify it appears in list → delete it
- [ ] As admin: open `/admin/audit` → confirm the create+delete you just did appear as recent audit entries

## 4. Monitoring window (first 30 min after deploy)

- [ ] CloudWatch backend logs: no spike in 5xx errors
- [ ] Sentry (if production error reporting active): no new error groups appearing
- [ ] CloudFront cache hit ratio recovering after invalidation (initial dip is expected)
- [ ] No browser console errors reported from any team member who happens to load the app

## 5. Rollback plan (in case of major regression)

The deploy pipeline does not auto-rollback. If something breaks badly:

**Backend rollback** (if needed — no backend changes in this deploy, so unlikely):
- ECS service has previous task definition in revision history
- Update service to previous revision via console or `aws ecs update-service --task-definition <prev-rev>`

**Frontend rollback** (more likely scenario given scope of frontend changes):
- Identify the last known-good commit before this session's work began (look for the commit before `5256db8`)
- `git revert <range>` to revert the cumulative changes, or `git push origin <known-good-sha>:main --force` (requires temporarily disabling branch protection)
- Once `main` reflects the rollback target, push triggers auto-deploy of the prior state
- After rollback, manually invalidate CloudFront: `aws cloudfront create-invalidation --distribution-id <id> --paths '/*'`

**Partial rollback** (only the route reorganization, keep Angular 21):
- Revert the three route-restructure commits: `git revert d7576a0 a073af1 e3a7f01`
- Push to `main`, let auto-deploy run
- The flat route structure (`/users`, `/audit`, etc.) is restored; Angular 21 + standalone migration stays

## 6. Communication

Since "no one is using it currently" per the project context, deploy comms can be minimal. If that changes:

- [ ] Inform any internal users that admin/account URLs have moved (`/users` → `/admin/users`, etc.)
- [ ] Note that the redirect-to-dashboard fallback means bookmarks don't 404 — they just land on dashboard instead of the intended page

---

## Reference: what could go wrong and how to recognize it

| Symptom | Likely cause | Where to look |
|---|---|---|
| Admin user lands on `/dashboard` when navigating to `/admin/users` | Functional-guard regression or AuthService user state lost | Browser DevTools console — look for `TypeError: guard is not a function` or `currentUser$` being null. Re-check commit `19b62fb` (functional guards) and `e3a7f01` (canActivateChild removal) deployed. |
| Page loads but Material widgets unstyled / missing | Material 3 theme not loading correctly | Network tab — look for missing `.scss`-compiled CSS or wrong stylesheet path. |
| All admin/* and account/* routes 404 | Route table not loading; check whether `app.routes.ts` made it into the bundle | Network tab — look for routing config in the main chunk. |
| Sidebar Administration section missing for admin user | `isAdmin()` returns false; check the AuthService stored user shape | Browser localStorage — inspect `currentUser` key; role should be `"admin"` lowercase. |
| Login succeeds but routes immediately redirect to `/auth` | AuthGuard's `isAuthenticated$` returning false; possibly stale localStorage token | Clear localStorage + retry. If reproducible, check the auth.service.ts behavior with the new functional guard. |
| First-paint very slow | CloudFront cache miss expected for ~5 min after invalidation; should self-resolve | CloudFront cache statistics. |
