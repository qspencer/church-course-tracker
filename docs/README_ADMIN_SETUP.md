# Admin User Setup

This directory contains the script to create the default administrator user for the Church Course Tracker application.

## Quick Setup

To create the default admin user, run:

```bash
cd backend
source venv/bin/activate
python create_default_admin.py
```

## Default Admin Credentials

- **Username**: `Admin`
- **Email**: `course.tracker.admin@eastgate.church`
- **Password**: `Matthew778*`
- **Role**: `admin`

## What the Script Does

1. **Checks for existing admin**: The script first checks if an admin user already exists
2. **Creates admin user**: If no admin exists, it creates one with the default credentials
3. **Provides feedback**: Shows clear success/error messages with user details
4. **Safe to run multiple times**: Won't create duplicate users

## Database Requirements

The script requires:
- Database tables to be created (run migrations first)
- SQLAlchemy models to be available
- Database connection to be configured

## Troubleshooting

If you encounter issues:

1. **Database not found**: Make sure you've run the database migrations
2. **Permission errors**: Ensure the database file is writable
3. **Import errors**: Make sure you're running from the backend directory with the virtual environment activated

## Security Notes

- The default password should be changed after first login
- This script is only for initial setup - use the web interface for ongoing user management
- The admin user has full access to all system features


