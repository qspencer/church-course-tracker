"""Ensure admin user exists

Revision ID: v2w3x4y5z6a7
Revises: u1v2w3x4y5z6
Create Date: 2025-11-23 03:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'v2w3x4y5z6a7'
down_revision = 'u1v2w3x4y5z6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Ensure admin user exists in the database.
    This is idempotent - it will only create the user if it doesn't exist.
    Uses environment variables for configuration (defaults to Admin/Matthew778*).
    """
    connection = op.get_bind()
    
    # Get admin credentials from environment variables (with defaults)
    import os
    admin_username = os.getenv("ADMIN_USERNAME", "Admin")
    admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    admin_password = os.getenv("ADMIN_PASSWORD", "Matthew778*")
    admin_full_name = os.getenv("ADMIN_FULL_NAME", "System Admin")
    
    # Check if admin user already exists
    result = connection.execute(
        text("SELECT COUNT(*) FROM users WHERE username = :username OR email = :email"),
        {"username": admin_username, "email": admin_email}
    )
    count = result.scalar()
    
    if count == 0:
        # Import password hashing - add backend to path first
        import sys
        backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'backend')
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        
        try:
            from app.core.security import get_password_hash
            
            # Hash the password
            hashed_password = get_password_hash(admin_password)
        except ImportError:
            # Fallback: use bcrypt directly if import fails
            import bcrypt
            hashed_password = bcrypt.hashpw(
                admin_password.encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8')
        
        # Get current timestamp
        now = datetime.utcnow().isoformat()
        
        # Insert admin user
        # Note: We use raw SQL to avoid model dependencies in migrations
        connection.execute(
            text("""
                INSERT INTO users (
                    username, email, full_name, hashed_password, role, is_active, 
                    created_at, updated_at
                ) VALUES (
                    :username, :email, :full_name, :hashed_password, 
                    'admin', 1, :created_at, :updated_at
                )
            """),
            {
                "username": admin_username,
                "email": admin_email,
                "full_name": admin_full_name,
                "hashed_password": hashed_password,
                "created_at": now,
                "updated_at": now
            }
        )
        connection.commit()
        print(f"✅ Created admin user ({admin_username})")
    else:
        print(f"ℹ️  Admin user already exists (username: {admin_username}), skipping creation")


def downgrade() -> None:
    """
    Remove admin user if it exists.
    WARNING: This will delete the admin user!
    """
    connection = op.get_bind()
    
    # Delete admin user
    connection.execute(
        text("DELETE FROM users WHERE username = 'Admin' OR email = 'admin@example.com'")
    )
    connection.commit()
    print("⚠️  Removed admin user")

