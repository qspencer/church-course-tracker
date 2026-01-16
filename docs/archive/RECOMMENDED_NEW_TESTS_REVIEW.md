# Recommended New Tests - Review and Gap Analysis

## Executive Summary

This document reviews the `RECOMMENDED_NEW_TESTS.md` document against the existing test suite to identify:
- ✅ Tests that already exist
- ❌ Tests that are missing (gaps)
- ⚠️ Tests that need enhancement
- 📋 Prioritized implementation plan

**Current Status**: 60% coverage → Target: 80% coverage
**Estimated New Tests Needed**: 70-90 tests
**Estimated Implementation Time**: 42-53 hours

---

## Priority 1: Security Tests (40% → 70% coverage)

### Current State Analysis

**Existing Tests** (`backend/tests/test_security.py`):
- ✅ Password hashing (5 tests)
- ✅ Password strength validation (6 tests)
- ✅ JWT token creation and basic verification (5 tests)
- ✅ Secure token generation (3 tests)
- ✅ File validation (3 tests)
- ✅ Filename sanitization (5 tests)
- ✅ Authentication endpoints (6 tests)
- ✅ Authentication dependencies (4 tests)
- ✅ Security headers (2 tests)
- ✅ Rate limiting (2 tests)
- ✅ Input validation (3 tests - SQL injection, XSS, path traversal)

**Total Existing**: ~45 security tests

### Gap Analysis

#### 1. JWT Token Validation Edge Cases (6 tests) - ❌ **MISSING**

**Recommended Tests**:
1. `test_verify_token_malformed_header` - ❌ Missing
2. `test_verify_token_tampered_signature` - ❌ Missing
3. `test_verify_token_missing_algorithm` - ❌ Missing
4. `test_verify_token_wrong_algorithm` - ❌ Missing
5. `test_verify_token_empty_payload` - ❌ Missing
6. `test_verify_token_non_numeric_sub` - ❌ Missing

**Status**: None of these edge case tests exist. The current `test_verify_token_invalid` is too generic.

**Priority**: 🔴 **HIGH** - Critical for security

---

#### 2. Authorization Edge Cases (5 tests) - ⚠️ **PARTIALLY EXISTS**

**Recommended Tests**:
1. `test_get_current_admin_user_staff_role` - ⚠️ Partial (exists as `test_get_current_admin_user_non_admin` but needs enhancement)
2. `test_get_current_admin_user_viewer_role` - ❌ Missing
3. `test_get_current_active_user_with_invalid_role` - ❌ Missing
4. `test_role_based_content_access_staff` - ❌ Missing
5. `test_role_based_content_access_viewer` - ❌ Missing

**Status**: Basic admin check exists but granular role-based content access tests are missing.

**Priority**: 🔴 **HIGH** - Critical for authorization

---

#### 3. Account Lockout Edge Cases (4 tests) - ❌ **MISSING**

**Recommended Tests**:
1. `test_lockout_after_max_attempts` - ❌ Missing
2. `test_lockout_duration_expiration` - ❌ Missing
3. `test_lockout_attempts_reset_after_success` - ❌ Missing
4. `test_lockout_partial_attempts` - ❌ Missing

**Status**: Account lockout feature appears to be in `test_new_features.py` but these specific edge cases are missing.

**Note**: Check `UNIMPLEMENTED_FEATURES_AND_CHANGES.md` - account lockout may not be fully implemented.

**Priority**: 🔴 **HIGH** - Critical for security (if feature is implemented)

---

#### 4. Password Security Edge Cases (4 tests) - ⚠️ **PARTIALLY EXISTS**

**Recommended Tests**:
1. `test_password_hash_different_salts` - ❌ Missing
2. `test_verify_password_case_sensitivity` - ⚠️ Implicitly tested but not explicit
3. `test_verify_password_unicode_characters` - ❌ Missing
4. `test_password_strength_common_passwords` - ❌ Missing

**Status**: Basic password hashing/verification exists, but edge cases are missing.

**Priority**: 🟡 **MEDIUM** - Important but not critical

---

#### 5. Session Management (3 tests) - ⚠️ **PARTIALLY EXISTS**

**Recommended Tests**:
1. `test_token_refresh_before_expiry` - ✅ Exists (`test_refresh_token`)
2. `test_token_refresh_after_expiry` - ⚠️ Partial (exists as `test_refresh_token_invalid` but not specific to expiry)
3. `test_concurrent_token_refresh` - ❌ Missing

