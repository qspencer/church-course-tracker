# Instructions to Activate Admin User

## Problem
The Admin user is inactive in the database, causing 8 API authentication tests to skip.

## Solution
Activate the Admin user by setting `is_active = true` in the database.

## Method 1: Using Python Script (Recommended)

Run from a machine with database access:

```bash
cd /home/ubuntu/Dev/church-course-tracker
python3 scripts/update_aws_admin_user.py
```

This script will:
1. Connect to AWS RDS PostgreSQL database
2. Find the Admin user
3. Set `is_active = True`
4. Test the login

## Method 2: Direct SQL (If you have psql access)

```bash
PGPASSWORD=church_course_tracker_password psql \
  -h church-course-tracker-db.cmn082g02d5u.us-east-1.rds.amazonaws.com \
  -U postgres \
  -d church_course_tracker \
  -c "UPDATE users SET is_active = true WHERE username = 'Admin';"
```

## Method 3: Via API (If you have another active admin)

```bash
python3 scripts/activate_admin_via_api.py
```

## Verification

After activating, test the login:

```bash
curl -X POST 'https://tinev5iszf.execute-api.us-east-1.amazonaws.com/api/v1/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"Admin","password":"Admin123!"}'
```

Expected response: `200 OK` with access_token

## Test the Fix

Run the 8 API authentication tests:

```bash
cd tests/e2e
npx playwright test \
  api-improvements.spec.ts:227 \
  api-tests.spec.ts:44 \
  comprehensive-test-suite.spec.ts:169 \
  comprehensive-test-suite.spec.ts:224 \
  comprehensive-test-suite.spec.ts:251 \
  comprehensive-test-suite.spec.ts:459 \
  comprehensive-test-suite.spec.ts:486 \
  comprehensive-test-suite.spec.ts:512 \
  --project=chromium \
  --reporter=line
```

All 8 tests should now pass instead of being skipped.
