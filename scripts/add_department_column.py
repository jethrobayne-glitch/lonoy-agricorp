#!/usr/bin/env python3
"""
Script to add department column to the employees table.
Run this from the project root directory.
"""

import sys
import os
import sqlite3

def add_department_column():
    db_path = "instance/app.db"
    
    if not os.path.exists(db_path):
        print("Database file not found!")
        return
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if department column already exists
        cursor.execute("PRAGMA table_info(employees)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'department' in columns:
            print("Department column already exists!")
            
            # Update existing employees to TVET department if they don't have one
            cursor.execute("UPDATE employees SET department = 'TVET' WHERE department IS NULL OR department = ''")
            conn.commit()
            print("Updated existing employees to TVET department.")
            
        else:
            # Add department column
            cursor.execute("ALTER TABLE employees ADD COLUMN department VARCHAR(10) DEFAULT 'TVET'")
            print("Department column added successfully!")
            
            # Update all existing employees to TVET
            cursor.execute("UPDATE employees SET department = 'TVET'")
            conn.commit()
            print("Set all existing employees to TVET department.")
        
        conn.close()
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == '__main__':
    add_department_column()