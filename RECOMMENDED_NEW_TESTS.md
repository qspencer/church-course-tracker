# Recommended New Tests - Detailed Specification

## Overview

This document outlines the comprehensive test suite recommendations to improve test coverage from **60% to 80%** and address critical security and integration gaps. Based on the feedback analysis, these tests are prioritized by criticality and impact.

---

## 📊 Current Coverage Status

- **Overall Coverage**: 60% (2,437/4,032 statements)
- **Test Pass Rate**: 95.4% (289/302 tests passing)
- **Security Coverage**: 40% ❌ **CRITICAL GAP**
- **Planning Center Integration**: 11% ❌ **CRITICAL GAP**
- **CSV Loader**: 13% ❌ **CRITICAL GAP**
- **Service Layer**: 32-81% ⚠️ **NEEDS IMPROVEMENT**
- **Configuration**: 0-81% ⚠️ **NEEDS IMPROVEMENT**

---

## 🔴 Priority 1: Security Tests (40% → 70% coverage)

### Current State
- **Security Module**: `app/core/security.py` (40% coverage)
- **User Service**: `app/services/user_service.py` (40% coverage)
- **Critical Gap**: JWT validation, authorization edge cases, account lockout

### Recommended Tests: ~20-25 new tests

#### 1. JWT Token Validation Edge Cases (6 tests)

**File**: `backend/tests/test_security.py`

##### Test 1.1: `test_verify_token_malformed_header`
```python
def test_verify_token_malformed_header():
    """Test verifying token with malformed JWT header"""
    # Input: Token with invalid header format
    # Expected: Returns None
    # Coverage: JWT decode error handling
```

##### Test 1.2: `test_verify_token_tampered_signature`
```python
def test_verify_token_tampered_signature():
    """Test verifying token with tampered signature"""
    # Input: Valid token format but modified signature
    # Expected: Returns None (signature verification fails)
    # Coverage: JWT signature verification
```

##### Test 1.3: `test_verify_token_missing_algorithm`
```python
def test_verify_token_missing_algorithm():
    """Test verifying token without algorithm claim"""
    # Input: Token missing algorithm in header
    # Expected: Returns None
    # Coverage: Algorithm validation
```

##### Test 1.4: `test_verify_token_wrong_algorithm`
```python
def test_verify_token_wrong_algorithm():
    """Test verifying token with wrong algorithm"""
    # Input: Token signed with different algorithm than expected
    # Expected: Returns None
    # Coverage: Algorithm mismatch handling
```

##### Test 1.5: `test_verify_token_empty_payload`
```python
def test_verify_token_empty_payload():
    """Test verifying token with empty payload"""
    # Input: Valid token structure but empty payload
    # Expected: Returns None (missing 'sub' claim)
    # Coverage: Payload validation
```

##### Test 1.6: `test_verify_token_non_numeric_sub`
```python
def test_verify_token_non_numeric_sub():
    """Test verifying token with non-numeric sub claim"""
    # Input: Token with sub="admin" (string instead of numeric)
    # Expected: Returns None or handles gracefully
    # Coverage: Sub claim type validation
```

#### 2. Authorization Edge Cases (5 tests)

**File**: `backend/tests/test_security.py` or `backend/tests/test_authorization.py`

##### Test 2.1: `test_get_current_admin_user_staff_role`
```python
def test_get_current_admin_user_staff_role(client: TestClient, staff_token):
    """Test admin-only endpoint access with staff role"""
    # Input: Staff user token accessing admin-only endpoint
    # Expected: 403 Forbidden
    # Coverage: Role-based access control (RBAC) enforcement
```

##### Test 2.2: `test_get_current_admin_user_viewer_role`
```python
def test_get_current_admin_user_viewer_role(client: TestClient, viewer_token):
    """Test admin-only endpoint access with viewer role"""
    # Input: Viewer user token accessing admin-only endpoint
    # Expected: 403 Forbidden
    # Coverage: RBAC viewer role restrictions
```

##### Test 2.3: `test_get_current_active_user_with_invalid_role`
```python
def test_get_current_active_user_with_invalid_role(client: TestClient, db_session):
    """Test accessing endpoint with invalid role claim"""
    # Input: Token with role="invalid_role"
    # Expected: 401 Unauthorized or 403 Forbidden
    # Coverage: Role validation
```