**Status**: Basic token refresh exists, but expiry-specific and concurrency tests are missing.

**Priority**: 🟡 **MEDIUM**

---

#### 6. Input Validation Edge Cases (3 tests) - ✅ **EXISTS**

**Recommended Tests**:
1. `test_sql_injection_in_username` - ✅ Exists (`test_sql_injection_prevention`)
2. `test_xss_in_content_fields` - ✅ Exists (`test_xss_prevention`)
3. `test_path_traversal_in_filename` - ✅ Exists (`test_path_traversal_prevention`)

**Status**: All recommended tests exist.

**Priority**: ✅ **COMPLETE**

---

### Security Tests Summary

| Category | Recommended | Existing | Missing | Status |
|----------|------------|----------|---------|--------|
| JWT Edge Cases | 6 | 0 | 6 | ❌ Critical Gap |
| Authorization Edge Cases | 5 | 1 | 4 | ⚠️ Needs Enhancement |
| Account Lockout | 4 | 0 | 4 | ❌ Critical Gap* |
| Password Edge Cases | 4 | 0 | 4 | 🟡 Medium Priority |
| Session Management | 3 | 2 | 1 | ⚠️ Mostly Complete |
| Input Validation | 3 | 3 | 0 | ✅ Complete |
| **Total** | **25** | **6** | **19** | **76% Missing** |

*Note: Account lockout tests depend on feature implementation status.

**Action Required**: Add 19 new security tests, prioritize JWT edge cases and authorization.

---

## Priority 2: Planning Center Integration Tests (11% → 60% coverage)

### Current State Analysis

**Existing Tests** (`backend/tests/test_planning_center_integration.py`):
- ✅ Authentication and configuration (3 tests)
- ✅ Task management (10 tests)
- ✅ Sync operations - people (4 tests)
- ✅ Sync operations - events (2 tests)
- ✅ Sync operations - registrations (2 tests)
- ✅ Webhook processing (5 tests)
- ✅ Sync logging and caching (4 tests)
- ✅ Error handling (3 tests)

**Total Existing**: ~33 Planning Center tests

### Gap Analysis

#### 1. External API Integration Tests (6 tests) - ⚠️ **PARTIALLY EXISTS**

**Recommended Tests**:
1. `test_sync_people_api_timeout` - ⚠️ Partial (exists as `test_sync_with_network_timeout` but not specific to people)
2. `test_sync_people_api_rate_limit` - ❌ Missing
3. `test_sync_people_api_invalid_response` - ⚠️ Partial (exists as `test_sync_with_invalid_json_response`)
4. `test_sync_people_api_pagination` - ❌ Missing
5. `test_sync_people_api_authentication_failure` - ❌ Missing
6. `test_sync_people_api_server_error` - ❌ Missing

**Status**: Basic error handling exists, but specific API error scenarios are missing.

**Priority**: 🔴 **HIGH** - Critical for integration reliability

---

#### 2. Async Operations Tests (4 tests) - ⚠️ **PARTIALLY EXISTS**

**Recommended Tests**:
1. `test_async_sync_people_execution` - ✅ Exists (`test_start_sync_people_success`)
2. `test_async_sync_events_execution` - ✅ Exists (`test_start_sync_events_success`)
3. `test_concurrent_sync_operations` - ❌ Missing
4. `test_sync_task_cancellation` - ❌ Missing

**Status**: Basic async execution exists, but concurrency and cancellation tests are missing.

**Priority**: 🟡 **MEDIUM**

---

#### 3. Webhook Processing Tests (5 tests) - ✅ **EXISTS**

**Recommended Tests**:
1. `test_webhook_person_updated` - ✅ Exists (`test_process_webhook_event_person_created` - similar)
2. `test_webhook_person_deleted` - ❌ Missing
3. `test_webhook_event_updated` - ✅ Exists (`test_process_webhook_event_event_created` - similar)
4. `test_webhook_registration_cancelled` - ✅ Exists (`test_process_webhook_event_registration_created` - similar)
5. `test_webhook_malformed_data` - ✅ Exists (`test_webhook_processing_with_malformed_data`)

**Status**: Most webhook tests exist, but person deletion webhook is missing.

**Priority**: 🟡 **MEDIUM**

---

