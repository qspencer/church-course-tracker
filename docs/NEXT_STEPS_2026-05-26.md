# Next Steps — 2026-05-26

Forward-looking checklist after the **Angular 18 → 21 migration + route reorganization + tech-debt sweep + CI Node fix** landed in production today.

Related documents:
- `ROADMAP_2026-05-25.md` — the original Angular 21 migration plan (most items now ✅ shipped)
- `DEPLOY_CHECKLIST_2026-05-26.md` — the per-deploy verification template

---

## 1. Immediate — finish this deploy's verification (today)

These are still open from today's deploy:

- [ ] **Run manual sections A–E** of the deploy smoke (admin login → sidebar visibility → new routes → old route redirects → CRUD smoke → console errors). Documented in the conversation; I'll re-paste the bite-sized checklist on request.
- [ ] **Watch first 24h** for production anomalies:
  - CloudWatch backend logs — no spike in 5xx
  - Sentry — no new error groups (if production error reporting is active)
  - Any user reports

If any of A–E fail, the rollback plan in `DEPLOY_CHECKLIST_2026-05-26.md` §5 has three tiers (full, frontend-only, partial-revert-of-routes-only).

## 2. Patch DEPLOY_CHECKLIST.md with the lesson learned (this week)

Today's near-miss was that **the frontend deploy job had been failing silently for ~10 commits** while the backend job (independent) succeeded. The auto-version-bump still ran after every push, masking the fact that frontend never shipped.

Update `DEPLOY_CHECKLIST_2026-05-26.md` §2 to add:

```
- [ ] Verify BOTH the `deploy-backend` AND `deploy-frontend` jobs
      succeeded — they're independent jobs in the same workflow,
      and one can fail while the other passes. The auto-version-bump
      runs regardless of frontend success.
```

Better yet: **add a smoke-test step to `deploy.yml`** that runs after the frontend deploy completes, hits the production URL, and fails the workflow if the new chunk hash isn't being served. That would have caught today's issue automatically.

## 3. Short-term tech debt — within 2 weeks

### 3.1 GitHub Actions Node 24 migration
The CI deprecation banner noted: `actions/checkout@v4` and `actions/setup-node@v4` internally use Node 20, which will be removed September 2026. The runner is also defaulting to Node 24 starting June 2nd, 2026.

- [ ] Bump action versions and explicitly opt into Node 24:
  ```yaml
  env:
    FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: 'true'
  ```
- [ ] Verify all three workflows still pass

### 3.2 Pin Node version more strictly
Currently the version constraint is **only** in `.github/workflows/*.yml`. There's no `.nvmrc` or `engines` field in `package.json` to catch local-dev drift. Add:

- [ ] `frontend/church-course-tracker/.nvmrc` with `22`
- [ ] `engines: { "node": ">=22.12" }` in `frontend/church-course-tracker/package.json`

This ensures developers running locally with Node 18 get an immediate warning, not silent runtime breakage.

### 3.3 Run full e2e suite against production once it's stable
We ran the e2e suite locally during validation but never against the deployed production. Once the deploy is settled (>24h, no incidents):

- [ ] `cd tests/e2e && APP_BASE_URL=https://apps.quentinspencer.com/churchcoursetracker npx playwright test --project=chromium`
- [ ] Triage any new failures; most should be either (a) pre-existing flakes from the prior triage, or (b) tests that need real production data the local SQLite didn't have.

### 3.4 Production admin password rotation
While verifying, the prod admin account hit **1 of 5 failed-login attempts** (my credential probe). The remaining 4 attempts are intact, but if anyone manually probes it again it'll lock.

- [ ] Decide whether to keep the lockout policy at 5 attempts or relax it
- [ ] Document a runbook for unlocking the admin account if it does lock

## 4. Bucket 3 tech debt — deferred from today (within a quarter)

These were enumerated in the tech-debt sweep but intentionally deferred because of low cost-to-leave / high cost-to-fix.

### 4.1 `datetime.utcnow()` deprecation warnings (backend)
- Pre-existing 405 warnings during pytest runs
- Doesn't break anything; Python release cycle gives years of runway
- Mechanical sweep: ~30 min, find/replace `datetime.utcnow()` → `datetime.now(datetime.UTC)`
- Files: scan `backend/app/**/*.py` and `backend/tests/**/*.py`

### 4.2 `backend/start.sh` inline DDL → Alembic migrations
- The start script does some DDL inline (legacy of pre-Alembic era)
- Pre-existing tech debt; flagged in `EVALUATION_2026-05-18.md`
- ~1-2 hours: extract each inline DDL block into a proper Alembic migration revision

### 4.3 Remaining 34 silent-fallback e2e sites
- `tests/e2e/utils/skip-if.ts` introduced today (the `skipIfMissing` helper)
- 2 user-management tests converted as exemplars (commit `d5c1f8f`)
- The other 34 sites stay until natural touch — each has local nuance (keyboard.press('Escape'), retry loops) that mechanical conversion risks breaking
- Future tests should use `skipIfMissing` per the README guidance added in commit `41e411a`

