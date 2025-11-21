# Data Model Feedback & Recommendations

## Overview

This document addresses three key pieces of feedback about the current data model and provides recommendations for improvements.

---

## 1. People <-> Campus Relationship (N:M → 1:M)

### Current Implementation

**Status**: ❌ Currently N:M relationship via `people_campus` junction table

**Current Model**:
```python
# backend/app/models/people_campus.py
class PeopleCampus(Base):
    people_id: Integer (FK to people.id)
    campus_id: Integer (FK to campus.id)
    assigned_date: Date
    is_primary: Boolean  # Supports multiple campuses per person
    is_active: Boolean
```

**Issues**:
- Allows one person to be assigned to multiple campuses simultaneously
- Uses `is_primary` flag to indicate primary campus
- Supports historical tracking but enables multiple active assignments

### Requirements

1. **1:M Relationship**: One person → One campus at a time (can change over time)
2. **Historical Tracking**: Track campus assignment changes over time
3. **Data Source Question**: Should campus be stored locally or fetched from Planning Center API when needed?

### Recommendations

#### Option A: 1:M with Historical Tracking (Recommended) ✅

**Approach**: Change `people_campus` to support one active assignment with historical tracking

**Changes Needed**:

1. **Add `campus_id` directly to `People` model** (optional nullable FK):
   ```python
   # backend/app/models/member.py
   class People(Base):
       # ... existing fields ...
       campus_id = Column(Integer, ForeignKey("campus.id"), nullable=True, index=True)
       campus_assigned_date = Column(Date, nullable=True)  # When current assignment started
       campus = relationship("Campus", foreign_keys=[campus_id])
   ```

2. **Keep `people_campus` for historical tracking**:
   ```python
   class PeopleCampus(Base):
       people_id: Integer
       campus_id: Integer
       assigned_date: Date  # When assignment started
       unassigned_date: Date  # When assignment ended (NULL = current)
       is_active: Boolean  # FALSE if unassigned_date is set
       notes: Text  # Reason for change
   ```

3. **Migration Strategy**:
   - Migrate current active assignment (`is_primary=True` or first active) to `People.campus_id`
   - Keep all historical records in `people_campus` table
   - Update application logic to:
     - Set `People.campus_id` when assigning campus
     - Create `PeopleCampus` record with `assigned_date`
     - When changing campus, set `unassigned_date` on old record, create new record

**Benefits**:
- ✅ Simple query for current campus (`People.campus_id`)
- ✅ Historical tracking maintained
- ✅ Easy to change campus assignment
- ✅ Can still query history

#### Option B: Remove Local Campus Storage (Alternative)

**Approach**: Remove campus from local database, fetch from Planning Center API when needed

**Changes Needed**:
1. Remove `people_campus` table entirely
2. Remove campus-related fields from `People` model
3. Fetch campus from Planning Center API via `planning_center_id` when needed
4. Cache campus data in application layer if performance is a concern

**Benefits**:
- ✅ Single source of truth (Planning Center)
- ✅ No sync issues
- ✅ Simpler data model

**Drawbacks**:
- ❌ Requires Planning Center API call for campus data
- ❌ No offline campus data
- ❌ No historical tracking of campus changes
- ❌ Performance impact if campus is needed frequently

### Recommendation: **Option A (1:M with Historical Tracking)** ✅

**Rationale**:
- Provides current assignment easily (1:M query)
- Maintains historical tracking for audit/compliance
- Allows campus data to be used without API calls
- Can still sync with Planning Center if needed
- Better performance for queries that need campus

**Implementation Priority**: Medium

---

## 2. Course Enrollment Methods

### Current Implementation

**Status**: ⚠️ Partially Implemented

**Current Model**:
```python
# backend/app/models/enrollment.py
class CourseEnrollment(Base):
    people_id: Integer
    course_id: Integer
    planning_center_registration_id: String (nullable)  # Links to PC if synced
    enrollment_date: DateTime
    status: String  # enrolled, in_progress, completed, dropped
    data_source: String  # 'csv', 'api', 'manual', etc.
```

**Existing Functionality**:
- ✅ Manual enrollment supported (`planning_center_registration_id = None`)
- ✅ Bulk enrollment method exists in `EnrollmentService.bulk_enroll()`
- ✅ Planning Center registration sync supported

### Requirements

1. **Multiple Enrollment Methods**:
   - Manual enrollment (within application)
   - Planning Center Registration sync
   - Bulk enrollment from Planning Center Registration events

2. **Bulk Enrollment Feature**:
   - Enroll multiple people based on who signed up for a Planning Center Registration event
   - Should work for both new and existing registrations

### Recommendations

#### Enhanced Enrollment Service ✅

**Changes Needed**:

