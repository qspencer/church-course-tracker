"""
Extended coverage for app.services.enrollment_service.CourseEnrollmentService.

The basic CRUD path is already covered by tests/test_services.py::
TestCourseEnrollmentService. This file targets the methods that were
uncovered by the 2026-05-18 evaluation (§3.2 finding Q6: service was
at 29% coverage):

- bulk_delete_enrollments (hard delete, soft delete, partial-failure)
- sync_from_planning_center (new + update paths)
- update_progress (missing enrollment, completion threshold, partial)
- _map_pc_status_to_enrollment_status (mapping table + default)
- _get_people_id_from_pc_person_id (found + not-found)
- get_enrollments sorting branches (asc, desc, unknown-field fallback)

Together these add ~18 tests that move coverage from ~27% to ~50%+ without
needing to mock the Planning Center HTTP client. The remaining gap
(bulk_enroll_from_pc_event / bulk_enroll_from_pc_list / import_registrations,
~400 LOC) requires HTTP mocking and is left for a follow-up.
"""
from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

from app.models.course import Course
from app.models.enrollment import CourseEnrollment
from app.models.member import People
from app.services.enrollment_service import CourseEnrollmentService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_enrollment(db, people_id: int, course_id: int, *, status: str = "enrolled",
                    progress: float = 0.0, pc_registration_id: str = None,
                    enrollment_date=None) -> CourseEnrollment:
    """Create + persist a CourseEnrollment row, returning it (with id set)."""
    e = CourseEnrollment(
        people_id=people_id,
        course_id=course_id,
        enrollment_date=enrollment_date or datetime.now(timezone.utc),
        status=status,
        progress_percentage=progress,
        planning_center_registration_id=pc_registration_id,
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


@pytest.fixture
def people_and_course(db_session, sample_people_data, sample_course_data):
    """Persist one person + one course and return their IDs."""
    person = People(**sample_people_data)
    course = Course(**sample_course_data)
    db_session.add_all([person, course])
    db_session.commit()
    db_session.refresh(person)
    db_session.refresh(course)
    return person, course


# ---------------------------------------------------------------------------
# bulk_delete_enrollments
# ---------------------------------------------------------------------------

class TestBulkDeleteEnrollments:
    def test_hard_delete_happy_path(self, db_session, people_and_course):
        person, course = people_and_course
        e1 = _make_enrollment(db_session, person.id, course.id, status="enrolled")
        e2 = _make_enrollment(db_session, person.id, course.id, status="enrolled")
        ids = [e1.id, e2.id]

        service = CourseEnrollmentService(db_session)
        result = service.bulk_delete_enrollments(ids, deleted_by=999, soft_delete=False)

        assert result["deleted_count"] == 2
        assert set(result["deleted_ids"]) == set(ids)
        assert result["failed_ids"] == []
        assert result["errors"] == []
        # Hard delete - rows really gone
        assert service.get_enrollment(e1.id) is None
        assert service.get_enrollment(e2.id) is None

    def test_soft_delete_marks_dropped(self, db_session, people_and_course):
        person, course = people_and_course
        e = _make_enrollment(db_session, person.id, course.id, status="enrolled")

        service = CourseEnrollmentService(db_session)
        result = service.bulk_delete_enrollments([e.id], deleted_by=42, soft_delete=True)

        # If the service returned errors, surface them in the assertion message
        # so failures point at the real problem instead of just a count.
        assert result["deleted_count"] == 1, f"errors={result.get('errors')}"
        # Soft delete - row exists but status flipped to "dropped"
        fetched = service.get_enrollment(e.id)
        assert fetched is not None
        assert fetched.status == "dropped"

    def test_partial_failure_when_some_ids_missing(self, db_session, people_and_course):
        person, course = people_and_course
        e = _make_enrollment(db_session, person.id, course.id)
        missing_id = 999_999

        service = CourseEnrollmentService(db_session)
        result = service.bulk_delete_enrollments([e.id, missing_id])

        assert result["deleted_count"] == 1
        assert result["deleted_ids"] == [e.id]
        assert result["failed_ids"] == [missing_id]
        assert len(result["errors"]) == 1
        assert result["errors"][0]["enrollment_id"] == missing_id
        assert "not found" in result["errors"][0]["error"].lower()

    def test_all_ids_missing(self, db_session):
        service = CourseEnrollmentService(db_session)
        result = service.bulk_delete_enrollments([1_000_001, 1_000_002])

        assert result["deleted_count"] == 0
        assert result["deleted_ids"] == []
        assert set(result["failed_ids"]) == {1_000_001, 1_000_002}
        assert len(result["errors"]) == 2


# ---------------------------------------------------------------------------
# sync_from_planning_center
# ---------------------------------------------------------------------------

class TestSyncFromPlanningCenter:
    def test_updates_existing_enrollment_when_pc_registration_id_matches(
        self, db_session, people_and_course
    ):
        person, course = people_and_course
        e = _make_enrollment(
            db_session, person.id, course.id, pc_registration_id="pc-reg-100"
        )

        service = CourseEnrollmentService(db_session)
        result = service.sync_from_planning_center(
            {"id": "pc-reg-100", "status": "confirmed", "notes": "Welcome"},
            updated_by=7,
        )

        assert result.id == e.id, "should update the existing enrollment, not create"
        assert result.registration_status == "confirmed"
        assert result.registration_notes == "Welcome"
        assert result.updated_by == 7

    def test_unknown_pc_registration_id_raises_until_resolved(
        self, db_session, people_and_course
    ):
        """Documented limitation: sync_from_planning_center with a brand-new
        pc_registration_id falls through to create_enrollment with placeholder
        people_id=0 / course_id=0 (the service has a TODO to resolve these
        from PC person/event IDs). The create_enrollment validator rejects
        people_id=0, surfacing the limitation as an HTTPException. Locking
        this in as a test makes the limitation explicit; remove this test
        once the resolution logic is implemented."""
        service = CourseEnrollmentService(db_session)
        with pytest.raises(HTTPException) as exc:
            service.sync_from_planning_center(
                {
                    "id": "pc-reg-new-200",
                    "status": "registered",
                    "notes": "First-time",
                    "created_at": datetime.now(timezone.utc),
                },
                updated_by=3,
            )
        # The service raises a 400-class error wrapping the people_id validation
        # from create_enrollment.
        assert exc.value.status_code in (400, 422, 500)


# ---------------------------------------------------------------------------
# update_progress edge cases
# ---------------------------------------------------------------------------

class TestUpdateProgress:
    def test_missing_enrollment_returns_none(self, db_session):
        service = CourseEnrollmentService(db_session)
        assert service.update_progress(999_999, 50.0) is None

    def test_full_progress_marks_completed(self, db_session, people_and_course):
        person, course = people_and_course
        e = _make_enrollment(db_session, person.id, course.id, progress=0.0)

        service = CourseEnrollmentService(db_session)
        result = service.update_progress(e.id, 100.0, updated_by=1)

        assert result is not None
        assert result.progress_percentage == 100.0
        assert result.status == "completed"
        assert result.completion_date is not None

    def test_partial_progress_marks_in_progress(self, db_session, people_and_course):
        person, course = people_and_course
        e = _make_enrollment(db_session, person.id, course.id, progress=0.0)

        service = CourseEnrollmentService(db_session)
        result = service.update_progress(e.id, 45.0)

        assert result is not None
        assert result.progress_percentage == 45.0
        assert result.status == "in_progress"
        # completion_date should remain unset for partial progress
        assert result.completion_date is None


# ---------------------------------------------------------------------------
# _map_pc_status_to_enrollment_status (helper)
# ---------------------------------------------------------------------------

class TestMapPCStatusToEnrollmentStatus:
    @pytest.mark.parametrize(
        ("pc_status", "expected"),
        [
            ("registered", "enrolled"),
            ("confirmed", "enrolled"),
            ("waitlisted", "enrolled"),
            ("cancelled", "dropped"),
            ("declined", "dropped"),
        ],
    )
    def test_known_statuses_map_correctly(self, db_session, pc_status, expected):
        service = CourseEnrollmentService(db_session)
        assert service._map_pc_status_to_enrollment_status(pc_status) == expected

    def test_unknown_status_defaults_to_enrolled(self, db_session):
        service = CourseEnrollmentService(db_session)
        assert service._map_pc_status_to_enrollment_status("anything-else") == "enrolled"

    def test_status_lookup_is_case_insensitive(self, db_session):
        service = CourseEnrollmentService(db_session)
        assert service._map_pc_status_to_enrollment_status("CANCELLED") == "dropped"
        assert service._map_pc_status_to_enrollment_status("Registered") == "enrolled"


# ---------------------------------------------------------------------------
# _get_people_id_from_pc_person_id (helper)
# ---------------------------------------------------------------------------

class TestGetPeopleIdFromPCPersonId:
    def test_returns_local_id_when_person_exists(self, db_session, sample_people_data):
        person = People(**sample_people_data)
        db_session.add(person)
        db_session.commit()
        db_session.refresh(person)

        service = CourseEnrollmentService(db_session)
        result = service._get_people_id_from_pc_person_id(person.planning_center_id)
        assert result == person.id

    def test_raises_404_when_person_not_found(self, db_session):
        service = CourseEnrollmentService(db_session)
        with pytest.raises(HTTPException) as exc:
            service._get_people_id_from_pc_person_id("pc-does-not-exist-xyz")
        assert exc.value.status_code == 404
        assert "Planning Center" in exc.value.detail


# ---------------------------------------------------------------------------
# get_enrollments sorting branches
# ---------------------------------------------------------------------------

class TestGetEnrollmentsSorting:
    def test_sort_by_status_ascending(self, db_session, people_and_course):
        person, course = people_and_course
        _make_enrollment(db_session, person.id, course.id, status="enrolled")
        _make_enrollment(db_session, person.id, course.id, status="completed")
        _make_enrollment(db_session, person.id, course.id, status="dropped")

        service = CourseEnrollmentService(db_session)
        results = service.get_enrollments(sort="status", order="asc")

        # The status values are "completed" < "dropped" < "enrolled" lexically
        statuses = [r.status for r in results]
        assert statuses == sorted(statuses)

    def test_sort_by_enrollment_date_desc(self, db_session, people_and_course):
        person, course = people_and_course
        # Create in non-chronological order so the sort is doing actual work
        older = _make_enrollment(
            db_session, person.id, course.id,
            enrollment_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
        )
        newer = _make_enrollment(
            db_session, person.id, course.id,
            enrollment_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )

        service = CourseEnrollmentService(db_session)
        results = service.get_enrollments(sort="enrollment_date", order="desc")

        assert [r.id for r in results] == [newer.id, older.id]

    def test_unknown_sort_field_falls_back_to_default(self, db_session, people_and_course):
        person, course = people_and_course
        _make_enrollment(
            db_session, person.id, course.id,
            enrollment_date=datetime(2024, 6, 1, tzinfo=timezone.utc),
        )
        _make_enrollment(
            db_session, person.id, course.id,
            enrollment_date=datetime(2025, 6, 1, tzinfo=timezone.utc),
        )

        service = CourseEnrollmentService(db_session)
        # Unknown field exercises the fall-through branch (line 75-76)
        results = service.get_enrollments(sort="bogus_field")
        # Fallback ordering is enrollment_date DESC, so newer first
        assert results[0].enrollment_date >= results[1].enrollment_date

    def test_sort_with_alias_enrolled_at(self, db_session, people_and_course):
        """`sort=enrolled_at` is the frontend field name; the service should
        accept it and map to the enrollment_date column."""
        person, course = people_and_course
        e1 = _make_enrollment(
            db_session, person.id, course.id,
            enrollment_date=datetime(2023, 1, 1, tzinfo=timezone.utc),
        )
        e2 = _make_enrollment(
            db_session, person.id, course.id,
            enrollment_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )

        service = CourseEnrollmentService(db_session)
        results = service.get_enrollments(sort="enrolled_at", order="asc")
        assert [r.id for r in results] == [e1.id, e2.id]
