#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web import create_app, db

app = create_app()

with app.app_context():
    try:
        print("Creating certificates table...")
        
        # Create all tables including certificates
        db.create_all()
        print("✓ Created certificates table")
        
        # Ensure uploads directory exists
        os.makedirs("web/static/uploads/certificates", exist_ok=True)
        print("✓ Created uploads directory")
        
        print("\nDatabase setup completed successfully!")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error during setup: {e}")
        import traceback
        traceback.print_exc()