1. **Add Bulk Enrollment from Planning Center Event**:
   ```python
   # backend/app/services/enrollment_service.py
   def bulk_enroll_from_pc_event(
       self, 
       course_id: int, 
       pc_event_id: str, 
       created_by: Optional[int] = None,
       status_filter: Optional[List[str]] = None  # ['registered', 'waitlisted']
   ) -> List[CourseEnrollmentModel]:
       """
       Bulk enroll people based on Planning Center Registration event
       
       Args:
           course_id: The course to enroll people in
           pc_event_id: Planning Center event ID to get registrations from
           created_by: User creating the enrollments
           status_filter: Only enroll registrations with these statuses
       
       Returns:
           List of created/updated enrollments
       """
   ```

2. **Update Enrollment Endpoints**:
   ```python
   # backend/app/api/v1/endpoints/enrollments.py
   @router.post("/bulk-from-pc-event")
   async def bulk_enroll_from_pc_event(
       enrollment_data: BulkEnrollFromPCEventRequest,
       current_user: dict = Depends(get_current_active_user),
       db: Session = Depends(get_db)
   ):
       """Bulk enroll people from a Planning Center Registration event"""
   ```

3. **Frontend UI Enhancement**:
   - Add "Bulk Enroll from Planning Center" option in enrollment dialog
   - Show Planning Center events that can be synced
   - Allow selecting which registration statuses to include (registered, waitlisted, etc.)

**Implementation Details**:

1. **Service Layer** (`enrollment_service.py`):
   ```python
   def bulk_enroll_from_pc_event(
       self, 
       course_id: int, 
       pc_event_id: str,
       created_by: Optional[int] = None,
       status_filter: Optional[List[str]] = None
   ) -> List[CourseEnrollmentModel]:
       """Bulk enroll from PC event registrations"""
       from app.services.planning_center_sync_service import PlanningCenterSyncService
       
       pc_service = PlanningCenterSyncService(self.db)
       
       # Get registrations for this event
       registrations = pc_service.get_event_registrations(pc_event_id)
       
       if status_filter:
           registrations = [r for r in registrations if r.status in status_filter]
       
       enrollments = []
       for reg in registrations:
           # Find or create enrollment
           existing = self.get_enrollment_by_pc_registration_id(reg.id)
           if existing:
               # Update existing
               existing.status = self._map_pc_status_to_enrollment_status(reg.status)
               enrollments.append(existing)
           else:
               # Create new enrollment
               enrollment = CourseEnrollmentCreate(
                   people_id=self._get_people_id_from_pc_person_id(reg.person_id),
                   course_id=course_id,
                   planning_center_registration_id=reg.id,
                   enrollment_date=reg.registration_date,
                   status=self._map_pc_status_to_enrollment_status(reg.status),
                   registration_status=reg.status,
                   data_source='api'
               )
               enrollments.append(self.create_enrollment(enrollment, created_by))
       
       return enrollments
   ```

2. **Schema** (`backend/app/schemas/enrollment.py`):
   ```python
   class BulkEnrollFromPCEventRequest(BaseModel):
       course_id: int
       pc_event_id: str
       status_filter: Optional[List[str]] = ['registered']  # registered, waitlisted, etc.
       update_existing: bool = True  # Update existing enrollments
   ```

**Implementation Priority**: High

---

## 3. Course Instances & Life on Life Discipleship Tracking

### Current Implementation

**Status**: ❌ Not Implemented

**Current Model**:
```python
# backend/app/models/course.py
class Course(Base):
    # Represents a "Master Course" with content
    event_start_date: DateTime  # Suggests single instance
    event_end_date: DateTime
    # No concept of multiple instances or teachers
```

**Issues**:
- Course model mixes "Master Course" (content definition) with "Instance" (specific offering)
- No way to track multiple offerings of the same course
- No teacher/mentor tracking for specific instances
- Cannot track "who is discipling whom" relationship

### Requirements

1. **Master Course vs Course Instance**:
   - Master Course: Content definition, prerequisites, modules
   - Course Instance: Specific offering with start/end dates, schedule, teachers

2. **Teacher Tracking**:
   - Track which People are teachers for a specific Course Instance
   - Support multiple teachers per instance
   - Track teacher-student relationships ("who is discipling whom")

3. **Life on Life Discipleship**:
   - One-on-one or small group discipleship tracking
   - Track mentor/mentee relationships
   - Track progress within a Course Instance

### Recommendations

#### New Data Model: Course Instance Architecture ✅

**Approach**: Separate Master Course from Course Instance, add teacher tracking

**New Models**:

