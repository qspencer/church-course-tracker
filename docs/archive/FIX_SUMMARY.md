# Admin Authentication Fix - Root Cause Analysis

## Problem Identified

### Issue
- Admin login failing with "Incorrect username or password"
- BCrypt hashes were being created but not verifying

### Root Cause
**Password hash format mismatch:**

1. **Admin Script** (create_admin_standalone.py):
   - Was using `bcrypt.hashpw()` directly
   - Created raw bcrypt hashes

2. **Application** (security.py):
   - Uses `passlib.context.CryptContext`
   - Expects passlib-formatted hashes
   - Fallback to SHA256 for old admin users

### The Mismatch
- Passlib wraps bcrypt hashes with its own format
- Direct bcrypt hashes ≠ passlib bcrypt hashes
- Even though both use bcrypt internally, the formats differ

## Solution Applied

### Fix (Commit 1a3f08c)
Updated admin script to use the **exact same** password hashing method as the application:

```python
# Use same CryptContext configuration as application
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

# Hash password using passlib (same as get_password_hash)
hashed_password = pwd_context.hash(simple_password)
```

### Why This Works
- Uses same `CryptContext` with same `bcrypt__rounds=12`
- Creates hashes in passlib format
- `pwd_context.verify()` in security.py will now match

## Expected Result

After deployment:
- ✅ Admin user will be created with passlib-formatted hash
- ✅ Login will work with `Admin/<REDACTED>`
- ✅ Tests will pass

## Next Steps

1. Wait for GitHub Actions deployment (~10-15 min)
2. Test admin login
3. Run E2E tests

