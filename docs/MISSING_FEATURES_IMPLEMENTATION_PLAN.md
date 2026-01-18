# Missing Features Implementation Plan

**Date**: January 17, 2026
**Purpose**: Implementation plan for features tested in E2E but not yet implemented
**Impact**: ~150 tests currently skipped due to missing features

---

## Overview

The E2E test suite includes tests for features that are either:
1. **Partially implemented** (backend exists, frontend missing)
2. **Not implemented** (neither backend nor frontend exists)
3. **Future enhancements** (planned but not prioritized)

This document provides a prioritized implementation plan for each missing feature.

---

## Feature Priority Matrix

| Feature | Backend Status | Frontend Status | Tests Affected | Priority | Effort |
|---------|---------------|-----------------|----------------|----------|--------|
| Course Content Management | ✅ Complete | ❌ Missing | 25+ | **HIGH** | Medium |
| Audit Log Export | ✅ Complete | ⚠️ Partial | 6 | HIGH | Low |
| Progress Tracking Dashboard | ⚠️ Partial | ❌ Missing | 15+ | HIGH | High |
| Course Prerequisites | ❌ Missing | ❌ Missing | 8 | MEDIUM | Medium |
| Learning Goals | ❌ Missing | ❌ Missing | 5+ | LOW | Low |
| System Settings UI | ✅ Complete | ⚠️ Partial | 10+ | MEDIUM | Low |

---

## 1. Course Content Management (HIGH PRIORITY)

### Current State
- **Backend**: ✅ Fully implemented (`/api/v1/courses/{id}/content`)
- **Frontend**: ❌ "Manage Content" button doesn't exist

### Tests Affected: 25+
- File upload/download
- Content CRUD operations
- Module management
- Content summary and reports
- Role-based content access

### Implementation Plan

#### Phase 1: Add "Manage Content" Button
**Location**: `frontend/church-course-tracker/src/app/components/courses/courses.component.html`

```typescript
// In the courses table, add button:
<button
  mat-icon-button
  color="primary"
  (click)="manageContent(course)"
  matTooltip="Manage Content">
  <mat-icon>folder</mat-icon>
</button>
```

#### Phase 2: Create Content Management Dialog
**New Component**: `course-content-dialog.component.ts`

Features needed:
- List all content items for the course
- Add new content (text, video, file, quiz)
- Edit/delete content
- Organize into modules
- Set content visibility/unlock mode

**Screens**:
1. **Content List** - Table of all content items
2. **Add Content** - Form to create new content
3. **Edit Content** - Form to update existing content
4. **Module Organization** - Drag-drop to organize content

#### Phase 3: Content Viewing for Students
**New Component**: `course-viewer.component.ts`

Features:
- Display content based on unlock mode
- Track progress (mark as complete)
- Navigate between content items
- Show module structure

### Backend Endpoints (Already Exist)
```
GET    /api/v1/courses/{id}/content          - List content
POST   /api/v1/courses/{id}/content          - Create content
GET    /api/v1/content/{id}                  - Get content
PUT    /api/v1/content/{id}                  - Update content
DELETE /api/v1/content/{id}                  - Delete content
POST   /api/v1/content/{id}/upload           - Upload file
GET    /api/v1/content/{id}/download         - Download file
```

### Effort Estimate
- Phase 1 (Button): 30 minutes
- Phase 2 (Management Dialog): 4-6 hours
- Phase 3 (Viewer): 3-4 hours
- **Total**: 8-11 hours

### Test Impact
✅ Will fix 25+ tests once implemented

---

## 2. Audit Log Export (HIGH PRIORITY)

### Current State
- **Backend**: ✅ Audit log API exists
- **Frontend**: ⚠️ Can view logs, but no export button

### Tests Affected: 6
- Export audit logs to CSV
- Export filtered logs
- Download audit report

### Implementation Plan

#### Add Export Button
**Location**: `frontend/church-course-tracker/src/app/components/audit/audit.component.html`

```typescript
<button
  mat-raised-button
  color="primary"
  (click)="exportAuditLogs()"
  [disabled]="loading">
  <mat-icon>file_download</mat-icon>
  Export to CSV
</button>
```

#### Implement Export Function
```typescript
exportAuditLogs(): void {
  this.auditService.getAuditLogs(this.filters).subscribe(logs => {
    const csv = this.convertToCSV(logs);
    this.downloadCSV(csv, 'audit-logs.csv');
  });
}

convertToCSV(logs: AuditLog[]): string {
  const header = ['Timestamp', 'User', 'Action', 'Resource', 'Details'];
  const rows = logs.map(log => [
    log.timestamp,
    log.user_email,
    log.action,
    log.resource_type,
    log.details
  ]);

  return [header, ...rows]
    .map(row => row.map(cell => `"${cell}"`).join(','))
    .join('\n');
}

downloadCSV(content: string, filename: string): void {
  const blob = new Blob([content], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
}
```

### Effort Estimate
- 1-2 hours

### Test Impact
✅ Will fix 6 tests once implemented