#### 4. Data Synchronization Tests (4 tests) - ⚠️ **PARTIALLY EXISTS**

**Recommended Tests**:
1. `test_sync_people_creates_new_records` - ✅ Exists (`test_sync_people_background_with_existing_person` - similar)
2. `test_sync_people_updates_existing_records` - ⚠️ Partial (tested implicitly)
3. `test_sync_events_creates_courses` - ❌ Missing
4. `test_sync_registrations_creates_enrollments` - ❌ Missing

**Status**: Basic sync exists, but course/enrollment creation from sync is missing.

**Priority**: 🔴 **HIGH** - Critical for data integrity

---

### Planning Center Tests Summary

| Category | Recommended | Existing | Missing | Status |
|----------|------------|----------|---------|--------|
| External API Integration | 6 | 2 | 4 | ⚠️ Needs Enhancement |
| Async Operations | 4 | 2 | 2 | ⚠️ Mostly Complete |
| Webhook Processing | 5 | 4 | 1 | ⚠️ Mostly Complete |
| Data Synchronization | 4 | 1 | 3 | ⚠️ Needs Enhancement |
| **Total** | **19** | **9** | **10** | **53% Missing** |

**Action Required**: Add 10 new Planning Center tests, prioritize API error handling and data synchronization.

---

## Priority 3: CSV Loader Tests (13% → 70% coverage)

### Current State Analysis

**Existing Tests**: ❌ **NONE FOUND**

**Files Searched**:
- `backend/tests/test_csv_loader.py` - ❌ Does not exist
- `backend/tests/test_enhanced_csv_loader.py` - ❌ Does not exist

**Status**: No CSV loader tests exist.

### Gap Analysis

#### All CSV Loader Tests (15 tests) - ❌ **MISSING**

**Recommended Tests**:
1. CSV Parsing Tests (4 tests) - ❌ All Missing
2. Data Validation Tests (4 tests) - ❌ All Missing
3. Error Handling Tests (3 tests) - ❌ All Missing
4. Enhanced CSV Loader Tests (4 tests) - ❌ All Missing

**Priority**: 🔴 **HIGH** - Critical gap, 0% coverage

**Action Required**: Create new test file `backend/tests/test_csv_loader.py` with all 15 tests.

---

## Priority 4: Service Layer Coverage Tests (32-81% → 85% coverage)

### Current State Analysis

**Existing Tests** (`backend/tests/test_services.py`):
- ✅ PeopleService tests
- ✅ CourseService tests
- ✅ CourseEnrollmentService tests (includes some progress tracking)

**Gap Analysis**:

#### 1. Progress Service Tests (5 tests) - ⚠️ **PARTIALLY EXISTS**

**Recommended Tests**:
1. `test_get_member_progress_multiple_courses` - ⚠️ Partial (progress exists in enrollment service)
2. `test_update_progress_with_completion` - ✅ Exists (`test_update_progress`)
3. `test_get_progress_nonexistent_member` - ❌ Missing
4. `test_calculate_progress_percentage` - ⚠️ Partial (implicitly tested)
5. `test_progress_with_partial_completion` - ❌ Missing

**Status**: Basic progress tracking exists in enrollment service, but dedicated progress service tests are missing.

**Priority**: 🟡 **MEDIUM**

---

#### 2. Report Service Tests (5 tests) - ❌ **MISSING**

**Recommended Tests**:
1. `test_generate_enrollment_report_date_range` - ❌ Missing
2. `test_generate_progress_report_grouped_by_course` - ❌ Missing
3. `test_generate_completion_report` - ❌ Missing
4. `test_report_with_no_data` - ❌ Missing
5. `test_report_export_csv_format` - ❌ Missing

**Status**: No report service tests found.

**Priority**: 🔴 **HIGH** - Critical gap

---

#### 3. Sync Service Tests (5 tests) - ⚠️ **PARTIALLY EXISTS**

**Recommended Tests**:
1. `test_sync_with_conflict_resolution` - ❌ Missing
2. `test_sync_incremental_updates` - ❌ Missing
3. `test_sync_with_rollback` - ❌ Missing
4. `test_sync_performance_large_dataset` - ❌ Missing
5. `test_sync_status_tracking` - ✅ Exists (in Planning Center tests)

**Status**: Basic sync exists in Planning Center tests, but advanced sync features are missing.