##### Test 2.4: `test_role_based_content_access_staff`
```python
def test_role_based_content_access_staff(client: TestClient, staff_token, db_session):
    """Test staff user can create/update but not delete content"""
    # Input: Staff token, attempt to delete content
    # Expected: 403 Forbidden
    # Coverage: Granular permission checks
```

##### Test 2.5: `test_role_based_content_access_viewer`
```python
def test_role_based_content_access_viewer(client: TestClient, viewer_token, db_session):
    """Test viewer user can only read content"""
    # Input: Viewer token, attempt to create content
    # Expected: 403 Forbidden
    # Coverage: Read-only role permissions
```

#### 3. Account Lockout Edge Cases (4 tests)

**File**: `backend/tests/test_security.py` or `backend/tests/test_account_lockout.py`

##### Test 3.1: `test_lockout_after_max_attempts`
```python
def test_lockout_after_max_attempts(client: TestClient, db_session):
    """Test account locks after MAX_FAILED_ATTEMPTS"""
    # Input: Multiple failed login attempts (MAX_FAILED_ATTEMPTS times)
    # Expected: Account locked, 423 Locked status
    # Coverage: Lockout threshold enforcement
```

##### Test 3.2: `test_lockout_duration_expiration`
```python
def test_lockout_duration_expiration(client: TestClient, db_session):
    """Test account unlocks after lockout duration expires"""
    # Input: Account locked, wait for LOCKOUT_DURATION_MINUTES + 1
    # Expected: Account unlocks automatically
    # Coverage: Lockout expiration logic
```

##### Test 3.3: `test_lockout_attempts_reset_after_success`
```python
def test_lockout_attempts_reset_after_success(client: TestClient, db_session):
    """Test failed attempts reset after successful login"""
    # Input: 2 failed attempts, then successful login, then failed attempt
    # Expected: Failed attempt count resets to 1 (not 3)
    # Coverage: Failed attempt counter reset
```

##### Test 3.4: `test_lockout_partial_attempts`
```python
def test_lockout_partial_attempts(client: TestClient, db_session):
    """Test account not locked with fewer than max attempts"""
    # Input: MAX_FAILED_ATTEMPTS - 1 failed attempts
    # Expected: Account not locked, can still login
    # Coverage: Lockout boundary condition
```

#### 4. Password Security Edge Cases (4 tests)

**File**: `backend/tests/test_security.py`

##### Test 4.1: `test_password_hash_different_salts`
```python
def test_password_hash_different_salts():
    """Test password hashing produces different hashes for same password"""
    # Input: Same password hashed twice
    # Expected: Different hash values (different salts)
    # Coverage: Salt generation uniqueness
```

##### Test 4.2: `test_verify_password_case_sensitivity`
```python
def test_verify_password_case_sensitivity():
    """Test password verification is case-sensitive"""
    # Input: Password "Password123!", hashed, verify with "password123!"
    # Expected: Returns False
    # Coverage: Case-sensitive password matching
```

##### Test 4.3: `test_verify_password_unicode_characters`
```python
def test_verify_password_unicode_characters():
    """Test password verification with unicode characters"""
    # Input: Password with unicode characters (e.g., "Pässwörd123!")
    # Expected: Correctly handles unicode
    # Coverage: Unicode password support
```

##### Test 4.4: `test_password_strength_common_passwords`
```python
def test_password_strength_common_passwords():
    """Test password strength validation rejects common passwords"""
    # Input: Common passwords like "password123", "12345678"
    # Expected: Returns False with appropriate message
    # Coverage: Common password rejection (if implemented)
```

#### 5. Session Management (3 tests)

**File**: `backend/tests/test_security.py` or `backend/tests/test_session.py`

##### Test 5.1: `test_token_refresh_before_expiry`
```python
def test_token_refresh_before_expiry(client: TestClient, admin_token):
    """Test token can be refreshed before expiry"""
    # Input: Valid token, call refresh endpoint
    # Expected: New token issued with extended expiry
    # Coverage: Token refresh logic
```

##### Test 5.2: `test_token_refresh_after_expiry`
```python
def test_token_refresh_after_expiry(client: TestClient, db_session):
    """Test token cannot be refreshed after expiry"""
    # Input: Expired token, call refresh endpoint
    # Expected: 401 Unauthorized
    # Coverage: Expired token handling
```

