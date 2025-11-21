# Safe Implementation Plan - Changes Before Stakeholder Answers

## Overview

This document outlines changes that can be safely implemented **before** getting answers to the stakeholder questions in `DATA_MODEL_FEEDBACK_RECOMMENDATIONS.md`.

---

## ✅ **Safe to Implement Now**

### 1. Bulk Enrollment from Planning Center Event

**Status**: ✅ Safe to implement  
**Priority**: High  
**Complexity**: Medium  
**Data Model Changes**: None

#### What This Adds

Enhances the existing bulk enrollment functionality to support enrolling multiple people from a Planning Center Registration event in a single operation.

#### Implementation Steps

1. **Add Service Method** (`backend/app/services/enrollment_service.py`)
   - Method: `bulk_enroll_from_pc_event()`
   - Fetches registrations from Planning Center API
   - Creates/updates enrollments based on registrations
   - Supports status filtering (registered, waitlisted, etc.)

2. **Add API Endpoint** (`backend/app/api/v1/endpoints/enrollments.py`)
   - Endpoint: `POST /api/v1/enrollments/bulk-from-pc-event`
   - Accepts course_id, pc_event_id, and optional status_filter
   - Returns list of created/updated enrollments

3. **Add Schema** (`backend/app/schemas/enrollment.py`)
   - Schema: `BulkEnrollFromPCEventRequest`
   - Fields: course_id, pc_event_id, status_filter, update_existing

4. **Frontend Enhancement** (Optional, can be done later)
   - Add "Bulk Enroll from Planning Center" button in enrollment UI
   - Show available Planning Center events
   - Allow filtering by registration status

#### Why This Is Safe

- ✅ No database schema changes required
- ✅ Uses existing `CourseEnrollment` model
- ✅ Uses existing `PlanningCenterSyncService` infrastructure
- ✅ Builds on existing `bulk_enroll()` method pattern
- ✅ No impact on existing functionality
- ✅ Can be tested independently

#### Dependencies

- Existing `PlanningCenterSyncService` ✅ (already exists)
- Existing `CourseEnrollmentService.bulk_enroll()` ✅ (already exists)
- Existing `get_enrollment_by_pc_registration_id()` ✅ (already exists)
- Planning Center API access ✅ (already configured)

---

## ⏸️ **Wait for Stakeholder Input**

### 2. Campus Relationship (1:M)

**Status**: ⏸️ Wait  
**Reason**: Requires stakeholder decision on storage approach (local vs. fetch from PC)

**Blocked By**:
- Question: "Do you want to keep campus data locally (Option A) or fetch from Planning Center (Option B)?"

**Impact if Implemented Early**:
- Might implement wrong approach
- Would require rework/migration if decision changes
- Database migration needed (risky without decision)

---

### 3. Course Instances & Teacher Tracking

**Status**: ⏸️ Wait  
**Reason**: Major architectural change with multiple unanswered questions

**Blocked By**:
- Question: "What should we call 'Course Instance'?" (e.g., "Course Offering", "Session", "Cohort")
- Question: "Should we use separate `CourseInstanceTeacher` model or extend `CourseRole`?"
- Question: "Do you need 1:1 assignments, small groups, or both?"
- Question: "Migration strategy - auto-create default instances or require manual creation?"

**Impact if Implemented Early**:
- Would require significant database migrations
- Might choose wrong naming convention
- Could build wrong architecture for teacher tracking
- Major rework if stakeholder preferences differ

---

## 📋 **Implementation Checklist for Safe Change**

### Phase 1: Backend Service Method

- [ ] Add `bulk_enroll_from_pc_event()` to `CourseEnrollmentService`
- [ ] Add helper method `_get_people_id_from_pc_person_id()`
- [ ] Add helper method `_map_pc_status_to_enrollment_status()`
- [ ] Add error handling for missing people/courses
- [ ] Add transaction management
- [ ] Add audit logging

### Phase 2: API Endpoint

- [ ] Add `BulkEnrollFromPCEventRequest` schema
- [ ] Add `POST /api/v1/enrollments/bulk-from-pc-event` endpoint
- [ ] Add authentication/authorization (admin/staff only)
- [ ] Add request validation
- [ ] Add error handling
- [ ] Update API documentation

### Phase 3: Planning Center Integration

- [ ] Add method to get registrations for specific event
- [ ] Add pagination support if needed
- [ ] Add caching/performance optimization
- [ ] Handle Planning Center API errors gracefully

### Phase 4: Testing

- [ ] Unit tests for service method
- [ ] Integration tests for API endpoint
- [ ] Test with mock Planning Center data
- [ ] Test error scenarios (missing people, invalid event, etc.)
- [ ] Test status filtering
- [ ] Test update_existing flag

### Phase 5: Documentation

- [ ] Update API documentation
- [ ] Add usage examples
- [ ] Document status filter options

### Phase 6: Frontend (Optional - Can Do Later)

- [ ] Add "Bulk Enroll from PC" button to enrollment UI
- [ ] Create dialog for selecting PC event
- [ ] Show registration status filter options
- [ ] Display results/confirmation
- [ ] Handle errors in UI

---

## 🎯 **Recommended Action**

**Implement Now**: Bulk Enrollment from PC Event (Phase 1-5)

**Wait**: Campus 1:M relationship and Course Instances until stakeholder questions are answered

---

## 📝 **Implementation Notes**

### Helper Methods Needed

1. **`_get_people_id_from_pc_person_id(pc_person_id: str) -> int`**
   - Look up local `People.id` from Planning Center person ID
   - Raise error if person doesn't exist locally

2. **`_map_pc_status_to_enrollment_status(pc_status: str) -> str`**
   - Map PC registration status to enrollment status
   - Mapping:
     - `registered` → `enrolled`
     - `waitlisted` → `enrolled` (or new status)
     - `cancelled` → `dropped`

### Error Scenarios to Handle

1. Planning Center event not found
2. People not found locally (need to sync first)
3. Course not found
4. Duplicate enrollment (handle based on `update_existing` flag)
5. Planning Center API errors (rate limits, timeouts, etc.)

### Performance Considerations

- If event has many registrations, consider batch processing
- Add pagination support for large registration lists
- Consider async processing for very large enrollments
- Add progress tracking for UI feedback

---

*Document Created: January 2025*  
*Status: Ready for Implementation*