**Priority**: 🟡 **MEDIUM**

---

### Service Layer Tests Summary

| Category | Recommended | Existing | Missing | Status |
|----------|------------|----------|---------|--------|
| Progress Service | 5 | 2 | 3 | ⚠️ Needs Enhancement |
| Report Service | 5 | 0 | 5 | ❌ Critical Gap |
| Sync Service | 5 | 1 | 4 | ⚠️ Needs Enhancement |
| **Total** | **15** | **3** | **12** | **80% Missing** |

**Action Required**: Add 12 new service layer tests, prioritize report service.

---

## Priority 5: Configuration Tests (0-81% → 70% coverage)

### Current State Analysis

**Existing Tests**: ❌ **NONE FOUND**

**Files Searched**:
- `backend/tests/test_config_aws.py` - ❌ Does not exist
- `backend/tests/test_config_prod.py` - ❌ Does not exist
- `backend/tests/test_config.py` - ❌ Does not exist

**Status**: No configuration tests exist.

### Gap Analysis

#### All Configuration Tests (8 tests) - ❌ **MISSING**

**Recommended Tests**:
1. AWS Configuration Tests (4 tests) - ❌ All Missing
2. Production Configuration Tests (4 tests) - ❌ All Missing

**Priority**: 🟢 **LOW** - Important but not critical for functionality

**Action Required**: Create new test files for configuration testing.

---

## Overall Gap Analysis Summary

| Priority | Category | Recommended | Existing | Missing | Completion % |
|----------|----------|------------|----------|---------|--------------|
| 🔴 P1 | Security Tests | 25 | 6 | 19 | 24% |
| 🔴 P2 | Planning Center Integration | 19 | 9 | 10 | 47% |
| 🔴 P3 | CSV Loader Tests | 15 | 0 | 15 | 0% |
| 🟡 P4 | Service Layer Coverage | 15 | 3 | 12 | 20% |
| 🟢 P5 | Configuration Tests | 8 | 0 | 8 | 0% |
| **Total** | | **82** | **18** | **64** | **22%** |

**Overall Status**: Only 22% of recommended tests exist. **64 tests need to be implemented.**

---

## Prioritized Implementation Plan

### Phase 1: Critical Security Gaps (Week 1) - 19 tests

**Priority**: 🔴 **CRITICAL**

1. **JWT Token Validation Edge Cases** (6 tests)
   - File: `backend/tests/test_security.py`
   - Add tests for malformed headers, tampered signatures, missing/wrong algorithms, empty payload, non-numeric sub
   - **Estimated Time**: 3-4 hours

2. **Authorization Edge Cases** (4 tests)
   - File: `backend/tests/test_security.py` or new `backend/tests/test_authorization.py`
   - Add tests for viewer role restrictions, invalid roles, granular content access
   - **Estimated Time**: 2-3 hours

3. **Account Lockout Edge Cases** (4 tests)
   - File: `backend/tests/test_security.py` or `backend/tests/test_account_lockout.py`
   - **Note**: Verify feature is implemented first (check `UNIMPLEMENTED_FEATURES_AND_CHANGES.md`)
   - **Estimated Time**: 2-3 hours

4. **Password Security Edge Cases** (4 tests)
   - File: `backend/tests/test_security.py`
   - Add tests for salt uniqueness, case sensitivity, unicode, common passwords
   - **Estimated Time**: 1-2 hours

5. **Session Management** (1 test)
   - File: `backend/tests/test_security.py`
   - Add concurrent token refresh test
   - **Estimated Time**: 1 hour

**Total Phase 1**: 19 tests, 9-13 hours

---

### Phase 2: Integration and Data Gaps (Week 2) - 25 tests

**Priority**: 🔴 **HIGH**

1. **Planning Center API Integration** (4 tests)
   - File: `backend/tests/test_planning_center_integration.py`
   - Add tests for rate limiting, authentication failure, server errors, pagination
   - **Estimated Time**: 3-4 hours

2. **Planning Center Data Synchronization** (3 tests)
   - File: `backend/tests/test_planning_center_integration.py`
   - Add tests for course/enrollment creation from sync
   - **Estimated Time**: 2-3 hours

3. **Planning Center Async Operations** (2 tests)
   - File: `backend/tests/test_planning_center_integration.py`
   - Add tests for concurrent sync and task cancellation
   - **Estimated Time**: 2 hours

