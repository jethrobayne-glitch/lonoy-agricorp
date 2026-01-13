"""
Migration script to create study folders and videos tables
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from web import create_app
from web.models import db

def create_study_tables():
    """Create study folders and videos tables"""
    app = create_app()
    
    with app.app_context():
        # Drop existing tables if they exist (to handle incomplete tables)
        try:
            db.session.execute(db.text('DROP TABLE IF EXISTS study_videos'))
            db.session.execute(db.text('DROP TABLE IF EXISTS study_folders'))
            db.session.commit()
            print("✓ Dropped existing study tables (if any)")
        except Exception as e:
            print(f"  Note: {e}")
            db.session.rollback()
        
        # Create tables with proper schema
        db.session.execute(db.text('''
            CREATE TABLE IF NOT EXISTS study_folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                parent_folder_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_folder_id) REFERENCES study_folders(id)
            )
        '''))
        
        db.session.execute(db.text('''
            CREATE TABLE IF NOT EXISTS study_videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                filename VARCHAR(255) NOT NULL,
                original_name VARCHAR(255) NOT NULL,
                file_path VARCHAR(500) NOT NULL,
                file_size INTEGER,
                duration VARCHAR(50),
                mime_type VARCHAR(100),
                thumbnail_path VARCHAR(500),
                folder_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (folder_id) REFERENCES study_folders(id)
            )
        '''))
        
        db.session.commit()
        
        print("✓ Study tables created successfully!")
        print("  - study_folders table created")
        print("  - study_videos table created")

if __name__ == '__main__':
    create_study_tables()
