#!/usr/bin/env python3
"""
Lambda function to activate Admin user
Can be deployed and invoked to activate the user
"""
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine, text

def lambda_handler(event, context):
    """Lambda handler to activate Admin user"""
    db_url = os.getenv('DATABASE_URL', 
        "postgresql://postgres:church_course_tracker_password@church-course-tracker-db.cmn082g02d5u.us-east-1.rds.amazonaws.com:5432/church_course_tracker")
    
    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            result = conn.execute(
                text("UPDATE users SET is_active = true WHERE username = 'Admin' RETURNING id, username, is_active;")
            )
            row = result.fetchone()
            conn.commit()
            
            if row:
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'message': 'Admin user activated',
                        'id': row[0],
                        'username': row[1],
                        'is_active': row[2]
                    })
                }
            else:
                return {
                    'statusCode': 404,
                    'body': json.dumps({'message': 'Admin user not found'})
                }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

if __name__ == "__main__":
    # Test locally
    result = lambda_handler({}, None)
    print(json.dumps(result, indent=2))
