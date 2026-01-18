#!/usr/bin/env python3
"""
Script to seed test data for E2E testing
Creates courses, users, members, enrollments, and programs
"""
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Get DATABASE_URL from environment or use default (SQLite)
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./data/church_course_tracker.db')

def seed_test_data():
    """Seed test data for E2E testing"""
    try:
        # Create engine and session
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()

        print("Seeding test data for E2E testing...")
        print(f"Database: {DATABASE_URL}")
        print("=" * 60)

        # 1. Create test courses
        print("\n[1/5] Creating test courses...")
        courses = [
            {
                'title': 'Introduction to Programming',
                'description': 'Learn the basics of programming with Python',
                'duration_weeks': 8,
                'is_active': True
            },
            {
                'title': 'Web Development Fundamentals',
                'description': 'Master HTML, CSS, and JavaScript',
                'duration_weeks': 10,
                'is_active': True
            },
            {
                'title': 'Database Design',
                'description': 'Learn database design principles and SQL',
                'duration_weeks': 6,
                'is_active': True
            },
            {
                'title': 'Advanced JavaScript',
                'description': 'Deep dive into JavaScript and modern frameworks',
                'duration_weeks': 12,
                'is_active': True
            },
            {
                'title': 'Project Management',
                'description': 'Learn to manage software projects effectively',
                'duration_weeks': 4,
                'is_active': True
            }
        ]

        course_ids = []
        for course in courses:
            # Check if course already exists
            existing = db.execute(
                text("SELECT id FROM courses WHERE title = :title"),
                {"title": course['title']}
            ).fetchone()

            if existing:
                course_ids.append(existing[0])
                print(f"   - Course '{course['title']}' already exists (ID: {existing[0]})")
            else:
                result = db.execute(
                    text("""
                        INSERT INTO courses (title, description, duration_weeks, is_active, current_registrations, created_at, updated_at)
                        VALUES (:title, :description, :duration_weeks, :is_active, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """),
                    course
                )
                db.commit()

                new_course = db.execute(
                    text("SELECT id FROM courses WHERE title = :title"),
                    {"title": course['title']}
                ).fetchone()
                course_ids.append(new_course[0])
                print(f"   ✅ Created course '{course['title']}' (ID: {new_course[0]})")

        # 2. Create test members/people
        print("\n[2/5] Creating test members...")
        members = [
            {
                'planning_center_id': 'test_pc_10001',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@example.com',
                'phone': '555-0101'
            },
            {
                'planning_center_id': 'test_pc_10002',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'jane.smith@example.com',
                'phone': '555-0102'
            },
            {
                'planning_center_id': 'test_pc_10003',
                'first_name': 'Bob',
                'last_name': 'Johnson',
                'email': 'bob.johnson@example.com',
                'phone': '555-0103'
            },
            {
                'planning_center_id': 'test_pc_10004',
                'first_name': 'Alice',
                'last_name': 'Williams',
                'email': 'alice.williams@example.com',
                'phone': '555-0104'
            },
            {
                'planning_center_id': 'test_pc_10005',
                'first_name': 'Charlie',
                'last_name': 'Brown',
                'email': 'charlie.brown@example.com',
                'phone': '555-0105'
            },
            {
                'planning_center_id': 'test_pc_10006',
                'first_name': 'Diana',
                'last_name': 'Davis',
                'email': 'diana.davis@example.com',
                'phone': '555-0106'
            },
            {
                'planning_center_id': 'test_pc_10007',
                'first_name': 'Eve',
                'last_name': 'Miller',
                'email': 'eve.miller@example.com',
                'phone': '555-0107'
            },
            {
                'planning_center_id': 'test_pc_10008',
                'first_name': 'Frank',
                'last_name': 'Wilson',
                'email': 'frank.wilson@example.com',
                'phone': '555-0108'
            },
            {
                'planning_center_id': 'test_pc_10009',
                'first_name': 'Grace',
                'last_name': 'Moore',
                'email': 'grace.moore@example.com',
                'phone': '555-0109'
            },
            {
                'planning_center_id': 'test_pc_10010',
                'first_name': 'Henry',
                'last_name': 'Taylor',
                'email': 'henry.taylor@example.com',
                'phone': '555-0110'
            }
        ]

        member_ids = []
        for member in members:
            # Check if member already exists
            existing = db.execute(
                text("SELECT id FROM people WHERE email = :email"),
                {"email": member['email']}
            ).fetchone()

            if existing:
                member_ids.append(existing[0])
                print(f"   - Member '{member['first_name']} {member['last_name']}' already exists")
            else:
                db.execute(
                    text("""
                        INSERT INTO people (planning_center_id, first_name, last_name, email, phone, is_active, created_at, updated_at)
                        VALUES (:planning_center_id, :first_name, :last_name, :email, :phone, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """),
                    member
                )
                db.commit()

                new_member = db.execute(
                    text("SELECT id FROM people WHERE email = :email"),
                    {"email": member['email']}
                ).fetchone()
                member_ids.append(new_member[0])
                print(f"   ✅ Created member '{member['first_name']} {member['last_name']}' (ID: {new_member[0]})")

        # 3. Create test programs
        print("\n[3/4] Creating test programs...")
        programs = [
            {
                'title': 'Life on Life Discipleship',
                'description': 'Mentorship program for spiritual growth',
                'is_active': True,
                'role_definitions': '[{"name": "Mentor", "min_participants": 0, "max_participants": 100, "is_primary": true}, {"name": "Mentee", "min_participants": 0, "max_participants": 100, "is_primary": false}]'
            },
            {
                'title': 'Small Group Leadership',
                'description': 'Training program for small group leaders',
                'is_active': True,
                'role_definitions': '[{"name": "Leader", "min_participants": 0, "max_participants": 50, "is_primary": true}, {"name": "Participant", "min_participants": 0, "max_participants": 200, "is_primary": false}]'
            },
            {
                'title': 'Youth Ministry',
                'description': 'Youth development and discipleship program',
                'is_active': True,
                'role_definitions': '[{"name": "Leader", "min_participants": 0, "max_participants": 20, "is_primary": true}, {"name": "Student", "min_participants": 0, "max_participants": 100, "is_primary": false}]'
            }
        ]

        program_ids = []
        for program in programs:
            # Check if program already exists
            existing = db.execute(
                text("SELECT id FROM programs WHERE title = :title"),
                {"title": program['title']}
            ).fetchone()

            if existing:
                program_ids.append(existing[0])
                print(f"   - Program '{program['title']}' already exists (ID: {existing[0]})")
            else:
                db.execute(
                    text("""
                        INSERT INTO programs (title, description, is_active, role_definitions, created_at, updated_at)
                        VALUES (:title, :description, :is_active, :role_definitions, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """),
                    program
                )
                db.commit()

                new_program = db.execute(
                    text("SELECT id FROM programs WHERE title = :title"),
                    {"title": program['title']}
                ).fetchone()
                program_ids.append(new_program[0])
                print(f"   ✅ Created program '{program['title']}' (ID: {new_program[0]})")

        # 4. Create program participants
        print("\n[4/4] Creating program participants...")
        participant_count = 0
        for i, program_id in enumerate(program_ids):
            # Add mentors/leaders (first 2 members)
            for member_id in member_ids[:2]:
                existing = db.execute(
                    text("SELECT id FROM program_participants WHERE program_id = :program_id AND people_id = :people_id"),
                    {"program_id": program_id, "people_id": member_id}
                ).fetchone()

                if not existing:
                    role = "Mentor" if i == 0 else "Leader"
                    db.execute(
                        text("""
                            INSERT INTO program_participants (
                                program_id, people_id, role_name, status, start_date, progress_percentage, created_at, updated_at
                            )
                            VALUES (
                                :program_id, :people_id, :role_name, :status, :start_date, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                            )
                        """),
                        {
                            "program_id": program_id,
                            "people_id": member_id,
                            "role_name": role,
                            "status": "active",
                            "start_date": (datetime.now() - timedelta(days=90)).isoformat()
                        }
                    )
                    participant_count += 1

            # Add mentees/participants (next 4 members)
            for member_id in member_ids[2:6]:
                existing = db.execute(
                    text("SELECT id FROM program_participants WHERE program_id = :program_id AND people_id = :people_id"),
                    {"program_id": program_id, "people_id": member_id}
                ).fetchone()

                if not existing:
                    role = "Mentee" if i == 0 else "Participant" if i == 1 else "Student"
                    db.execute(
                        text("""
                            INSERT INTO program_participants (
                                program_id, people_id, role_name, status, start_date, progress_percentage, created_at, updated_at
                            )
                            VALUES (
                                :program_id, :people_id, :role_name, :status, :start_date, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                            )
                        """),
                        {
                            "program_id": program_id,
                            "people_id": member_id,
                            "role_name": role,
                            "status": "active",
                            "start_date": (datetime.now() - timedelta(days=60)).isoformat()
                        }
                    )
                    participant_count += 1

        db.commit()
        print(f"   ✅ Created {participant_count} program participants")

        # Summary
        print("\n" + "=" * 60)
        print("Test data seeding complete!")
        print("\nSeeded Data Summary:")
        print("-" * 60)
        print(f"Courses: {len(course_ids)}")
        print(f"Members: {len(member_ids)}")
        print(f"Programs: {len(program_ids)}")
        print(f"Program Participants: {participant_count}")
        print("-" * 60)
        print("\nYou can now run E2E tests with this test data!")

        db.close()
        return True

    except Exception as e:
        print(f"\n❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = seed_test_data()
    sys.exit(0 if success else 1)
