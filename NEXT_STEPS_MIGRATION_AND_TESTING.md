# Next Steps: Migration and Testing Guide

## Overview

This document outlines the next steps for implementing and testing Phase 2 (Campus 1:M) and Phase 3 (Course Offerings) features.

---

## Step 1: Run Database Migrations

### Prerequisites

1. **Database Connection**: Ensure `DATABASE_URL` environment variable is set
2. **Database Access**: Verify you have access to the database
3. **Backup**: Consider backing up the database before running migrations

### Running Migrations

#### Local Development

```bash
cd backend

# Check current migration status
alembic current

# View pending migrations
alembic heads

# Run migrations to latest version
alembic upgrade head

# If there are issues, check migration history
alembic history
```

#### Production/Staging (via ECS)

If running in AWS ECS, migrations can be run via:

```bash
# Use the provided script
./scripts/run-migrations-via-ecs.sh

# Or manually execute in ECS container
aws ecs execute-command \
    --cluster church-course-tracker-cluster \
    --task <TASK_ARN> \
    --container <CONTAINER_NAME> \
    --interactive \
    --command "alembic upgrade head"
```

### Migration Order

The migrations must be run in order:

1. **m4n5o6p7q8r9** - `add_campus_1m_relationship.py`
   - Adds `campus_id` to `people` table
   - Adds `unassigned_date` to `people_campus` table
   - Migrates existing campus assignments

2. **n5o6p7q8r9s0** - `add_course_offerings_architecture.py`
   - Creates `course_instances` table
   - Creates `course_instance_teachers` table
   - Updates `course_enrollment` table
   - Migrates existing courses to course instances

### Verification

After running migrations, verify:

```sql
-- Check people table has campus_id
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'people' AND column_name = 'campus_id';

-- Check course_instances table exists
SELECT table_name FROM information_schema.tables 
WHERE table_name = 'course_instances';

-- Check course_instance_teachers table exists
SELECT table_name FROM information_schema.tables 
WHERE table_name = 'course_instance_teachers';

-- Check course_enrollment has new columns
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'course_enrollment' 
AND column_name IN ('course_instance_id', 'assigned_teacher_id');
```

---

## Step 2: Test New API Endpoints

### Course Instances (Course Offerings)

#### 1. List Course Instances

```bash
curl -X GET "http://localhost:8000/api/v1/course-instances" \
  -H "Authorization: Bearer <token>"
```

#### 2. Get Specific Course Instance

```bash
curl -X GET "http://localhost:8000/api/v1/course-instances/1" \
  -H "Authorization: Bearer <token>"
```

#### 3. Create Course Instance

```bash
curl -X POST "http://localhost:8000/api/v1/course-instances" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "course_id": 1,
    "instance_name": "Fall 2024 - Session A",
    "start_date": "2024-09-01T00:00:00Z",
    "end_date": "2024-12-15T23:59:59Z",
    "is_active": true,
    "enrollment_open": true
  }'
```

#### 4. Update Course Instance

```bash
curl -X PATCH "http://localhost:8000/api/v1/course-instances/1" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "instance_name": "Updated Name",
    "enrollment_open": false
  }'
```

#### 5. Add Teacher to Instance

```bash
curl -X POST "http://localhost:8000/api/v1/course-instances/1/teachers" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "people_id": 1,
    "role_type": "teacher",
    "assigned_date": "2024-09-01",
    "is_primary": true
  }'
```

#### 6. List Teachers for Instance

```bash
curl -X GET "http://localhost:8000/api/v1/course-instances/1/teachers" \
  -H "Authorization: Bearer <token>"
```

#### 7. Assign Student to Teacher

```bash
curl -X POST "http://localhost:8000/api/v1/course-instances/enrollments/1/assign-teacher?teacher_id=1" \
  -H "Authorization: Bearer <token>"
```

### Campus Assignment (Phase 2)

Campus assignment is currently handled via the service layer. To assign a campus:

```python
from app.services.people_service import PeopleService
from datetime import date

people_service = PeopleService(db_session)
people_service.assign_campus(
    person_id=1,
    campus_id=2,
    assigned_date=date.today(),
    notes="Campus change",
    updated_by=current_user_id
)
```

**Future Enhancement**: Add API endpoint `PATCH /api/v1/people/{id}/campus`

---

## Step 3: Run Automated Tests

### Backend Tests

```bash
cd backend

# Run all tests
pytest tests/ -v

# Run specific test file for course instances
pytest tests/test_course_instances.py -v

# Run with coverage
pytest tests/test_course_instances.py --cov=app.services.course_instance_service --cov=app.api.v1.endpoints.course_instances -v
```

### E2E Tests

```bash
cd tests/e2e

# Run API tests (if configured)
npm test api-improvements.spec.ts

# Or with Playwright
npx playwright test api-improvements.spec.ts
```

---

## Step 4: Integration Testing

### Test Scenarios

#### Scenario 1: Create Course Offering and Enroll Students

1. Create a Master Course
2. Create a Course Instance (Offering)
3. Add teachers to the instance
4. Enroll students in the instance
5. Assign students to teachers
6. Verify enrollment and teacher assignments