4. **CSV Loader Tests** (15 tests)
   - File: `backend/tests/test_csv_loader.py` (NEW)
   - Create comprehensive CSV loader test suite
   - **Estimated Time**: 8-10 hours

**Total Phase 2**: 24 tests, 15-19 hours

---

### Phase 3: Service Layer and Configuration (Week 3) - 20 tests

**Priority**: 🟡 **MEDIUM** / 🟢 **LOW**

1. **Report Service Tests** (5 tests)
   - File: `backend/tests/test_report_service.py` (NEW)
   - Create comprehensive report service test suite
   - **Estimated Time**: 4-5 hours

2. **Progress Service Tests** (3 tests)
   - File: `backend/tests/test_progress_service.py` (NEW)
   - Add missing progress service tests
   - **Estimated Time**: 2-3 hours

3. **Sync Service Tests** (4 tests)
   - File: `backend/tests/test_sync_service.py` (NEW)
   - Add advanced sync feature tests
   - **Estimated Time**: 3-4 hours

4. **Configuration Tests** (8 tests)
   - Files: `backend/tests/test_config_aws.py`, `backend/tests/test_config_prod.py` (NEW)
   - Create configuration test suites
   - **Estimated Time**: 4-6 hours

**Total Phase 3**: 20 tests, 13-18 hours

---

## Dependencies and Prerequisites

### Before Starting Implementation

1. **Verify Feature Implementation Status**
   - Check `UNIMPLEMENTED_FEATURES_AND_CHANGES.md` for:
     - Account lockout feature
     - CSV loader functionality
     - Report service
     - Progress service

2. **Review Existing Test Patterns**
   - Study `backend/tests/test_security.py` for security test patterns
   - Study `backend/tests/test_planning_center_integration.py` for integration test patterns
   - Study `backend/tests/test_services.py` for service test patterns

3. **Set Up Test Fixtures**
   - Ensure `conftest.py` has necessary fixtures
   - Add fixtures for:
     - CSV test files (`tmp_path`)
     - Mock Planning Center API responses
     - Test users with different roles

4. **Mocking Strategy**
   - Use `unittest.mock.patch` for external dependencies
   - Mock at endpoint level for API tests: `patch('app.api.v1.endpoints.module.ContentService')`
   - Use `AsyncMock` for async operations

---

## Success Metrics

### Immediate Success (After Phase 1)
- ✅ Security test coverage: 40% → 70%
- ✅ All security edge cases covered
- ✅ Authorization tests comprehensive

### Short-term Success (After Phase 2)
- ✅ Planning Center integration: 11% → 60%
- ✅ CSV loader coverage: 0% → 70%
- ✅ External API mocking comprehensive

### Long-term Success (After Phase 3)
- ✅ Overall coverage: 60% → 80%
- ✅ Service layer coverage: 32-81% → 85%
- ✅ Configuration tests: 0% → 70%

---

## Notes and Recommendations

1. **Test File Organization**
   - Keep related tests together
   - Use descriptive test class names
   - Follow existing naming conventions

2. **Test Data Management**
   - Use fixtures for reusable test data
   - Clean up test data after each test
   - Use `tmp_path` for file-based tests

3. **Mocking Best Practices**
   - Mock external dependencies (APIs, file system)
   - Use actual model instances instead of dicts
   - Clear global state in setup/teardown

4. **Async Testing**
   - Use proper async testing patterns
   - Add timeouts for async operations
   - Test concurrent operations

5. **Coverage Goals**
   - Aim for 80% overall coverage
   - Prioritize critical paths
   - Don't sacrifice quality for quantity

---

## Conclusion

**Current Status**: 18/82 recommended tests exist (22% completion)

**Action Required**: Implement 64 new tests across 5 priority areas

**Estimated Total Time**: 37-50 hours (aligned with original 42-53 hour estimate)

**Recommended Approach**: 
1. Start with Phase 1 (Security) - most critical
2. Proceed to Phase 2 (Integration/Data) - high impact
3. Complete with Phase 3 (Service/Config) - polish and completeness

**Next Steps**:
1. Review this document with the team
2. Verify feature implementation status
3. Begin Phase 1 implementation
4. Track progress against this plan

---

*Document Version: 1.0*  
*Last Updated: January 2025*  
*Based on: RECOMMENDED_NEW_TESTS.md and existing test suite analysis*