---

## 3. Progress Tracking Dashboard (HIGH PRIORITY)

### Current State
- **Backend**: ⚠️ Basic progress API exists
- **Frontend**: ❌ No progress dashboard UI

### Tests Affected: 15+
- View all user progress
- Generate progress reports
- Export progress data
- Filter by course/user
- Track completion rates

### Implementation Plan

#### Phase 1: Progress Dashboard Component
**New Component**: `progress-dashboard.component.ts`

**Route**: `/progress`

**Features**:
- Table of all users with progress stats
- Filter by course
- Search by user name
- Sort by completion %

**Data Structure**:
```typescript
interface UserProgress {
  userId: number;
  userName: string;
  coursesEnrolled: number;
  coursesCompleted: number;
  completionRate: number;
  lastActivity: Date;
}
```

#### Phase 2: Course Progress Details
**New Component**: `course-progress-detail.component.ts`

**Features**:
- Detailed progress for a specific course
- List all students enrolled
- Individual student progress
- Content completion breakdown

#### Phase 3: Reports and Export
- Generate PDF reports
- Export to CSV/Excel
- Email reports to instructors

### Backend Endpoints Needed
```
GET /api/v1/progress/users              - All users progress
GET /api/v1/progress/courses/{id}       - Course progress detail
GET /api/v1/progress/export             - Export progress data
POST /api/v1/progress/report            - Generate report
```

### Effort Estimate
- Phase 1 (Dashboard): 4-6 hours
- Phase 2 (Details): 3-4 hours
- Phase 3 (Reports): 4-6 hours
- **Total**: 11-16 hours

### Test Impact
✅ Will fix 15+ tests once implemented

---

## 4. Course Prerequisites (MEDIUM PRIORITY)

### Current State
- **Backend**: ❌ Not implemented
- **Frontend**: ❌ Not implemented

### Tests Affected: 8
- Set course prerequisites
- Validate prerequisite completion
- Block enrollment without prerequisites

### Implementation Plan

#### Phase 1: Backend Implementation

**Database** (Already exists):
```sql
courses.prerequisites JSON  -- List of prerequisite course IDs
```

**API Endpoints**:
```
GET  /api/v1/courses/{id}/prerequisites      - Get prerequisites
POST /api/v1/courses/{id}/prerequisites      - Set prerequisites
GET  /api/v1/courses/{id}/check-prerequisites/{userId} - Check if user meets prereqs
```

**Business Logic**:
```python
def check_prerequisites(course_id: int, user_id: int) -> bool:
    course = get_course(course_id)
    if not course.prerequisites:
        return True

    for prereq_id in course.prerequisites:
        enrollment = get_enrollment(user_id, prereq_id)
        if not enrollment or enrollment.status != 'completed':
            return False

    return True
```

#### Phase 2: Frontend Implementation

**Course Form** - Add prerequisites selector:
```html
<mat-form-field>
  <mat-label>Prerequisites</mat-label>
  <mat-select multiple [(ngModel)]="course.prerequisites">
    <mat-option *ngFor="let c of availableCourses" [value]="c.id">
      {{ c.title }}
    </mat-option>
  </mat-select>
</mat-form-field>
```

**Enrollment** - Check prerequisites before allowing enrollment:
```typescript
enrollInCourse(courseId: number): void {
  this.courseService.checkPrerequisites(courseId, this.currentUserId).subscribe(
    canEnroll => {
      if (canEnroll) {
        this.proceedWithEnrollment(courseId);
      } else {
        this.showPrerequisiteError(courseId);
      }
    }
  );
}
```

### Effort Estimate
- Phase 1 (Backend): 3-4 hours
- Phase 2 (Frontend): 2-3 hours
- **Total**: 5-7 hours

### Test Impact
✅ Will fix 8 tests once implemented

---

## 5. System Settings UI (MEDIUM PRIORITY)

### Current State
- **Backend**: ✅ System settings API exists
- **Frontend**: ⚠️ No dedicated settings page

### Tests Affected: 10+
- Configure application settings
- Update organization info
- Manage feature flags
- Configure integrations

### Implementation Plan

#### Create Settings Component
**New Component**: `settings.component.ts`

**Route**: `/settings` (admin only)

**Sections**:
1. **General Settings**
   - Organization name
   - Time zone
   - Date format
   - Logo upload

2. **Integration Settings**
   - Planning Center credentials
   - Email configuration
   - AWS S3 settings

3. **Feature Flags**
   - Enable/disable features
   - Beta feature access

4. **Security Settings**
   - Session timeout
   - Password policy
   - Failed login lockout

### Backend Endpoints (Already Exist)
```
GET  /api/v1/settings              - Get all settings
PUT  /api/v1/settings              - Update settings
GET  /api/v1/settings/{key}        - Get specific setting
PUT  /api/v1/settings/{key}        - Update specific setting
```

### Effort Estimate
- 3-5 hours

### Test Impact
✅ Will fix 10+ tests once implemented

---

## 6. Learning Goals (LOW PRIORITY)