##### Test 5.3: `test_concurrent_token_refresh`
```python
def test_concurrent_token_refresh(client: TestClient, admin_token):
    """Test concurrent token refresh requests"""
    # Input: Multiple simultaneous refresh requests with same token
    # Expected: All requests succeed (idempotent) or handled gracefully
    # Coverage: Concurrent access handling
```

#### 6. Input Validation Edge Cases (3 tests)

**File**: `backend/tests/test_security.py`

##### Test 6.1: `test_sql_injection_in_username`
```python
def test_sql_injection_in_username(client: TestClient):
    """Test SQL injection attempt in username field"""
    # Input: Username: "admin'; DROP TABLE users; --"
    # Expected: 401 Unauthorized (handled safely, no SQL execution)
    # Coverage: SQL injection prevention
```

##### Test 6.2: `test_xss_in_content_fields`
```python
def test_xss_in_content_fields(client: TestClient, admin_token, db_session):
    """Test XSS prevention in content fields"""
    # Input: Content with <script>alert('xss')</script>
    # Expected: Content sanitized or rejected
    # Coverage: XSS prevention in content
```

##### Test 6.3: `test_path_traversal_in_filename`
```python
def test_path_traversal_in_filename():
    """Test path traversal prevention in filename sanitization"""
    # Input: Filename: "../../../etc/passwd"
    # Expected: Sanitized to "passwd" (path removed)
    # Coverage: Path traversal prevention
```

---

## 🔴 Priority 2: Planning Center Integration Tests (11% → 60% coverage)

### Current State
- **Planning Center Sync Service**: `app/services/planning_center_sync_service.py` (11% coverage)
- **Critical Gap**: External API integration, async operations, webhook processing

### Recommended Tests: ~15-20 new tests

#### 1. External API Integration Tests (6 tests)

**File**: `backend/tests/test_planning_center_integration.py`

##### Test 1.1: `test_sync_people_api_timeout`
```python
@patch('app.services.planning_center_sync_service.httpx.AsyncClient')
def test_sync_people_api_timeout(mock_client, db_session):
    """Test sync handles Planning Center API timeout"""
    # Input: Mock API timeout exception
    # Expected: Task marked as failed, error logged
    # Coverage: Timeout error handling
```

##### Test 1.2: `test_sync_people_api_rate_limit`
```python
@patch('app.services.planning_center_sync_service.httpx.AsyncClient')
def test_sync_people_api_rate_limit(mock_client, db_session):
    """Test sync handles Planning Center API rate limiting"""
    # Input: Mock 429 Too Many Requests response
    # Expected: Retry logic or graceful degradation
    # Coverage: Rate limit handling
```

##### Test 1.3: `test_sync_people_api_invalid_response`
```python
@patch('app.services.planning_center_sync_service.httpx.AsyncClient')
def test_sync_people_api_invalid_response(mock_client, db_session):
    """Test sync handles invalid JSON response from API"""
    # Input: Mock response with invalid JSON
    # Expected: Error handling, task marked as failed
    # Coverage: Invalid response handling
```

##### Test 1.4: `test_sync_people_api_pagination`
```python
@patch('app.services.planning_center_sync_service.httpx.AsyncClient')
def test_sync_people_api_pagination(mock_client, db_session):
    """Test sync handles paginated API responses"""
    # Input: Mock paginated responses (page 1, 2, 3)
    # Expected: All pages processed, all people synced
    # Coverage: Pagination logic
```

##### Test 1.5: `test_sync_people_api_authentication_failure`
```python
@patch('app.services.planning_center_sync_service.httpx.AsyncClient')
def test_sync_people_api_authentication_failure(mock_client, db_session):
    """Test sync handles authentication failure"""
    # Input: Mock 401 Unauthorized response
    # Expected: Task marked as failed, authentication error logged
    # Coverage: Authentication error handling
```

##### Test 1.6: `test_sync_people_api_server_error`
```python
@patch('app.services.planning_center_sync_service.httpx.AsyncClient')
def test_sync_people_api_server_error(mock_client, db_session):
    """Test sync handles Planning Center server errors"""
    # Input: Mock 500 Internal Server Error response
    # Expected: Retry logic or graceful error handling
    # Coverage: Server error handling
```

