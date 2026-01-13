"""
Script to create finance transactions table in the database
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web import create_app
from web.models import db


def create_finance_tables():
    # Use the SQLAlchemy models to create tables. This is portable across DB backends
    app = create_app()

    with app.app_context():
        try:
            db.create_all()
            print("✅ Finance transactions (and other models) created successfully!")
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_finance_tables()
