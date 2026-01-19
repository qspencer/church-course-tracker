"""Add default users for each role (staff, instructor, viewer)

Revision ID: z8a9b0c1d2e3
Revises: y7z8a9b0c1d2
Create Date: 2026-01-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from datetime import datetime, timezone

# revision identifiers, used by Alembic.
revision = 'z8a9b0c1d2e3'
down_revision = 'y7z8a9b0c1d2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Ensure default users exist for each role (staff, instructor, viewer).
    This is idempotent - it will only create users that don't exist.
    Uses environment variables for configuration with sensible defaults.
    """
    connection = op.get_bind()

    import os

    # Define default users (excluding admin which already exists)
    default_users = [
        {
            "username": os.getenv("STAFF_USERNAME", "Staff"),
            "email": os.getenv("STAFF_EMAIL", "staff@example.com"),
            "password": os.getenv("STAFF_PASSWORD", "Staff123!"),
            "full_name": os.getenv("STAFF_FULL_NAME", "Default Staff"),
            "role": "staff"
        },
        {
            "username": os.getenv("INSTRUCTOR_USERNAME", "Instructor"),
            "email": os.getenv("INSTRUCTOR_EMAIL", "instructor@example.com"),
            "password": os.getenv("INSTRUCTOR_PASSWORD", "Instructor123!"),
            "full_name": os.getenv("INSTRUCTOR_FULL_NAME", "Default Instructor"),
            "role": "instructor"
        },
        {
            "username": os.getenv("VIEWER_USERNAME", "Viewer"),
            "email": os.getenv("VIEWER_EMAIL", "viewer@example.com"),
            "password": os.getenv("VIEWER_PASSWORD", "Viewer123!"),
            "full_name": os.getenv("VIEWER_FULL_NAME", "Default Viewer"),
            "role": "viewer"
        }
    ]

    # Use bcrypt directly for password hashing (avoids passlib compatibility issues)
    import bcrypt
    def hash_password(password):
        return bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt(rounds=12)
        ).decode('utf-8')

    # Get current timestamp
    now = datetime.now(timezone.utc).isoformat()

    for user_data in default_users:
        # Check if user already exists
        result = connection.execute(
            text("SELECT COUNT(*) FROM users WHERE username = :username OR email = :email"),
            {"username": user_data["username"], "email": user_data["email"]}
        )
        count = result.scalar()

        if count == 0:
            # Hash the password
            hashed_password = hash_password(user_data["password"])

            # Insert user
            connection.execute(
                text("""
                    INSERT INTO users (
                        username, email, full_name, hashed_password, role, is_active,
                        created_at, updated_at
                    ) VALUES (
                        :username, :email, :full_name, :hashed_password,
                        :role, 1, :created_at, :updated_at
                    )
                """),
                {
                    "username": user_data["username"],
                    "email": user_data["email"],
                    "full_name": user_data["full_name"],
                    "hashed_password": hashed_password,
                    "role": user_data["role"],
                    "created_at": now,
                    "updated_at": now
                }
            )
            connection.commit()
            print(f"✅ Created {user_data['role']} user ({user_data['username']})")
        else:
            print(f"ℹ️  {user_data['role'].capitalize()} user already exists (username: {user_data['username']}), skipping creation")


def downgrade() -> None:
    """
    Remove the default role users if they exist.
    WARNING: This will delete these users!
    """
    connection = op.get_bind()

    # Remove default users (but not admin)
    users_to_remove = [
        ("Staff", "staff@example.com"),
        ("Instructor", "instructor@example.com"),
        ("Viewer", "viewer@example.com")
    ]

    for username, email in users_to_remove:
        connection.execute(
            text("DELETE FROM users WHERE username = :username OR email = :email"),
            {"username": username, "email": email}
        )

    connection.commit()
    print("⚠️  Removed default role users (staff, instructor, viewer)")