#### 2. Async Operations Tests (4 tests)

**File**: `backend/tests/test_planning_center_integration.py`

##### Test 2.1: `test_async_sync_people_execution`
```python
@patch('app.services.planning_center_sync_service.httpx.AsyncClient')
def test_async_sync_people_execution(mock_client, db_session):
    """Test async sync execution for people"""
    # Input: Start sync, wait for completion
    # Expected: People synced to database, task status updated
    # Coverage: Async task execution
```

##### Test 2.2: `test_async_sync_events_execution`
```python
@patch('app.services.planning_center_sync_service.httpx.AsyncClient')
def test_async_sync_events_execution(mock_client, db_session):
    """Test async sync execution for events"""
    # Input: Start sync, wait for completion
    # Expected: Events synced to database, task status updated
    # Coverage: Async event sync
```

##### Test 2.3: `test_concurrent_sync_operations`
```python
@patch('app.services.planning_center_sync_service.httpx.AsyncClient')
def test_concurrent_sync_operations(mock_client, db_session):
    """Test multiple concurrent sync operations"""
    # Input: Start multiple sync operations simultaneously
    # Expected: All operations complete successfully, no race conditions
    # Coverage: Concurrency handling
```

##### Test 2.4: `test_sync_task_cancellation`
```python
def test_sync_task_cancellation(db_session):
    """Test sync task can be cancelled"""
    # Input: Start sync, then cancel task
    # Expected: Task status updated to cancelled, operation stops
    # Coverage: Task cancellation logic
```

#### 3. Webhook Processing Tests (5 tests)

**File**: `backend/tests/test_planning_center_integration.py`

##### Test 3.1: `test_webhook_person_updated`
```python
def test_webhook_person_updated(db_session):
    """Test webhook processing for person.updated event"""
    # Input: Webhook data for person.updated event
    # Expected: Person record updated in database
    # Coverage: Person update webhook handling
```

##### Test 3.2: `test_webhook_person_deleted`
```python
def test_webhook_person_deleted(db_session):
    """Test webhook processing for person.deleted event"""
    # Input: Webhook data for person.deleted event
    # Expected: Person record marked as deleted or removed
    # Coverage: Person deletion webhook handling
```

##### Test 3.3: `test_webhook_event_updated`
```python
def test_webhook_event_updated(db_session):
    """Test webhook processing for event.updated event"""
    # Input: Webhook data for event.updated event
    # Expected: Event record updated in database
    # Coverage: Event update webhook handling
```

##### Test 3.4: `test_webhook_registration_cancelled`
```python
def test_webhook_registration_cancelled(db_session):
    """Test webhook processing for registration.cancelled event"""
    # Input: Webhook data for registration.cancelled event
    # Expected: Registration status updated to cancelled
    # Coverage: Registration cancellation webhook handling
```

##### Test 3.5: `test_webhook_malformed_data`
```python
def test_webhook_malformed_data(db_session):
    """Test webhook processing with malformed data"""
    # Input: Webhook with missing required fields
    # Expected: Error logged, webhook stored for review, graceful handling
    # Coverage: Malformed webhook handling
```

#### 4. Data Synchronization Tests (4 tests)

**File**: `backend/tests/test_planning_center_integration.py`

##### Test 4.1: `test_sync_people_creates_new_records`
```python
@patch('app.services.planning_center_sync_service.httpx.AsyncClient')
def test_sync_people_creates_new_records(mock_client, db_session):
    """Test sync creates new people records"""
    # Input: API returns new person not in database
    # Expected: New person record created
    # Coverage: New record creation logic
```

##### Test 4.2: `test_sync_people_updates_existing_records`
```python
@patch('app.services.planning_center_sync_service.httpx.AsyncClient')
def test_sync_people_updates_existing_records(mock_client, db_session):
    """Test sync updates existing people records"""
    # Input: API returns person already in database with changes
    # Expected: Existing person record updated
    # Coverage: Record update logic
```

##### Test 4.3: `test_sync_events_creates_courses`
```python
@patch('app.services.planning_center_sync_service.httpx.AsyncClient')
def test_sync_events_creates_courses(mock_client, db_session):
    """Test sync creates courses from events"""
    # Input: API returns event not mapped to course
    # Expected: New course created from event
    # Coverage: Course creation from events
```

