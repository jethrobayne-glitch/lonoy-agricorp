#!/usr/bin/env python3
"""
Script to create the students table in the database.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web import create_app
from web.models import db, Student

def create_students_table():
    """Create the students table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create the students table
            db.create_all()
            
            # Check if table was created successfully
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'students' in tables:
                print("✓ Students table created successfully!")
                
                # Get table columns
                columns = inspector.get_columns('students')
                print("  Columns:")
                for column in columns:
                    print(f"    - {column['name']}: {column['type']}")
                    
                print("\nThe students table is now ready to use!")
            else:
                print("✗ Failed to create students table")
                return False
                
        except Exception as e:
            print(f"✗ Error creating students table: {e}")
            return False
    
    return True

if __name__ == '__main__':
    print("Creating students table...")
    success = create_students_table()
    if not success:
        sys.exit(1)
    print("Done!")