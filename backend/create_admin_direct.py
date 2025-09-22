#!/usr/bin/env python3
"""
Script to create the default administrator user directly in H2 database
"""

import jaydebeapi
import os
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_default_admin():
    """Create the default administrator user"""
    
    # H2 database configuration
    h2_jar_path = '/home/qspencer/Dev/church-course-tracker/backend/lib/h2-2.2.224.jar'
    h2_database_path = '/home/qspencer/Dev/church-course-tracker/backend/data/church_course_tracker'
    
    # Create H2 JDBC URL
    h2_url = f'jdbc:h2:file:{h2_database_path};DB_CLOSE_DELAY=-1;DB_CLOSE_ON_EXIT=FALSE'
    
    try:
        # Test connection
        conn = jaydebeapi.connect(
            'org.h2.Driver',
            h2_url,
            ['', ''],  # username, password
            h2_jar_path
        )
        print('✅ H2 database connection successful!')
        
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'USERS'")
        result = cursor.fetchone()
        print(f'Users table exists: {result[0] > 0}')
        
        if result[0] > 0:
            # Check if admin user exists
            cursor.execute("SELECT COUNT(*) FROM USERS WHERE USERNAME = 'Admin' OR EMAIL = 'admin@church.com'")
            admin_count = cursor.fetchone()[0]
            print(f'Admin user exists: {admin_count > 0}')
            
            if admin_count == 0:
                print('Creating admin user...')
                # Hash the password
                hashed_password = pwd_context.hash('Matthew778*')
                
                # Insert admin user
                cursor.execute('''
                    INSERT INTO USERS (USERNAME, EMAIL, FULL_NAME, HASHED_PASSWORD, ROLE, IS_ACTIVE, CREATED_AT, UPDATED_AT)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                ''', ('Admin', 'admin@church.com', 'System Administrator', hashed_password, 'admin', True))
                
                conn.commit()
                print('✅ Default administrator user created successfully!')
                print('   Username: Admin')
                print('   Email: admin@church.com')
                print('   Password: Matthew778*')
                print('   Role: admin')
            else:
                print('✅ Admin user already exists!')
        else:
            print('❌ Users table does not exist. Please run database migrations first.')
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == "__main__":
    print("Creating default administrator user...")
    create_default_admin()
    print("Done!")
