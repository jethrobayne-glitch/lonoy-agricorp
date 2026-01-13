"""
Database migration script to add activity_logs table
Run this script to create the activity_logs table for tracking user login/logout activities
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from web import create_app
from web.models import db, ActivityLog

def create_activity_logs_table():
    """Create the activity_logs table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create the activity_logs table
            db.create_all()
            print("✓ Activity logs table created successfully!")
            
        except Exception as e:
            print(f"✗ Error creating activity_logs table: {e}")
            return False
    
    return True

if __name__ == '__main__':
    print("Creating activity_logs table...")
    success = create_activity_logs_table()
    
    if success:
        print("\nMigration completed successfully!")
        print("The admin can now view user login/logout activities in the logs section.")
    else:
        print("\nMigration failed. Please check the error messages above.")