1. **Course Model (Becomes "Master Course")**:
   ```python
   # backend/app/models/course.py
   class Course(Base):
       """Master Course - Content definition"""
       __tablename__ = "courses"
       
       id: Integer
       title: String
       description: Text
       duration_weeks: Integer
       prerequisites: JSON  # List of course IDs
       
       # Remove instance-specific fields:
       # event_start_date (move to CourseInstance)
       # event_end_date (move to CourseInstance)
       # max_capacity (move to CourseInstance)
       # current_registrations (move to CourseInstance)
       
       # Keep Planning Center mapping at master course level
       planning_center_event_template_id: String  # Template/Series ID
       
       # Relationships
       course_instances = relationship("CourseInstance", back_populates="course")
       modules = relationship("CourseModule", back_populates="course")
       course_content = relationship("CourseContent", back_populates="course")
   ```

2. **New CourseInstance Model**:
   ```python
   # backend/app/models/course_instance.py (NEW)
   class CourseInstance(Base):
       """Course Instance - Specific offering of a Master Course"""
       __tablename__ = "course_instances"
       
       id: Integer
       course_id: Integer (FK to courses.id)  # Links to Master Course
       instance_name: String  # e.g., "Fall 2024 - Session A"
       start_date: DateTime
       end_date: DateTime
       schedule: JSON  # Optional: {"day_of_week": "Monday", "time": "19:00", "frequency": "weekly"}
       max_capacity: Integer
       current_enrollments: Integer
       
       # Planning Center mapping (specific event)
       planning_center_event_id: String (unique)  # Specific PC Event ID
       planning_center_event_name: String
       
       # Status
       is_active: Boolean
       enrollment_open: Boolean
       enrollment_deadline: DateTime
       
       # Location
       campus_id: Integer (FK to campus.id, nullable)
       
       # Relationships
       course = relationship("Course", back_populates="course_instances")
       teachers = relationship("CourseInstanceTeacher", back_populates="course_instance")
       enrollments = relationship("CourseEnrollment", back_populates="course_instance")
   ```

3. **New CourseInstanceTeacher Model**:
   ```python
   # backend/app/models/course_instance_teacher.py (NEW)
   class CourseInstanceTeacher(Base):
       """Teacher/Mentor for a Course Instance"""
       __tablename__ = "course_instance_teachers"
       
       id: Integer
       course_instance_id: Integer (FK to course_instances.id)
       people_id: Integer (FK to people.id)  # Teacher
       role_type: String  # 'teacher', 'mentor', 'assistant', 'co-teacher'
       assigned_date: Date
       is_primary: Boolean  # Primary teacher/mentor
       max_students: Integer  # For 1:1 discipleship tracking
       is_active: Boolean
       
       # Relationships
       course_instance = relationship("CourseInstance", back_populates="teachers")
       people = relationship("People", back_populates="teaching_instances")
       assigned_students = relationship(
           "CourseEnrollment", 
           foreign_keys="[CourseEnrollment.assigned_teacher_id]",
           back_populates="assigned_teacher"
       )
   ```

4. **Update CourseEnrollment Model**:
   ```python
   # backend/app/models/enrollment.py
   class CourseEnrollment(Base):
       """Enrollment links Person to CourseInstance (not Course)"""
       
       id: Integer
       people_id: Integer (FK to people.id)
       course_instance_id: Integer (FK to course_instances.id)  # CHANGED from course_id
       
       # Teacher assignment for discipleship tracking
       assigned_teacher_id: Integer (FK to course_instance_teachers.id, nullable)
       
       # Rest of fields remain the same...
   ```

5. **Update CourseRole Model** (Alternative to CourseInstanceTeacher):
   ```python
   # Option: Use existing CourseRole model at instance level
   # backend/app/models/course_role.py
   class CourseRole(Base):
       course_instance_id: Integer (FK to course_instances.id)  # CHANGED from course_id
       people_id: Integer
       role_type: String  # 'teacher', 'student', 'mentor', 'mentee'
   ```

### Recommended Approach: **Separate Teacher Model** ✅

**Rationale**:
- `CourseInstanceTeacher` provides clearer teacher-specific fields (max_students, is_primary)
- Better for tracking teacher-student assignments
- Allows assigning students to specific teachers for discipleship tracking
- More flexible than using `CourseRole` for both students and teachers

### Implementation Strategy

#### Phase 1: Add Course Instance Model

1. **Create CourseInstance Model**:
   - Move instance-specific fields from `Course` to `CourseInstance`
   - Add 1:M relationship: `Course` → `CourseInstance`

2. **Migration**:
   - Create `course_instances` table
   - For each existing `Course`, create a default `CourseInstance`
   - Migrate `event_start_date`, `event_end_date`, `max_capacity` to instance
   - Update `CourseEnrollment` to reference `course_instance_id` instead of `course_id`

3. **Update Services**:
   - `CourseService`: Add instance management methods
   - `EnrollmentService`: Update to work with instances
   - API endpoints: Add instance CRUD operations

#### Phase 2: Add Teacher Tracking