##### Test 4.4: `test_sync_registrations_creates_enrollments`
```python
@patch('app.services.planning_center_sync_service.httpx.AsyncClient')
def test_sync_registrations_creates_enrollments(mock_client, db_session):
    """Test sync creates enrollments from registrations"""
    # Input: API returns registration not mapped to enrollment
    # Expected: New enrollment created from registration
    # Coverage: Enrollment creation from registrations
```

---

## 🔴 Priority 3: CSV Loader Tests (13% → 70% coverage)

### Current State
- **CSV Loader**: `app/core/csv_loader.py` (13% coverage)
- **Enhanced CSV Loader**: `app/core/enhanced_csv_loader.py` (0% coverage)
- **Critical Gap**: CSV parsing, data validation, error handling

### Recommended Tests: ~12-15 new tests

#### 1. CSV Parsing Tests (4 tests)

**File**: `backend/tests/test_csv_loader.py`

##### Test 1.1: `test_load_csv_valid_format`
```python
def test_load_csv_valid_format(tmp_path, db_session):
    """Test loading CSV with valid format"""
    # Input: Valid CSV file with headers and data
    # Expected: All records loaded successfully
    # Coverage: Basic CSV parsing logic
```

##### Test 1.2: `test_load_csv_different_delimiters`
```python
def test_load_csv_different_delimiters(tmp_path, db_session):
    """Test loading CSV with different delimiters (comma, semicolon, tab)"""
    # Input: CSV files with different delimiters
    # Expected: All formats parsed correctly
    # Coverage: Delimiter detection/configuration
```

##### Test 1.3: `test_load_csv_with_quoted_fields`
```python
def test_load_csv_with_quoted_fields(tmp_path, db_session):
    """Test loading CSV with quoted fields containing commas"""
    # Input: CSV with quoted fields like "Last Name, First Name"
    # Expected: Fields parsed correctly, quotes handled properly
    # Coverage: Quoted field parsing
```

##### Test 1.4: `test_load_csv_with_encoding_utf8`
```python
def test_load_csv_with_encoding_utf8(tmp_path, db_session):
    """Test loading CSV with UTF-8 encoding and special characters"""
    # Input: CSV with UTF-8 characters (é, ñ, etc.)
    # Expected: Characters parsed correctly
    # Coverage: Encoding handling
```

#### 2. Data Validation Tests (4 tests)

**File**: `backend/tests/test_csv_loader.py`

##### Test 2.1: `test_load_csv_missing_required_columns`
```python
def test_load_csv_missing_required_columns(tmp_path, db_session):
    """Test loading CSV with missing required columns"""
    # Input: CSV missing required column (e.g., "email")
    # Expected: Error raised with clear message
    # Coverage: Required column validation
```

##### Test 2.2: `test_load_csv_invalid_email_format`
```python
def test_load_csv_invalid_email_format(tmp_path, db_session):
    """Test loading CSV with invalid email formats"""
    # Input: CSV with invalid email addresses
    # Expected: Validation error or skipped records
    # Coverage: Email format validation
```

##### Test 2.3: `test_load_csv_invalid_date_format`
```python
def test_load_csv_invalid_date_format(tmp_path, db_session):
    """Test loading CSV with invalid date formats"""
    # Input: CSV with dates in wrong format
    # Expected: Date parsing error or format conversion
    # Coverage: Date format validation
```

##### Test 2.4: `test_load_csv_empty_rows`
```python
def test_load_csv_empty_rows(tmp_path, db_session):
    """Test loading CSV with empty rows"""
    # Input: CSV with empty rows mixed with data
    # Expected: Empty rows skipped or handled gracefully
    # Coverage: Empty row handling
```

#### 3. Error Handling Tests (3 tests)

**File**: `backend/tests/test_csv_loader.py`

##### Test 3.1: `test_load_csv_file_not_found`
```python
def test_load_csv_file_not_found(db_session):
    """Test loading non-existent CSV file"""
    # Input: Path to non-existent file
    # Expected: FileNotFoundError or clear error message
    # Coverage: File not found handling
```

##### Test 3.2: `test_load_csv_corrupted_file`
```python
def test_load_csv_corrupted_file(tmp_path, db_session):
    """Test loading corrupted CSV file"""
    # Input: CSV file with corrupted data/binary content
    # Expected: Error raised with clear message
    # Coverage: File corruption handling
```

