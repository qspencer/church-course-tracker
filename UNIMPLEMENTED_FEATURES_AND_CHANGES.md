# Unimplemented Features and Required Application Code Changes

This document lists features that are tested but not yet fully implemented in the application code, as well as other changes needed based on test failures.

## Backend - Unimplemented Features

### 1. User Profile Management Endpoints

**Status:** ❌ Not Implemented

**Required Endpoints:**
- `PATCH /api/v1/users/me` - Update current user's profile
  - Should allow updating: `full_name`, `email`
  - Should NOT allow updating: `role`, `username`
  - Should return updated user object

**Test Location:** `backend/tests/test_new_features.py::TestUserProfileUpdate`

**Implementation Notes:**
- Endpoint should be in `backend/app/api/v1/endpoints/users.py` or `auth.py`
- Should use current authenticated user from token
- Should validate that role cannot be changed
- Should update user in database and return updated user

---

### 2. Password Change Endpoint

**Status:** ❌ Not Implemented

**Required Endpoint:**
- `PATCH /api/v1/users/me/change-password`
  - Request body: `{ "current_password": "...", "new_password": "..." }`
  - Should verify current password before allowing change
  - Should hash new password before storing
  - Should return success message

**Test Location:** `backend/tests/test_new_features.py::TestChangePassword`

**Implementation Notes:**
- Endpoint should be in `backend/app/api/v1/endpoints/users.py` or `auth.py`
- Should verify current password using `verify_password()`
- Should hash new password using `get_password_hash()`
- Should return 400 if current password is incorrect
- Should return 200 with success message if password changed

---

### 3. Notification Preferences Endpoints

**Status:** ❌ Not Implemented

**Required Endpoints:**
- `GET /api/v1/users/me/preferences` - Get user notification preferences
- `PATCH /api/v1/users/me/preferences` - Update user notification preferences
  - Request body: `{ "email_notifications": true/false, "course_updates": true/false, "system_announcements": true/false }`

**Test Location:** `backend/tests/test_new_features.py::TestNotificationPreferences`

**Implementation Notes:**
- May require new `UserPreference` model if not already exists
- Should store preferences per user
- Should return default preferences if none set
- Should allow updating individual preference flags

---

### 4. Course Prerequisites Feature

**Status:** ❌ Not Implemented

**Required Endpoints:**
- `GET /api/v1/courses/prerequisites/available` - Get list of courses available as prerequisites
- `POST /api/v1/courses` - Should accept `prerequisites` array in request body
- `PATCH /api/v1/courses/{id}` - Should accept `prerequisites` array in request body
- Should validate that a course cannot be a prerequisite for itself

**Test Location:** `backend/tests/test_new_features.py::TestCoursePrerequisites`

**Implementation Notes:**
- May require new database table/model for course prerequisites relationship
- Should validate prerequisite relationships (no circular dependencies, no self-reference)
- Should return available courses (excluding current course when editing)
- Should store prerequisite relationships when creating/updating courses

---

### 5. Staff Activity Logs Endpoint

**Status:** ❌ Not Implemented

**Required Endpoint:**
- `GET /api/v1/audit/activity` - Get activity logs for staff users
  - Should return list of activity logs
  - Should be accessible to staff and admin roles

**Test Location:** `backend/tests/test_new_features.py::TestStaffActivityLogs`

**Implementation Notes:**
- May use existing audit log system
- Should filter or format logs appropriately for staff view
- Should respect role-based access (staff can see their own activity, admin can see all)

---

### 6. Enhanced Error Handling

**Status:** ⚠️ Partially Implemented

**Required Changes:**
- All 404 errors should return JSON format with:
  - `detail`: Error message
  - `status_code`: 404
  - `Content-Type`: `application/json`

**Test Location:** `backend/tests/test_new_features.py::TestErrorHandling`

**Implementation Notes:**
- May need custom exception handlers in FastAPI
- Should ensure all endpoints return JSON errors, not HTML
- Should apply to:
  - Course endpoints (`/api/v1/courses/{id}`)
  - Content endpoints (`/api/v1/content/{id}`)
  - Other resource endpoints

---

### 7. Account Lockout Feature

**Status:** ⚠️ Partially Implemented

**Current State:** Basic lockout tracking exists but may not be fully functional

**Required Functionality:**
- Lock account after 5 failed login attempts
- Return HTTP 423 (Locked) status code when account is locked
- Clear failed attempts on successful login
- Show remaining attempts in error messages

**Test Location:** `backend/tests/test_new_features.py::TestAccountLockout`

**Implementation Notes:**
- `FailedLoginService` exists but may need fixes
- Should track failed attempts per username/email
- Should lock account for a configurable duration (e.g., 15 minutes)
- Should return appropriate error messages

---

## Backend - Test Fixes Needed (Not Application Code)

### 1. `test_get_course_content` Failure

**Issue:** Test expects endpoint `/api/v1/content/course/1` to return 200 with a list

**Possible Causes:**
- Endpoint may not exist or may have different path
- Endpoint may require different authentication
- Endpoint may return 404 if course doesn't exist

**Fix:** Update test to match actual endpoint behavior or create endpoint if missing

---

### 2. Other Failing Tests

- `test_download_content_not_found` - May need to adjust expected status codes
- `test_get_person_not_found` - May need to adjust expected status codes
- `test_get_sync_task_status_not_found` - May need to adjust expected status codes
- `test_rate_limiting_enabled` - May need to check if rate limiting is actually enabled

---

## Frontend - Test Fixes Needed (Not Application Code)

### 1. ModuleDialogComponent Tests

**Issues:**
- `should initialize form in edit mode with module data` - `isEditing` not set correctly
- `should update module successfully` - `dialogRef.close()` may not be mocked correctly
- `should handle update module error` - Error handling not working as expected

**Fix:** Update test setup to properly initialize component in edit mode and mock service responses

---

### 2. UserDialogComponent Tests

**Issues:**
- Error creating/updating user tests failing

**Fix:** Update test mocks to properly handle service responses and error cases

---

## Priority Recommendations

### High Priority (Core Functionality)
1. **User Profile Update** (`PATCH /api/v1/users/me`) - Basic user management
2. **Password Change** (`PATCH /api/v1/users/me/change-password`) - Security feature
3. **Enhanced Error Handling** - Better API responses

### Medium Priority (User Experience)
4. **Notification Preferences** - User customization
5. **Account Lockout** - Complete implementation of existing partial feature

### Low Priority (Advanced Features)
6. **Course Prerequisites** - Advanced course management
7. **Staff Activity Logs** - Enhanced audit features

---

## Notes

- All tests in `test_new_features.py` are currently ERROR status, indicating these features are not implemented
- The 5 FAILED tests may be due to test issues rather than missing features - these should be investigated
- Frontend test failures appear to be test setup/mocking issues rather than application bugs