1. **Create CourseInstanceTeacher Model**:
   - Support multiple teachers per instance
   - Track primary teacher
   - Support max_students for 1:1 discipleship

2. **Update CourseEnrollment**:
   - Add `assigned_teacher_id` field
   - Allow assigning students to specific teachers

3. **API Endpoints**:
   - Assign/remove teachers from instances
   - Assign students to teachers
   - Query "who is discipling whom"

#### Phase 3: Life on Life Discipleship Features

1. **Teacher-Student Assignment**:
   - UI to assign students to specific teachers
   - Auto-assignment based on availability
   - Tracking of mentor/mentee relationships

2. **Reporting**:
   - List of students per teacher
   - Teacher workload reports
   - Discipleship relationship reports

### Data Model Diagram

```
┌──────────────────┐
│  COURSE          │ (Master Course - Content Definition)
│  (Master)        │
└──────────────────┘
         │
         │ 1:N
         │
         ▼
┌──────────────────┐
│ COURSE_INSTANCE  │ (Specific Offering)
│                  │
│ - start_date     │
│ - end_date       │
│ - schedule       │
│ - teachers       │
└──────────────────┘
         │
         │ 1:N         │ 1:N
         │             │
         ▼             ▼
┌──────────────────┐ ┌──────────────────────────┐
│COURSE_ENROLLMENT │ │ COURSE_INSTANCE_TEACHER  │
│                  │ │                          │
│ - assigned_      │ │ - people_id (teacher)    │
│   teacher_id ────┼─┤ - max_students          │
│                  │ │ - role_type             │
└──────────────────┘ └──────────────────────────┘
         │                     │
         │                     │
         ▼                     ▼
┌──────────────────┐ ┌──────────────────┐
│    PEOPLE        │ │    PEOPLE        │
│  (Student)       │ │   (Teacher)      │
└──────────────────┘ └──────────────────┘
```

### Migration Considerations

1. **Backward Compatibility**:
   - Create default `CourseInstance` for each existing `Course`
   - Update `CourseEnrollment.course_id` → `course_instance_id` during migration
   - Keep `course_id` temporarily with computed property if needed

2. **API Changes**:
   - Add new endpoints for instance management
   - Keep existing course endpoints (create instance automatically if needed)
   - Deprecate old endpoints gradually

3. **Planning Center Integration**:
   - Map PC Events → `CourseInstance` (specific offering)
   - Map PC Event Templates/Series → `Course` (master course)

### Implementation Priority: **High** (Core Feature)

---

## Summary of Recommendations

| Feature | Priority | Recommendation | Complexity |
|---------|----------|----------------|------------|
| **1. Campus 1:M** | Medium | Add `campus_id` to `People`, keep `people_campus` for history | Low |
| **2. Bulk Enrollment** | High | Add `bulk_enroll_from_pc_event()` method | Medium |
| **3. Course Instances** | High | Create `CourseInstance` model, separate from `Course` | High |
| **3. Teacher Tracking** | High | Create `CourseInstanceTeacher` model with student assignment | High |

---

## Implementation Order

### Sprint 1: Quick Wins (Low Complexity)
1. ✅ Add bulk enrollment from PC event endpoint
2. ✅ Update enrollment UI for bulk operations

### Sprint 2: Campus Relationship (Medium Complexity)
1. ✅ Add `campus_id` to `People` model
2. ✅ Migrate existing campus assignments
3. ✅ Update services to maintain history

### Sprint 3: Course Instances (High Complexity)
1. ✅ Create `CourseInstance` model
2. ✅ Migrate existing courses to instances
3. ✅ Update enrollment to use instances
4. ✅ Update API endpoints

### Sprint 4: Teacher Tracking (High Complexity)
1. ✅ Create `CourseInstanceTeacher` model
2. ✅ Add teacher assignment to instances
3. ✅ Add student-teacher assignment to enrollments
4. ✅ Create UI for teacher management

---

## Questions for Stakeholder

1. **Campus Storage**: Do you want to keep campus data locally (Option A) or fetch from Planning Center (Option B)?

2. **Course Instance Name**: What should we call "Course Instance"? (e.g., "Course Offering", "Course Session", "Course Cohort")

3. **Teacher Model**: Should we use separate `CourseInstanceTeacher` model or extend `CourseRole`?

4. **Discipleship Tracking**: Do you need:
   - 1:1 teacher-student assignments?
   - Small group assignments (multiple students per teacher)?
   - Mentor/mentee relationship tracking (different from teacher)?

5. **Migration Strategy**: For existing courses, should we:
   - Create one default instance per course automatically?
   - Require manual instance creation going forward?
   - Support both master courses without instances and instances?

---

*Document Created: January 2025*  
*Status: Awaiting Stakeholder Review*