##### Test 3.3: `test_load_csv_large_file`
```python
def test_load_csv_large_file(tmp_path, db_session):
    """Test loading very large CSV file"""
    # Input: CSV file with 10,000+ rows
    # Expected: File processed in chunks or with progress tracking
    # Coverage: Large file handling
```

#### 4. Enhanced CSV Loader Tests (4 tests)

**File**: `backend/tests/test_enhanced_csv_loader.py`

##### Test 4.1: `test_enhanced_load_csv_with_source_tracking`
```python
def test_enhanced_load_csv_with_source_tracking(tmp_path, db_session):
    """Test enhanced loader tracks data source"""
    # Input: CSV loaded with source tracking enabled
    # Expected: Source information stored with records
    # Coverage: Source tracking functionality
```

##### Test 4.2: `test_enhanced_load_csv_with_transformation`
```python
def test_enhanced_load_csv_with_transformation(tmp_path, db_session):
    """Test enhanced loader applies data transformations"""
    # Input: CSV with transformation rules
    # Expected: Data transformed according to rules
    # Coverage: Data transformation logic
```

##### Test 4.3: `test_enhanced_load_csv_incremental_update`
```python
def test_enhanced_load_csv_incremental_update(tmp_path, db_session):
    """Test enhanced loader performs incremental updates"""
    # Input: CSV loaded twice, second time with updates
    # Expected: Only changed records updated
    # Coverage: Incremental update logic
```

##### Test 4.4: `test_enhanced_load_csv_with_validation_rules`
```python
def test_enhanced_load_csv_with_validation_rules(tmp_path, db_session):
    """Test enhanced loader applies custom validation rules"""
    # Input: CSV with custom validation rules
    # Expected: Records validated against rules
    # Coverage: Custom validation rule application
```

---

## 🟡 Priority 4: Service Layer Coverage Tests (32-81% → 85% coverage)

### Current State
- **Progress Service**: 32% coverage
- **Report Service**: 26% coverage
- **Sync Service**: 21% coverage
- **Audit Service**: 72% coverage (needs edge cases)

### Recommended Tests: ~15-20 new tests

#### 1. Progress Service Tests (5 tests)

**File**: `backend/tests/test_progress_service.py`

##### Test 1.1: `test_get_member_progress_multiple_courses`
```python
def test_get_member_progress_multiple_courses(db_session, sample_member):
    """Test getting progress across multiple courses"""
    # Input: Member enrolled in 3 courses with different progress
    # Expected: Progress for all courses returned
    # Coverage: Multi-course progress retrieval
```

##### Test 1.2: `test_update_progress_with_completion`
```python
def test_update_progress_with_completion(db_session, sample_enrollment):
    """Test updating progress marks content as completed"""
    # Input: Progress update with 100% completion
    # Expected: Content marked as completed
    # Coverage: Completion tracking
```

##### Test 1.3: `test_get_progress_nonexistent_member`
```python
def test_get_progress_nonexistent_member(db_session):
    """Test getting progress for non-existent member"""
    # Input: Member ID that doesn't exist
    # Expected: Empty list returned
    # Coverage: Non-existent member handling
```

##### Test 1.4: `test_calculate_progress_percentage`
```python
def test_calculate_progress_percentage(db_session, sample_enrollment):
    """Test progress percentage calculation"""
    # Input: 5 content items, 3 completed
    # Expected: 60% progress calculated correctly
    # Coverage: Progress calculation logic
```

##### Test 1.5: `test_progress_with_partial_completion`
```python
def test_progress_with_partial_completion(db_session, sample_enrollment):
    """Test progress with partially completed content"""
    # Input: Content items with various progress percentages (50%, 75%, 100%)
    # Expected: Average progress calculated correctly
    # Coverage: Partial completion tracking
```

#### 2. Report Service Tests (5 tests)

**File**: `backend/tests/test_report_service.py`

##### Test 2.1: `test_generate_enrollment_report_date_range`
```python
def test_generate_enrollment_report_date_range(db_session):
    """Test generating enrollment report with date range filter"""
    # Input: Date range filter
    # Expected: Report contains only enrollments in date range
    # Coverage: Date filtering in reports
```