#### Scenario 2: Campus Assignment

1. Create campuses
2. Assign people to campuses
3. Change campus assignments
4. Verify historical tracking in `people_campus` table
5. Verify current assignment in `people.campus_id`

#### Scenario 3: Multiple Offerings

1. Create a Master Course
2. Create multiple Course Instances with different dates
3. Enroll students in different instances
4. Verify enrollments are correctly associated

---

## Step 5: Data Migration Verification

### Check Migrated Data

```sql
-- Verify course instances were created from courses
SELECT 
    c.id as course_id,
    c.title as course_title,
    ci.id as instance_id,
    ci.instance_name
FROM courses c
LEFT JOIN course_instances ci ON ci.course_id = c.id
WHERE c.event_start_date IS NOT NULL OR c.planning_center_event_id IS NOT NULL;

-- Verify enrollments were linked to instances
SELECT 
    ce.id as enrollment_id,
    ce.course_id as old_course_id,
    ce.course_instance_id as new_instance_id,
    ci.instance_name
FROM course_enrollment ce
LEFT JOIN course_instances ci ON ci.id = ce.course_instance_id
WHERE ce.course_instance_id IS NOT NULL;

-- Verify campus assignments were migrated
SELECT 
    p.id as person_id,
    p.first_name,
    p.last_name,
    p.campus_id,
    c.name as campus_name,
    p.campus_assigned_date
FROM people p
LEFT JOIN campus c ON c.id = p.campus_id
WHERE p.campus_id IS NOT NULL;
```

---

## Step 6: Frontend Integration (If Applicable)

### Update Frontend to Use Course Instances

1. **Update Course Service** to use `/api/v1/course-instances`
2. **Update Enrollment Component** to reference `course_instance_id`
3. **Add Teacher Management UI** for course offerings
4. **Update Campus Assignment UI** (if endpoint is added)

### API Calls

```typescript
// Get course instances for a course
GET /api/v1/course-instances?course_id={courseId}

// Create new offering
POST /api/v1/course-instances

// Get teachers for an offering
GET /api/v1/course-instances/{instanceId}/teachers

// Assign student to teacher
POST /api/v1/course-instances/enrollments/{enrollmentId}/assign-teacher?teacher_id={teacherId}
```

---

## Troubleshooting

### Migration Issues

**Issue**: Multiple Alembic heads detected
```bash
# Merge heads
alembic merge heads -m "merge heads"

# Then upgrade
alembic upgrade head
```

**Issue**: Migration fails due to existing data
```bash
# Check migration history
alembic history

# Downgrade if needed
alembic downgrade -1

# Fix data issues
# Then upgrade again
alembic upgrade head
```

**Issue**: Foreign key constraint violations
- Check that referenced records exist (campuses, courses, people)
- Verify data integrity before migration

### API Issues

**Issue**: 404 Not Found for course instances endpoint
- Verify API router includes course_instances
- Check `/api/v1/course-instances` is registered
- Verify server is restarted after changes

**Issue**: 403 Forbidden for course instance operations
- Verify user has `admin` or `staff` role
- Check JWT token includes correct role
- Verify `get_current_active_user` dependency

---

## Checklist

- [ ] Database migrations run successfully
- [ ] All new tables created (`course_instances`, `course_instance_teachers`)
- [ ] All columns added to existing tables (`people.campus_id`, etc.)
- [ ] Existing data migrated correctly
- [ ] API endpoints accessible and working
- [ ] Tests pass for course instances
- [ ] Authorization working correctly
- [ ] Integration tests pass
- [ ] Documentation updated
- [ ] Frontend updated (if applicable)
- [ ] Production deployment plan created

---

## Optional Enhancements

### Phase 2 Enhancements

1. **Add Campus Assignment API Endpoint**
   ```python
   PATCH /api/v1/people/{id}/campus
   {
       "campus_id": 1,
       "assigned_date": "2024-01-15",
       "notes": "Campus change"
   }
   ```

2. **Add Campus History Endpoint**
   ```python
   GET /api/v1/people/{id}/campus-history
   ```

3. **Planning Center Campus Sync**
   - Implement in `PlanningCenterSyncService`
   - Periodic sync job to update campuses

### Phase 3 Enhancements

1. **Bulk Enrollment to Course Instance**
   ```python
   POST /api/v1/course-instances/{id}/bulk-enroll
   ```

2. **Teacher Capacity Management**
   - Auto-assign students based on teacher capacity
   - Track teacher workload

3. **Course Instance Calendar View**
   - Schedule visualization
   - Conflict detection

4. **Discipleship Reporting**
   - Who is discipling whom
   - Progress tracking per teacher-student relationship

---

## Support

For issues or questions:
1. Check migration logs
2. Review API endpoint documentation at `/docs`
3. Check test files for usage examples
4. Review `PHASE_2_AND_3_IMPLEMENTATION_SUMMARY.md`

---

**Status**: Ready for migration and testing  
**Last Updated**: January 2025