### 4.4 `passlib` audit
- Removed in the May 2026 hardening pass (per session memory)
- Verify no residual references: `grep -rn "passlib" backend/`
- ~10 min if clean, longer if cleanup needed

## 5. Longer-term architectural decisions — bring up when triggered

### 5.1 Zoneless change detection
- Decided NOT to do during today's migration because the app's workload doesn't benefit (form-heavy CRUD, no high-frequency animation, no live dashboards)
- **Revisit if** the app grows into a workload where it matters: live progress charts, real-time data, virtualized lists, heavy animation
- ~30 kB gzip bundle savings + cleaner stack traces; ~1-2 days migration effort with significant audit risk

### 5.2 Angular Service Worker
- `@angular/service-worker` is in `package.json` but NOT configured in `angular.json`
- So no SW is currently running in production
- **Decide:** is offline support / faster repeat loads valuable enough to enable it?
- If yes: ~half a day to configure + test cache strategies + verify on iOS Safari (notoriously twitchy)
- If no: consider removing the dep to slim node_modules

### 5.3 Bundle budget tightening
- Current main chunk: 1.45 MB raw / 350 kB transfer
- `angular.json` warn threshold: 2 MB / error: 5 MB
- Could tighten warn to **1.6 MB** to catch creep early without alarming on current state
- ~5 min change

### 5.4 Auth flow modernization
- AuthService still uses BehaviorSubject + localStorage pattern
- Could migrate to signal-based auth state for better template integration
- **Trigger to do:** when adding any new auth-aware UI (e.g., a "Welcome, {{user}}" badge that should reactively update)
- ~1-2 hours

### 5.5 Convert remaining tests to standalone-friendly patterns
- 6 of the 9 smoke specs use `NO_ERRORS_SCHEMA` — fine for boot-only tests
- Behavioral tests for the same components are still using older patterns
- Ratchet: when behavioral tests get touched, migrate them to the modern pattern (signal-based queries, inject() in tests via `runInInjectionContext`)

## 6. Process improvements identified this session

### 6.1 Pre-commit smoke
Today's session repeatedly hit the auto-version-bump race: `git push` → rejected → `git pull --rebase` → push. Friction is mild but persistent.

- [ ] Option A: change CI to push the version bump to a different branch and merge via PR (substantial refactor)
- [ ] Option B: change CI to write the version into a `version.json` file as part of the build artifact, not commit it (medium refactor — version becomes per-deploy, not per-commit)
- [ ] Option C: live with it (current state)

Recommend B if developer experience matters; the version-as-commit pattern was never load-bearing for anything important.

### 6.2 Production smoke as CI gate
The Node 18 issue would have been caught immediately if `deploy.yml` had a final step that:
1. Curls `https://apps.quentinspencer.com/churchcoursetracker/`
2. Extracts the `main.*.js` hash from the response
3. Compares it to the just-built bundle hash
4. Fails the workflow if they don't match

That would turn "silent partial deploy failure" into a loud workflow failure that triggers actual investigation. ~30 min to add.

### 6.3 Branch protection on `main`
- We've been pushing directly to `main` because the project is solo / no users
- For multi-contributor work, would want PR-required protection + green CI before merge
- **Trigger to enable:** when a second contributor joins, or when production has real users

## 7. Things explicitly NOT recommended

For symmetry, here are items I considered and rejected:

- **Don't bump bundle budget to mask current state** — current main (1.45 MB) is well under the 2 MB warn. Tightening (not loosening) is the right direction.
- **Don't mass-convert remaining 34 silent-fallback sites** — risk-reward is unfavorable. Ratchet over time.
- **Don't go zoneless yet** — app workload doesn't justify the audit cost.
- **Don't add new framework dependencies casually** — the recent migration showed how much work it is to keep a dep chain modern. Keep additions principled.

---

## Quick reference — session deliverables summary

| Category | Status |
|---|---|
| Angular 18 → 21 migration | ✅ Shipped (14 commits, all NgModules eliminated, 600 kB bundle reduction) |
| Route reorganization (`/admin/*`, `/account/*`) | ✅ Shipped (with guard bug + fix in same session) |
| Functional guards (`CanActivateFn`) | ✅ Shipped |
| E2E hygiene (helpers, gitignore, README docs) | ✅ Shipped |
| CI Node 18 → 22 fix | ✅ Shipped (this was unblocking everything else!) |
| Deploy checklist artifact | ✅ Created (this doc + DEPLOY_CHECKLIST_2026-05-26.md) |
| Manual production smoke verification | ⏳ Pending (requires admin browser session) |
| Bucket 3 tech debt | 📋 Deferred (see §4) |
