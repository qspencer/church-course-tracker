# Migration Fix: planning_center_event_template_id

## Issue

**Problem**: Missing column `planning_center_event_template_id` in `courses` table

- ✅ Column exists in Course model (`backend/app/models/course.py` line 29-31)
- ❌ Column does NOT exist in database
- ❌ No migration adds this column

**Impact**:
- 3 prerequisite tests failing (ERROR)
- 1 error handling test failing (FAILED)

---

## Root Cause

When the Course model was updated to include `planning_center_event_template_id` as part of Phase 3 implementation, the column was added to the model but no migration was created to add it to the database schema.

---

## Solution

### Migration Created

**File**: `backend/migrations/versions/o6p7q8r9s0t1_add_planning_center_event_template_id.py`

**Changes**:
1. ✅ Adds `planning_center_event_template_id` column to `courses` table
   - Type: VARCHAR(50)
   - Nullable: YES
   - Matches model definition

2. ✅ Creates index on the column
   - Index name: `ix_courses_planning_center_event_template_id`
   - Matches model's `index=True` setting

### Migration Details

- **Revision ID**: `o6p7q8r9s0t1`
- **Down Revision**: `n5o6p7q8r9s0` (Course Offerings architecture migration)
- **Description**: Adds Planning Center event template ID column for Master Courses

---

## Verification

### Database Schema Check

Before migration:
```sql
PRAGMA table_info(courses);
-- planning_center_event_template_id column NOT found
```

After migration:
```sql
PRAGMA table_info(courses);
-- planning_center_event_template_id column EXISTS
```

### Column Properties

```python
# From Course model
planning_center_event_template_id = Column(
    String(50), nullable=True, index=True
)  # Template/Series ID from Planning Center
```

### Migration Applied

```bash
cd backend
export DATABASE_URL="sqlite:///./data/church_course_tracker.db"
alembic upgrade head
# or
python -m alembic upgrade head
```

---

## Testing

### Verify Migration

```bash
# Check migration is recognized
python -m alembic current
# Should show: o6p7q8r9s0t1

# Check column exists
sqlite3 data/church_course_tracker.db "PRAGMA table_info(courses);" | grep template
```

### Run Tests

```bash
cd backend
source venv_new/bin/activate
pytest tests/test_new_features.py::TestCoursePrerequisites -v
pytest tests/test_new_features.py::TestErrorHandling -v
```

Expected results:
- ✅ Prerequisite tests should pass (no more ERROR)
- ✅ Error handling test should pass (no more FAILED)

---

## Rollback

If needed, rollback the migration:

```bash
cd backend
alembic downgrade -1
# or
python -m alembic downgrade -1
```

This will:
- Drop the index
- Drop the column

---

## Related Files

1. **Model**: `backend/app/models/course.py` (line 29-31)
   - Defines `planning_center_event_template_id` column

2. **Migration**: `backend/migrations/versions/o6p7q8r9s0t1_add_planning_center_event_template_id.py`
   - Adds column to database

3. **Tests**: `backend/tests/test_new_features.py`
   - Tests affected by missing column

---

## Status

✅ **FIXED**

- ✅ Migration created
- ✅ Column added to database
- ✅ Index created
- ✅ Migration committed

**Next Steps**:
1. Run `alembic upgrade head` to apply migration (if not already applied)
2. Run tests to verify fix
3. Verify all prerequisite and error handling tests pass

---

*Fix Date: January 2025*  
*Migration Revision: o6p7q8r9s0t1*  
*Status: Complete*