##### Test 2.2: `test_generate_progress_report_grouped_by_course`
```python
def test_generate_progress_report_grouped_by_course(db_session):
    """Test generating progress report grouped by course"""
    # Input: Multiple courses with various progress
    # Expected: Report grouped by course with aggregated stats
    # Coverage: Report grouping logic
```

##### Test 2.3: `test_generate_completion_report`
```python
def test_generate_completion_report(db_session):
    """Test generating course completion report"""
    # Input: Multiple courses with various completion rates
    # Expected: Completion statistics calculated correctly
    # Coverage: Completion report generation
```

##### Test 2.4: `test_report_with_no_data`
```python
def test_report_with_no_data(db_session):
    """Test generating report when no data exists"""
    # Input: Empty database
    # Expected: Report returns empty result or zero values
    # Coverage: Empty data handling in reports
```

##### Test 2.5: `test_report_export_csv_format`
```python
def test_report_export_csv_format(db_session):
    """Test exporting report in CSV format"""
    # Input: Report data, export to CSV
    # Expected: Valid CSV file generated
    # Coverage: CSV export functionality
```

#### 3. Sync Service Tests (5 tests)

**File**: `backend/tests/test_sync_service.py`

##### Test 3.1: `test_sync_with_conflict_resolution`
```python
def test_sync_with_conflict_resolution(db_session):
    """Test sync handles data conflicts"""
    # Input: Local and remote data conflict
    # Expected: Conflict resolved according to strategy
    # Coverage: Conflict resolution logic
```

##### Test 3.2: `test_sync_incremental_updates`
```python
def test_sync_incremental_updates(db_session):
    """Test sync performs incremental updates only"""
    # Input: Sync with only changed records
    # Expected: Only changed records updated
    # Coverage: Incremental sync logic
```

##### Test 3.3: `test_sync_with_rollback`
```python
def test_sync_with_rollback(db_session):
    """Test sync can rollback on error"""
    # Input: Sync fails mid-process
    # Expected: Changes rolled back, database consistent
    # Coverage: Transaction rollback on sync failure
```

##### Test 3.4: `test_sync_performance_large_dataset`
```python
def test_sync_performance_large_dataset(db_session):
    """Test sync performance with large dataset"""
    # Input: Sync 1000+ records
    # Expected: Sync completes within acceptable time
    # Coverage: Performance optimization
```

##### Test 3.5: `test_sync_status_tracking`
```python
def test_sync_status_tracking(db_session):
    """Test sync status is tracked throughout process"""
    # Input: Start sync operation
    # Expected: Status updates: pending → running → completed
    # Coverage: Status tracking during sync
```

---

## 🟢 Priority 5: Configuration Tests (0-81% → 70% coverage)

### Current State
- **Config AWS**: 0% coverage
- **Config Prod**: 0% coverage
- **Config Base**: 81% coverage

### Recommended Tests: ~8-10 new tests

#### 1. AWS Configuration Tests (4 tests)

**File**: `backend/tests/test_config_aws.py`

##### Test 1.1: `test_aws_s3_bucket_configuration`
```python
def test_aws_s3_bucket_configuration(monkeypatch):
    """Test AWS S3 bucket configuration"""
    # Input: Environment variables for S3 bucket
    # Expected: S3 bucket name correctly configured
    # Coverage: S3 configuration loading
```

##### Test 1.2: `test_aws_credentials_validation`
```python
def test_aws_credentials_validation(monkeypatch):
    """Test AWS credentials validation"""
    # Input: Valid/invalid AWS credentials
    # Expected: Credentials validated or error raised
    # Coverage: Credential validation
```

##### Test 1.3: `test_aws_region_configuration`
```python
def test_aws_region_configuration(monkeypatch):
    """Test AWS region configuration"""
    # Input: Environment variable for AWS region
    # Expected: Region correctly configured
    # Coverage: Region configuration
```

##### Test 1.4: `test_aws_configuration_fallback_defaults`
```python
def test_aws_configuration_fallback_defaults(monkeypatch):
    """Test AWS configuration falls back to defaults"""
    # Input: Missing AWS environment variables
    # Expected: Default values used or error raised appropriately
    # Coverage: Default value fallback
```

#### 2. Production Configuration Tests (4 tests)

**File**: `backend/tests/test_config_prod.py`

