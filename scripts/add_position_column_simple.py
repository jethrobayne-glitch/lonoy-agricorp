#!/usr/bin/env python3
"""
Script to add position column to users table
"""

import sqlite3
import os

def add_position_column():
    """Add position column to users table using direct SQLite connection"""
    
    # Find the database file
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance', 'app.db')
    
    if not os.path.exists(db_path):
        print(f"Database file not found at: {db_path}")
        return
    
    try:
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'position' not in columns:
            # Add the position column
            cursor.execute('ALTER TABLE users ADD COLUMN position TEXT DEFAULT ""')
            conn.commit()
            print("Position column added successfully!")
        else:
            print("Position column already exists!")
            
        conn.close()
                
    except Exception as e:
        print(f"Error adding position column: {e}")

if __name__ == "__main__":
    add_position_column()