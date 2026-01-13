"""
Add units and receipt columns to finance_transactions table
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'app.db')

def migrate():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if units column exists
        cursor.execute("PRAGMA table_info(finance_transactions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'units' not in columns:
            print("Adding units column...")
            cursor.execute("ALTER TABLE finance_transactions ADD COLUMN units INTEGER NOT NULL DEFAULT 1")
            print("Units column added successfully")
        else:
            print("Units column already exists")
        
        if 'receipt' not in columns:
            print("Adding receipt column...")
            cursor.execute("ALTER TABLE finance_transactions ADD COLUMN receipt TEXT")
            print("Receipt column added successfully")
        else:
            print("Receipt column already exists")
        
        conn.commit()
        print("\nMigration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\nError during migration: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    migrate()
