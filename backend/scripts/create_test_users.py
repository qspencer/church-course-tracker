#!/usr/bin/env python3
"""
Script to create test users for E2E testing
Creates staff and viewer users with credentials expected by E2E tests
Works with both SQLite (local) and PostgreSQL (production)
"""
import os
import sys

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.security import get_password_hash

# Get DATABASE_URL from environment or use default (SQLite)
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./data/church_course_tracker.db')

# Test users configuration (matching E2E test expectations)
TEST_USERS = [
    {
        'username': 'staff',
        'password': 'staff123',
        'email': 'test.staff@eastgate.church',
        'full_name': 'Test Staff User',
        'role': 'staff'
    },
    {
        'username': 'viewer',
        'password': 'viewer123',
        'email': 'test.viewer@eastgate.church',
        'full_name': 'Test Viewer User',
        'role': 'viewer'
    }
]

def create_test_users():
    """Create test users using SQLAlchemy"""
    try:
        # Create engine and session
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()

        print("Creating test users for E2E testing...")
        print(f"Database: {DATABASE_URL}")
        print("=" * 60)

        for user_data in TEST_USERS:
            try:
                # Check if user already exists
                result = db.execute(
                    text("SELECT id, username, role FROM users WHERE username = :username OR email = :email"),
                    {"username": user_data['username'], "email": user_data['email']}
                ).fetchone()

                # Hash the password
                hashed_password = get_password_hash(user_data['password'])

                if result:
                    user_id = result[0]
                    print(f"\n⚠️  User '{user_data['username']}' already exists (ID: {user_id})")
                    print(f"   Updating password and role...")

                    # Update existing user
                    db.execute(
                        text("""
                            UPDATE users
                            SET hashed_password = :hashed_password,
                                role = :role,
                                is_active = :is_active,
                                full_name = :full_name,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE username = :username OR email = :email
                        """),
                        {
                            "hashed_password": hashed_password,
                            "role": user_data['role'],
                            "is_active": True,
                            "full_name": user_data['full_name'],
                            "username": user_data['username'],
                            "email": user_data['email']
                        }
                    )

                    db.commit()
                    print(f"   ✅ Updated user '{user_data['username']}' with role '{user_data['role']}'")
                else:
                    # Create new user
                    db.execute(
                        text("""
                            INSERT INTO users (
                                email,
                                username,
                                full_name,
                                hashed_password,
                                role,
                                is_active,
                                created_at,
                                updated_at
                            )
                            VALUES (
                                :email,
                                :username,
                                :full_name,
                                :hashed_password,
                                :role,
                                :is_active,
                                CURRENT_TIMESTAMP,
                                CURRENT_TIMESTAMP
                            )
                        """),
                        {
                            "email": user_data['email'],
                            "username": user_data['username'],
                            "full_name": user_data['full_name'],
                            "hashed_password": hashed_password,
                            "role": user_data['role'],
                            "is_active": True
                        }
                    )

                    db.commit()

                    # Get the new user ID
                    new_user = db.execute(
                        text("SELECT id FROM users WHERE username = :username"),
                        {"username": user_data['username']}
                    ).fetchone()

                    print(f"\n✅ Created new user '{user_data['username']}' (ID: {new_user[0]})")
                    print(f"   Role: {user_data['role']}")
                    print(f"   Email: {user_data['email']}")
                    print(f"   Password: {user_data['password']}")

            except Exception as e:
                print(f"\n❌ Error processing user '{user_data['username']}': {e}")
                db.rollback()
                import traceback
                traceback.print_exc()
                continue

        print("\n" + "=" * 60)
        print("Test user creation complete!")
        print("\nE2E Test Credentials:")
        print("-" * 60)
        print("Admin:  username='Admin',  password='Matthew778*' (already exists)")
        print("Staff:  username='staff',  password='staff123'")
        print("Viewer: username='viewer', password='viewer123'")
        print("-" * 60)
        print("\nYou can now run E2E tests with these credentials!")

        db.close()
        return True

    except Exception as e:
        print(f"\n❌ Database connection error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_test_users()
    sys.exit(0 if success else 1)
