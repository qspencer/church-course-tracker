"""
Tests for program pairing constraint validation
"""

import pytest
from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.program import Program, ProgramParticipant, ProgramPairing
from app.models.member import People
from app.models.user import User


class TestPairingConstraintValidation:
    """Test pairing constraint validation logic"""

    def test_create_pairing_with_max_secondary_limit(self, client, db_session, admin_token):
        """Test that max_secondary_per_primary constraint is enforced"""
        # Get admin user ID from token
        from app.core.security import verify_token
        admin_user_id = verify_token(admin_token)
        if admin_user_id is None:
            admin_user_id = 1  # Fallback if token verification fails

        # Create program with max_secondary_per_primary = 2
        program = Program(
            title="Test Program",
            description="Test",
            relationship_config={
                "allow_multiple_secondary": True,
                "max_secondary_per_primary": 2
            },
            role_definitions=[
                {"name": "Mentor", "is_primary": True},
                {"name": "Mentee", "is_primary": False}
            ],
            created_by=admin_user_id,
            updated_by=admin_user_id
        )
        db_session.add(program)
        db_session.commit()
        db_session.refresh(program)

        # Create people
        person1 = People(planning_center_id="pc_test_1", first_name="Primary", last_name="Person", email="primary@test.com")
        person2 = People(planning_center_id="pc_test_2", first_name="Secondary1", last_name="Person", email="secondary1@test.com")
        person3 = People(planning_center_id="pc_test_3", first_name="Secondary2", last_name="Person", email="secondary2@test.com")
        person4 = People(planning_center_id="pc_test_4", first_name="Secondary3", last_name="Person", email="secondary3@test.com")
        db_session.add_all([person1, person2, person3, person4])
        db_session.commit()

        # Create participants
        primary = ProgramParticipant(
            program_id=program.id,
            people_id=person1.id,
            role_name="Mentor",
            status="active",
            start_date=datetime.now(timezone.utc),
            created_by=admin_user_id
        )
        secondary1 = ProgramParticipant(
            program_id=program.id,
            people_id=person2.id,
            role_name="Mentee",
            status="active",
            start_date=datetime.now(timezone.utc),
            created_by=admin_user_id
        )
        secondary2 = ProgramParticipant(
            program_id=program.id,
            people_id=person3.id,
            role_name="Mentee",
            status="active",
            start_date=datetime.now(timezone.utc),
            created_by=admin_user_id
        )
        secondary3 = ProgramParticipant(
            program_id=program.id,
            people_id=person4.id,
            role_name="Mentee",
            status="active",
            start_date=datetime.now(timezone.utc),
            created_by=admin_user_id
        )
        db_session.add_all([primary, secondary1, secondary2, secondary3])
        db_session.commit()

        # Create first pairing (should succeed)
        response = client.post(
            f"/api/v1/programs/{program.id}/pairings",
            json={
                "program_id": program.id,
                "primary_participant_id": primary.id,
                "secondary_participant_id": secondary1.id,
                "status": "active"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201

        # Create second pairing (should succeed - at limit)
        response = client.post(
            f"/api/v1/programs/{program.id}/pairings",
            json={
                "program_id": program.id,
                "primary_participant_id": primary.id,
                "secondary_participant_id": secondary2.id,
                "status": "active"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201

        # Try to create third pairing (should fail - exceeds max)
        response = client.post(
            f"/api/v1/programs/{program.id}/pairings",
            json={
                "program_id": program.id,
                "primary_participant_id": primary.id,
                "secondary_participant_id": secondary3.id,
                "status": "active"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 400
        assert "maximum" in response.json()["detail"].lower()
        assert "2" in response.json()["detail"]

    def test_create_pairing_with_multiple_secondary_not_allowed(self, client, db_session, admin_token):
        """Test that allow_multiple_secondary = false constraint is enforced"""
        # Get admin user ID from token
        from app.core.security import verify_token
        admin_user_id = verify_token(admin_token)
        if admin_user_id is None:
            admin_user_id = 1  # Fallback if token verification fails

        # Create program with allow_multiple_secondary = false
        program = Program(
            title="Test Program",
            description="Test",
            relationship_config={
                "allow_multiple_secondary": False
            },
            role_definitions=[
                {"name": "Mentor", "is_primary": True},
                {"name": "Mentee", "is_primary": False}
            ],
            created_by=admin_user_id,
            updated_by=admin_user_id
        )
        db_session.add(program)
        db_session.commit()
        db_session.refresh(program)

        # Create people
        person1 = People(planning_center_id="pc_test_1", first_name="Primary", last_name="Person", email="primary@test.com")
        person2 = People(planning_center_id="pc_test_2", first_name="Secondary1", last_name="Person", email="secondary1@test.com")
        person3 = People(planning_center_id="pc_test_3", first_name="Secondary2", last_name="Person", email="secondary2@test.com")
        db_session.add_all([person1, person2, person3])
        db_session.commit()

        # Create participants
        primary = ProgramParticipant(
            program_id=program.id,
            people_id=person1.id,
            role_name="Mentor",
            status="active",
            start_date=datetime.now(timezone.utc),
            created_by=admin_user_id
        )
        secondary1 = ProgramParticipant(
            program_id=program.id,
            people_id=person2.id,
            role_name="Mentee",
            status="active",
            start_date=datetime.now(timezone.utc),
            created_by=admin_user_id
        )
        secondary2 = ProgramParticipant(
            program_id=program.id,
            people_id=person3.id,
            role_name="Mentee",
            status="active",
            start_date=datetime.now(timezone.utc),
            created_by=admin_user_id
        )
        db_session.add_all([primary, secondary1, secondary2])
        db_session.commit()

        # Create first pairing (should succeed)
        response = client.post(
            f"/api/v1/programs/{program.id}/pairings",
            json={
                "program_id": program.id,
                "primary_participant_id": primary.id,
                "secondary_participant_id": secondary1.id,
                "status": "active"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201

        # Try to create second pairing (should fail - multiple not allowed)
        response = client.post(
            f"/api/v1/programs/{program.id}/pairings",
            json={
                "program_id": program.id,
                "primary_participant_id": primary.id,
                "secondary_participant_id": secondary2.id,
                "status": "active"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 400
        assert "multiple" in response.json()["detail"].lower()
        assert "does not allow" in response.json()["detail"].lower() or "not allowed" in response.json()["detail"].lower()

    def test_get_pairing_count_for_primary(self, client, db_session, admin_token):
        """Test the pairing count endpoint"""
        # Get admin user ID from token
        from app.core.security import verify_token
        admin_user_id = verify_token(admin_token)
        if admin_user_id is None:
            admin_user_id = 1  # Fallback if token verification fails

        # Create program
        program = Program(
            title="Test Program",
            description="Test",
            relationship_config={},
            role_definitions=[
                {"name": "Mentor", "is_primary": True},
                {"name": "Mentee", "is_primary": False}
            ],
            created_by=admin_user_id,
            updated_by=admin_user_id
        )
        db_session.add(program)
        db_session.commit()
        db_session.refresh(program)

        # Create people
        person1 = People(planning_center_id="pc_test_1", first_name="Primary", last_name="Person", email="primary@test.com")
        person2 = People(planning_center_id="pc_test_2", first_name="Secondary1", last_name="Person", email="secondary1@test.com")
        person3 = People(planning_center_id="pc_test_3", first_name="Secondary2", last_name="Person", email="secondary2@test.com")
        db_session.add_all([person1, person2, person3])
        db_session.commit()

        # Create participants
        primary = ProgramParticipant(
            program_id=program.id,
            people_id=person1.id,
            role_name="Mentor",
            status="active",
            start_date=datetime.now(timezone.utc),
            created_by=admin_user_id
        )
        secondary1 = ProgramParticipant(
            program_id=program.id,
            people_id=person2.id,
            role_name="Mentee",
            status="active",
            start_date=datetime.now(timezone.utc),
            created_by=admin_user_id
        )
        secondary2 = ProgramParticipant(
            program_id=program.id,
            people_id=person3.id,
            role_name="Mentee",
            status="active",
            start_date=datetime.now(timezone.utc),
            created_by=admin_user_id
        )
        db_session.add_all([primary, secondary1, secondary2])
        db_session.commit()

        # Initially no pairings
        response = client.get(
            f"/api/v1/programs/{program.id}/pairings/count",
            params={"primary_participant_id": primary.id, "status": "active"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["count"] == 0

        # Create a pairing
        pairing1 = ProgramPairing(
            program_id=program.id,
            primary_participant_id=primary.id,
            secondary_participant_id=secondary1.id,
            status="active",
            start_date=datetime.now(timezone.utc),
            created_by=admin_user_id
        )
        db_session.add(pairing1)
        db_session.commit()

        # Count should be 1
        response = client.get(
            f"/api/v1/programs/{program.id}/pairings/count",
            params={"primary_participant_id": primary.id, "status": "active"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["count"] == 1

        # Create another pairing
        pairing2 = ProgramPairing(
            program_id=program.id,
            primary_participant_id=primary.id,
            secondary_participant_id=secondary2.id,
            status="active",
            start_date=datetime.now(timezone.utc),
            created_by=admin_user_id
        )
        db_session.add(pairing2)
        db_session.commit()

        # Count should be 2
        response = client.get(
            f"/api/v1/programs/{program.id}/pairings/count",
            params={"primary_participant_id": primary.id, "status": "active"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["count"] == 2

        # Test filtering by status - ended pairings shouldn't count
        pairing2.status = "ended"
        db_session.commit()

        response = client.get(
            f"/api/v1/programs/{program.id}/pairings/count",
            params={"primary_participant_id": primary.id, "status": "active"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert response.json()["count"] == 1

    def test_get_pairings_filtered_by_primary(self, client, db_session, admin_token):
        """Test getting pairings filtered by primary participant"""
        # Get admin user ID from token
        from app.core.security import verify_token
        admin_user_id = verify_token(admin_token)
        if admin_user_id is None:
            admin_user_id = 1  # Fallback if token verification fails

        # Create program
        program = Program(
            title="Test Program",
            description="Test",
            relationship_config={},
            role_definitions=[
                {"name": "Mentor", "is_primary": True},
                {"name": "Mentee", "is_primary": False}
            ],
            created_by=admin_user_id,
            updated_by=admin_user_id
        )
        db_session.add(program)
        db_session.commit()
        db_session.refresh(program)

        # Create people
        person1 = People(planning_center_id="pc_test_1", first_name="Primary1", last_name="Person", email="primary1@test.com")
        person2 = People(planning_center_id="pc_test_2", first_name="Primary2", last_name="Person", email="primary2@test.com")
        person3 = People(planning_center_id="pc_test_3", first_name="Secondary", last_name="Person", email="secondary@test.com")
        db_session.add_all([person1, person2, person3])
        db_session.commit()

        # Create participants
        primary1 = ProgramParticipant(
            program_id=program.id,
            people_id=person1.id,
            role_name="Mentor",
            status="active",
            start_date=datetime.now(timezone.utc),
            created_by=admin_user_id
        )
        primary2 = ProgramParticipant(
            program_id=program.id,
            people_id=person2.id,
            role_name="Mentor",
            status="active",
            start_date=datetime.now(timezone.utc),
            created_by=admin_user_id
        )
        secondary = ProgramParticipant(
            program_id=program.id,
            people_id=person3.id,
            role_name="Mentee",
            status="active",
            start_date=datetime.now(timezone.utc),
            created_by=admin_user_id
        )
        db_session.add_all([primary1, primary2, secondary])
        db_session.commit()

        # Create pairings
        pairing1 = ProgramPairing(
            program_id=program.id,
            primary_participant_id=primary1.id,
            secondary_participant_id=secondary.id,
            status="active",
            start_date=datetime.now(timezone.utc),
            created_by=admin_user_id
        )
        pairing2 = ProgramPairing(
            program_id=program.id,
            primary_participant_id=primary2.id,
            secondary_participant_id=secondary.id,
            status="active",
            start_date=datetime.now(timezone.utc),
            created_by=admin_user_id
        )
        db_session.add_all([pairing1, pairing2])
        db_session.commit()

        # Get all pairings
        response = client.get(
            f"/api/v1/programs/{program.id}/pairings",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        assert len(response.json()) == 2

        # Get pairings for primary1 only
        response = client.get(
            f"/api/v1/programs/{program.id}/pairings",
            params={"primary_participant_id": primary1.id},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["primary_participant_id"] == primary1.id

    def test_error_message_quality(self, client, db_session, admin_token):
        """Test that error messages are clear and actionable"""
        # Get admin user ID from token
        from app.core.security import verify_token
        admin_user_id = verify_token(admin_token)
        if admin_user_id is None:
            admin_user_id = 1  # Fallback if token verification fails

        # Create program with max_secondary_per_primary = 1
        program = Program(
            title="Test Program",
            description="Test",
            relationship_config={
                "allow_multiple_secondary": True,
                "max_secondary_per_primary": 1
            },
            role_definitions=[
                {"name": "Mentor", "is_primary": True},
                {"name": "Mentee", "is_primary": False}
            ],
            created_by=admin_user_id,
            updated_by=admin_user_id
        )
        db_session.add(program)
        db_session.commit()
        db_session.refresh(program)

        # Create people
        person1 = People(planning_center_id="pc_test_1", first_name="Primary", last_name="Person", email="primary@test.com")
        person2 = People(planning_center_id="pc_test_2", first_name="Secondary1", last_name="Person", email="secondary1@test.com")
        person3 = People(planning_center_id="pc_test_3", first_name="Secondary2", last_name="Person", email="secondary2@test.com")
        db_session.add_all([person1, person2, person3])
        db_session.commit()

        # Create participants
        primary = ProgramParticipant(
            program_id=program.id,
            people_id=person1.id,
            role_name="Mentor",
            status="active",
            start_date=datetime.now(timezone.utc),
            created_by=admin_user_id
        )
        secondary1 = ProgramParticipant(
            program_id=program.id,
            people_id=person2.id,
            role_name="Mentee",
            status="active",
            start_date=datetime.now(timezone.utc),
            created_by=admin_user_id
        )
        secondary2 = ProgramParticipant(
            program_id=program.id,
            people_id=person3.id,
            role_name="Mentee",
            status="active",
            start_date=datetime.now(timezone.utc),
            created_by=admin_user_id
        )
        db_session.add_all([primary, secondary1, secondary2])
        db_session.commit()

        # Create first pairing
        response = client.post(
            f"/api/v1/programs/{program.id}/pairings",
            json={
                "program_id": program.id,
                "primary_participant_id": primary.id,
                "secondary_participant_id": secondary1.id,
                "status": "active"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 201

        # Try to create second pairing - check error message
        response = client.post(
            f"/api/v1/programs/{program.id}/pairings",
            json={
                "program_id": program.id,
                "primary_participant_id": primary.id,
                "secondary_participant_id": secondary2.id,
                "status": "active"
            },
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert response.status_code == 400
        error_detail = response.json()["detail"]
        assert "maximum" in error_detail.lower()
        assert "1" in error_detail
        # Check that error message is clear and actionable (either old or new format)
        assert ("remove" in error_detail.lower() or "existing" in error_detail.lower() or 
                "maximum" in error_detail.lower() and "secondary" in error_detail.lower())

