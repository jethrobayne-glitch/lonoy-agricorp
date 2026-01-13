"""
Script to create test users for the authentication system
"""

import sys
import os

# Add the parent directory to the path so we can import web
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web import create_app
from web.models import db, User

def create_test_users():
    app = create_app()
    
    with app.app_context():
        # Update admin user to have a name and position if it doesn't
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            updated = False
            if not admin_user.name:
                admin_user.name = 'System Administrator'
                updated = True
            if not admin_user.position:
                admin_user.position = 'System Administrator'
                updated = True
            if updated:
                db.session.commit()
                print("Updated admin user with name and/or position")
            print("Admin user exists: username='admin', password='admin', type='admin'")
        else:
            print("Admin user not found!")
        
        # Sample users to create
        test_users = [
            {'name': 'John Administrator', 'username': 'john_admin', 'password': 'password123', 'user_type': 'admin', 'position': 'IT Administrator'},
            {'name': 'Maria Garcia', 'username': 'maria_garcia', 'password': 'password123', 'user_type': 'user', 'position': 'Finance Manager'},
            {'name': 'Pedro Supervisor', 'username': 'pedro_super', 'password': 'password123', 'user_type': 'admin', 'position': 'Operations Supervisor'},
            {'name': 'Ana Reyes', 'username': 'ana_reyes', 'password': 'password123', 'user_type': 'user', 'position': 'HR Assistant'},
            {'name': 'Carlos Staff', 'username': 'carlos_staff', 'password': 'password123', 'user_type': 'user', 'position': 'General Staff'},
        ]
        
        for user_data in test_users:
            existing_user = User.query.filter_by(username=user_data['username']).first()
            if not existing_user:
                new_user = User(
                    name=user_data['name'],
                    username=user_data['username'],
                    user_type=user_data['user_type'],
                    position=user_data['position']
                )
                new_user.set_password(user_data['password'])
                db.session.add(new_user)
                print(f"Created user: {user_data['name']} ({user_data['username']}) - {user_data['position']}")
            else:
                # Update name and position if missing
                updated = False
                if not existing_user.name:
                    existing_user.name = user_data['name']
                    updated = True
                if not existing_user.position:
                    existing_user.position = user_data['position']
                    updated = True
                if updated:
                    print(f"Updated info for existing user: {user_data['username']}")
        
        db.session.commit()
        print("Test users setup completed!")

if __name__ == '__main__':
    create_test_users()