##### Test 2.1: `test_production_database_url_configuration`
```python
def test_production_database_url_configuration(monkeypatch):
    """Test production database URL configuration"""
    # Input: Production database URL environment variable
    # Expected: Database URL correctly configured
    # Coverage: Production database configuration
```

##### Test 2.2: `test_production_secret_key_validation`
```python
def test_production_secret_key_validation(monkeypatch):
    """Test production secret key validation"""
    # Input: Secret key validation rules
    # Expected: Secret key validated (length, complexity)
    # Coverage: Secret key validation in production
```

##### Test 2.3: `test_production_cors_origins_configuration`
```python
def test_production_cors_origins_configuration(monkeypatch):
    """Test production CORS origins configuration"""
    # Input: CORS origins environment variable
    # Expected: CORS origins correctly parsed and configured
    # Coverage: CORS configuration in production
```

##### Test 2.4: `test_production_logging_configuration`
```python
def test_production_logging_configuration(monkeypatch):
    """Test production logging configuration"""
    # Input: Logging level and format environment variables
    # Expected: Logging correctly configured
    # Coverage: Logging configuration in production
```

---

## 📋 Implementation Summary

### Test Count by Priority

| Priority | Category | Current Coverage | Target Coverage | Estimated Tests | Effort |
|----------|----------|-----------------|-----------------|-----------------|--------|
| 🔴 P1 | Security Tests | 40% | 70% | 20-25 | 8-10 hours |
| 🔴 P2 | Planning Center Integration | 11% | 60% | 15-20 | 12-15 hours |
| 🔴 P3 | CSV Loader Tests | 13% | 70% | 12-15 | 8-10 hours |
| 🟡 P4 | Service Layer Coverage | 32-81% | 85% | 15-20 | 10-12 hours |
| 🟢 P5 | Configuration Tests | 0-81% | 70% | 8-10 | 4-6 hours |
| **Total** | | **60%** | **80%** | **70-90** | **42-53 hours** |

### Implementation Order

1. **Week 1**: Security Tests (P1) - Critical for production readiness
2. **Week 2**: Planning Center Integration (P2) + CSV Loader Tests (P3)
3. **Week 3**: Service Layer Coverage (P4) + Configuration Tests (P5)

### Key Patterns to Follow

1. **Mocking Pattern**: Use endpoint-level mocking for API tests
   ```python
   with patch('app.api.v1.endpoints.module.ContentService') as MockService:
   ```

2. **Model Instances**: Use actual model instances instead of dicts
   ```python
   mock_access_log = ContentAccessLog(id=1, content_id=1, ...)
   ```

3. **Test Isolation**: Clear global state in setup_method/teardown_method
   ```python
   def setup_method(self):
       sync_tasks.clear()
   ```

4. **Async Testing**: Use proper async testing patterns with timeouts
   ```python
   import time
   time.sleep(0.1)  # Allow async operations to complete
   ```

### Coverage Goals

- **Overall Coverage**: 60% → **80%** (+20%)
- **Security Coverage**: 40% → **70%** (+30%)
- **Integration Coverage**: 11% → **60%** (+49%)
- **Service Coverage**: 32-81% → **85%** (average)
- **Configuration Coverage**: 0-81% → **70%** (average)

---

## 🎯 Success Metrics

### Immediate Success (After Week 1)
- ✅ Security test coverage: 40% → 70%
- ✅ All security edge cases covered
- ✅ Authorization tests comprehensive

### Short-term Success (After Week 2)
- ✅ Planning Center integration: 11% → 60%
- ✅ CSV loader coverage: 13% → 70%
- ✅ External API mocking comprehensive

### Long-term Success (After Week 3)
- ✅ Overall coverage: 60% → 80%
- ✅ Service layer coverage: 32-81% → 85%
- ✅ Configuration tests: 0-81% → 70%

---

## 📝 Notes

1. **Dependencies**: Some tests may depend on test fixtures that need to be created
2. **Mocking**: Extensive use of `unittest.mock.patch` for external dependencies
3. **Database**: Use test database with proper cleanup between tests
4. **Async Operations**: May require additional async testing patterns
5. **File System**: Use `tmp_path` fixture for temporary CSV files

---

*Document Version: 1.0*  
*Last Updated: January 2025*  
*Based on: Feedback Analysis and Test Coverage Review*

