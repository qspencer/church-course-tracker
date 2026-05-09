#!/usr/bin/env python3
"""
Create the default administrator user for the Church Course Tracker.

Reads credentials from environment variables (no hardcoded defaults):
  - ADMIN_USERNAME       (default: "Admin")
  - ADMIN_EMAIL          (default: "course.tracker.admin@eastgate.church")
  - ADMIN_PASSWORD       (REQUIRED — script exits non-zero if unset)
  - ADMIN_FULL_NAME      (default: "System Administrator")

Idempotent: skips creation if a user with the username or email already exists.
"""

import os
import sys
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
backend_dir = os.path.join(project_root, "backend")
sys.path.insert(0, backend_dir)

from app.core.database import SessionLocal  # noqa: E402
from app.models.user import User  # noqa: E402
from passlib.context import CryptContext  # noqa: E402

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_default_admin() -> bool:
    """Create the default administrator user.

    Returns True if the user was created or already existed; False on error.
    """
    admin_username = os.getenv("ADMIN_USERNAME", "Admin")
    admin_email = os.getenv("ADMIN_EMAIL", "course.tracker.admin@eastgate.church")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin_full_name = os.getenv("ADMIN_FULL_NAME", "System Administrator")

    if not admin_password:
        print(
            "❌ ADMIN_PASSWORD env var is required. Set it before running this script:\n"
            "     export ADMIN_PASSWORD='your-strong-password'\n"
            "   (No default is provided — a leaked literal lived in this file before May 2026.)",
            file=sys.stderr,
        )
        return False

    db = SessionLocal()
    try:
        existing = (
            db.query(User)
            .filter((User.username == admin_username) | (User.email == admin_email))
            .first()
        )
        if existing:
            print(f"✅ Admin user already exists (username: {existing.username})")
            return True

        admin_user = User(
            username=admin_username,
            email=admin_email,
            full_name=admin_full_name,
            hashed_password=pwd_context.hash(admin_password),
            role="admin",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        # Note: we deliberately do NOT print the password back.
        print("✅ Default administrator user created successfully!")
        print(f"   Username: {admin_user.username}")
        print(f"   Email:    {admin_user.email}")
        print(f"   Role:     {admin_user.role}")
        return True

    except Exception as e:
        print(f"❌ Error creating admin user: {e}", file=sys.stderr)
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("🏗️  Church Course Tracker - Admin User Setup")
    print("=" * 50)

    if not create_default_admin():
        sys.exit(1)