### Current State
- **Backend**: ❌ Not implemented
- **Frontend**: ❌ Not implemented

### Tests Affected: 5+
- Set learning goals for courses
- Track goal achievement
- Display goals to students

### Implementation Plan

#### Phase 1: Database Schema
```sql
CREATE TABLE learning_goals (
  id INTEGER PRIMARY KEY,
  course_id INTEGER NOT NULL,
  title VARCHAR(200) NOT NULL,
  description TEXT,
  order_index INTEGER NOT NULL,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  FOREIGN KEY (course_id) REFERENCES courses(id)
);
```

#### Phase 2: Backend API
```
GET  /api/v1/courses/{id}/goals      - List goals
POST /api/v1/courses/{id}/goals      - Create goal
PUT  /api/v1/goals/{id}              - Update goal
DELETE /api/v1/goals/{id}            - Delete goal
```

#### Phase 3: Frontend UI
- Course form: Add goals section
- Course viewer: Display goals
- Progress tracking: Track goal achievement

### Effort Estimate
- Phase 1 (Schema): 1 hour
- Phase 2 (Backend): 2-3 hours
- Phase 3 (Frontend): 3-4 hours
- **Total**: 6-8 hours

### Test Impact
✅ Will fix 5+ tests once implemented

---

## Implementation Priority & Timeline

### Sprint 1 (High Priority - 2 weeks)
1. **Course Content Management** (8-11 hours)
   - Week 1: Management dialog
   - Week 2: Content viewer

2. **Audit Log Export** (1-2 hours)
   - Week 1: Quick win

3. **Progress Tracking Dashboard** (11-16 hours)
   - Week 1: Dashboard component
   - Week 2: Details and reports

**Expected Impact**: +40 tests passing

---

### Sprint 2 (Medium Priority - 1 week)
1. **Course Prerequisites** (5-7 hours)
   - Backend + Frontend

2. **System Settings UI** (3-5 hours)
   - Admin settings page

**Expected Impact**: +18 tests passing

---

### Sprint 3 (Low Priority - 1 week)
1. **Learning Goals** (6-8 hours)
   - Schema + API + UI

**Expected Impact**: +5 tests passing

---

## Total Effort Estimate

| Priority | Features | Effort | Tests Fixed |
|----------|----------|--------|-------------|
| HIGH | 3 features | 20-29 hours | 46+ |
| MEDIUM | 2 features | 8-12 hours | 18 |
| LOW | 1 feature | 6-8 hours | 5 |
| **TOTAL** | **6 features** | **34-49 hours** | **69+** |

**Timeline**: 4-6 weeks (depending on team size and velocity)

---

## Success Metrics

### Before Implementation:
```
E2E Tests: ~787 passed, ~218 skipped
Feature Coverage: 78%
```

### After HIGH Priority Features:
```
E2E Tests: ~833 passed, ~172 skipped
Feature Coverage: 83%
```

### After MEDIUM Priority Features:
```
E2E Tests: ~851 passed, ~154 skipped
Feature Coverage: 85%
```

### After ALL Features:
```
E2E Tests: ~856 passed, ~149 skipped
Feature Coverage: 86%
```

### Remaining Skips (Expected):
- Production authentication tests (~100)
- Environment-specific tests (~30)
- Tests for truly future features (~19)

---

## Recommendations

### Immediate Action:
1. ✅ **START NOW**: Course Content Management (highest impact)
2. ✅ **QUICK WIN**: Audit Log Export (1-2 hours, 6 tests fixed)

### Next Sprint:
1. Progress Tracking Dashboard
2. System Settings UI

### Future Sprints:
1. Course Prerequisites
2. Learning Goals

---

## Files to Create/Modify

### New Components:
1. `frontend/src/app/components/courses/course-content-dialog/`
2. `frontend/src/app/components/courses/course-viewer/`
3. `frontend/src/app/components/progress/progress-dashboard/`
4. `frontend/src/app/components/progress/course-progress-detail/`
5. `frontend/src/app/components/settings/`

### Modified Components:
1. `frontend/src/app/components/courses/courses.component.html` (add button)
2. `frontend/src/app/components/audit/audit.component.html` (add export)
3. `frontend/src/app/components/courses/course-dialog/` (add prerequisites)

### New Backend Services:
1. `backend/app/api/v1/endpoints/progress.py` (if not exists)
2. `backend/app/api/v1/endpoints/learning_goals.py`

### Database Migrations:
1. `backend/migrations/versions/xxx_add_learning_goals.py`

---

## Testing Strategy

After each feature implementation:

1. **Run affected E2E tests**:
```bash
npx playwright test --grep "Course Content"
```

2. **Verify test pass rate improvement**

3. **Manual testing** to ensure quality

4. **Update this document** with actual results

---

**Document Status**: ✅ Complete
**Ready to Start**: Course Content Management + Audit Export
**Expected Timeline**: 4-6 weeks for all features
**Expected Test Improvement**: 787 → 856 tests passing (+9%)
