import sys
import os
import logging
from datetime import datetime

# Robust path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
# Go up one level from scripts/ to root, then into backend
backend_dir = os.path.join(os.path.dirname(current_dir), 'backend')
sys.path.append(backend_dir)

print(f"DEBUG: Added {backend_dir} to sys.path")
print(f"DEBUG: sys.path: {sys.path}")

try:
    from app.core.database import SessionLocal
    from app.models.user import User
    from app.core.security import verify_password, get_password_hash
    from app.services.failed_login_service import FailedLoginService
except ImportError as e:
    print(f"CRITICAL IMPORT ERROR: {e}")
    # Try to look into backend directory content
    print(f"Contents of {backend_dir}:")
    try:
        print(os.listdir(backend_dir))
        print(f"Contents of {os.path.join(backend_dir, 'app')}:")
        print(os.listdir(os.path.join(backend_dir, 'app')))
    except Exception as sub_e:
        print(f"Cannot list dir: {sub_e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def diagnose_login(username, password):
    db = SessionLocal()
    try:
        print(f"--- Diagnosing Login for '{username}' ---")
        
        # 1. Check if user exists
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"❌ User '{username}' NOT FOUND.")
            # Check if it exists with different case
            users = db.query(User).all()
            print("Existing users:")
            for u in users:
                print(f"  - {u.username} (Email: {u.email}, Role: {u.role})")
            
            # Create Admin user
            print(f"⚠️ Creating user '{username}' with password '{password}'...")
            new_user = User(
                username=username,
                email="admin@example.com",
                full_name="System Admin",
                hashed_password=get_password_hash(password),
                is_active=True,
                role="admin",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(new_user)
            db.commit()
            print(f"✅ Created user '{username}'. Try logging in now.")
            return

        print(f"✅ User found: ID={user.id}, Email={user.email}, Role={user.role}")
        
        # 2. Check active status
        if not user.is_active:
            print("❌ User is INACTIVE.")
        else:
            print("✅ User is ACTIVE.")

        # 3. Check Account Lockout
        failed_login_service = FailedLoginService(db)
        is_locked, lockout_end = failed_login_service.is_account_locked(username)
        if is_locked:
            print(f"❌ Account is LOCKED until {lockout_end}.")
            # Offer to unlock
            # failed_login_service.reset_failed_attempts(username)
            # print("  (Unlock not auto-performed in diagnosis, but could be)")
        else:
            print("✅ Account is NOT locked.")

        # 4. Check Password Verification
        print(f"Current Hash: {user.hashed_password}")
        is_valid = verify_password(password, user.hashed_password)
        if is_valid:
            print("✅ Password verification SUCCEEDED.")
        else:
            print("❌ Password verification FAILED.")
            
            # Debug: try to hash the provided password and compare (visually)
            new_hash = get_password_hash(password)
            print(f"New hash of provided password: {new_hash}")
            
            # Debug: Check bcrypt version compatibility?
            import bcrypt
            print(f"Bcrypt version: {bcrypt.__version__}")
            
            try:
                # Try direct bcrypt check if verify_password logic is complex
                if user.hashed_password.startswith(('$2b$', '$2a$', '$2y$')):
                    matches = bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8'))
                    print(f"Direct bcrypt.checkpw result: {matches}")
            except Exception as e:
                print(f"Direct bcrypt check error: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    diagnose_login("Admin", "<REDACTED>")
