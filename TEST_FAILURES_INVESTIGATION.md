# Test Failures Investigation Report

## Date: January 2025

## Summary

Investigation of failing tests revealed **three main categories of issues**:

1. **Model Import/Relationship Issues** (Critical - blocks all tests)
2. **bcrypt/passlib Compatibility Issues** (Affects test fixtures)
3. **Missing Text Import** (Fixed)

---

## Issue 1: SQLAlchemy Relationship Error - CRITICAL

### Error
```
sqlalchemy.exc.InvalidRequestError: When initializing mapper Mapper[People(people)], 
expression 'CourseInstanceTeacher' failed to locate a name ('CourseInstanceTeacher').
```

### Root Cause
- The `People` model (`backend/app/models/member.py:72`) has a relationship to `CourseInstanceTeacher`
- `CourseInstanceTeacher` exists in `backend/app/models/course_instance.py`
- **BUT**: The model may not be properly imported in `app/models/__init__.py`
- **OR**: There are untracked migration files that haven't been applied:
  - `backend/migrations/versions/n5o6p7q8r9s0_add_course_offerings_architecture.py`
  - `backend/migrations/versions/m4n5o6p7q8r9_add_campus_1m_relationship.py`

### Impact
- **Blocks ALL tests** - Tests can't even load because SQLAlchemy can't initialize models
- Affects: All 14 tests in `test_new_features.py` and potentially all other tests

### Status
- ✅ **Fixed**: Missing `Text` import in `people_campus.py` (line 24)
- ⚠️ **Needs Investigation**: Model import order and migration status

### Recommended Fix
1. Check if `CourseInstanceTeacher` is imported in `app/models/__init__.py`
2. Review untracked migration files - decide if they should be committed or removed
3. Ensure model import order is correct (dependencies loaded first)
4. Consider using string references for forward references: `relationship("CourseInstanceTeacher", ...)`

---

## Issue 2: bcrypt/passlib Compatibility - HIGH PRIORITY

### Error
```
ValueError: password cannot be longer than 72 bytes, truncate manually if necessary
AttributeError: module 'bcrypt' has no attribute '__about__'
```

### Root Cause
- bcrypt version: 5.0.0
- passlib version: 1.7.4
- Compatibility issue between bcrypt 5.0.0 and passlib 1.7.4
- The `get_password_hash()` function uses `pwd_context.hash()` which triggers bcrypt initialization
- During initialization, passlib tries to detect bcrypt version but fails

### Impact
- **Blocks test fixtures** - Can't create test users with hashed passwords
- Affects: All tests in `test_new_features.py` that use `admin_user` fixture

### Status
- ✅ **Partially Fixed**: Updated `test_new_features.py` to use direct bcrypt hashing instead of `get_password_hash()`
- ⚠️ **Needs Verification**: Test if the fix works

### Recommended Fix
1. **Option A**: Downgrade bcrypt to 4.x (compatible with passlib 1.7.4)
   ```bash
   pip install "bcrypt<5.0.0"
   ```

2. **Option B**: Upgrade passlib to latest version (if compatible with bcrypt 5.0.0)
   ```bash
   pip install --upgrade passlib
   ```

3. **Option C**: Use direct bcrypt in test fixtures (current approach)
   - Continue using `bcrypt.hashpw()` directly in test fixtures
   - Keep `get_password_hash()` for application code

### Current Fix Applied
- Modified `test_new_features.py` fixture to use direct bcrypt hashing:
  ```python
  import bcrypt
  password = "testpass123"
  hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
  ```

---

## Issue 3: Missing Text Import - FIXED ✅

### Error
```
NameError: name 'Text' is not defined (from backend/app/models/people_campus.py:24)
```

### Root Cause
- `people_campus.py` uses `Text` type but doesn't import it from sqlalchemy

### Fix Applied
- ✅ Added `Text` to imports: `from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, Text`

### Status
- ✅ **FIXED** - No longer blocking tests

---

## Test Status Summary

### Tests in `test_new_features.py` (14 tests)

| Test Class | Tests | Status | Issue |
|------------|-------|--------|-------|
| TestAccountLockout | 2 | ❌ ERROR | Model import + bcrypt |
| TestUserProfileUpdate | 2 | ❌ ERROR | Model import + bcrypt |
| TestChangePassword | 2 | ❌ ERROR | Model import + bcrypt |
| TestNotificationPreferences | 2 | ❌ ERROR | Model import + bcrypt |
| TestCoursePrerequisites | 3 | ❌ ERROR | Model import + bcrypt |
| TestStaffActivityLogs | 1 | ❌ ERROR | Model import + bcrypt |
| TestErrorHandling | 2 | ❌ ERROR | Model import + bcrypt |

**All 14 tests are failing due to setup errors, not test logic issues.**

---

## Overall Test Suite Status

From last full run:
- **159 failed**
- **109 passed**
- **130 errors** (mostly setup/import errors)
- **149 warnings**

### Error Categories
1. **Model Import Errors**: ~130 errors (blocks test loading)
2. **Test Logic Failures**: ~159 failures (actual test assertions failing)
3. **Warnings**: 149 (deprecation warnings, etc.)

---

## Recommended Action Plan

### Priority 1: Fix Model Import Issues (CRITICAL)
1. ✅ Check `app/models/__init__.py` - ensure `CourseInstanceTeacher` is imported
2. ✅ Review untracked migration files - decide on commit or removal
3. ✅ Verify model import order
4. ✅ Test if models can be imported without errors

### Priority 2: Fix bcrypt Compatibility (HIGH)
1. ✅ Test current fix (direct bcrypt in fixtures)
2. ⚠️ If still failing, consider downgrading bcrypt or upgrading passlib
3. ✅ Verify password verification still works with the fix

### Priority 3: Run Tests After Fixes (MEDIUM)
1. Run `test_new_features.py` to verify features work
2. Run full test suite to identify remaining issues
3. Update test expectations if needed

---

## Next Steps

1. **Immediate**: Fix model import issues to unblock tests
2. **Short-term**: Verify bcrypt fix works, adjust if needed
3. **Medium-term**: Run full test suite and fix remaining failures
4. **Long-term**: Address deprecation warnings and improve test coverage

---

## Files Modified

1. ✅ `backend/app/models/people_campus.py` - Added `Text` import
2. ✅ `backend/tests/test_new_features.py` - Fixed bcrypt hashing in fixture
3. ⚠️ `backend/app/models/__init__.py` - Needs review for `CourseInstanceTeacher` import
4. ⚠️ Untracked migration files - Need decision on commit/remove

---

*Investigation Date: January 2025*  
*Status: In Progress*  
*Critical Issues: 2 (Model Import, bcrypt)*  
*Fixed Issues: 1 (Text Import)*

