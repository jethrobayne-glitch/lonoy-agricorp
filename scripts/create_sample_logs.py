"""
Test script to generate sample activity logs
This will help verify that the login/logout tracking is working properly
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

from web import create_app
from web.models import db, User, ActivityLog
from datetime import datetime, timedelta

def create_sample_logs():
    """Create some sample activity logs for testing"""
    app = create_app()
    
    with app.app_context():
        try:
            # Get existing users
            admin_user = User.query.filter_by(username='admin').first()
            
            if admin_user:
                # Create some sample activity logs
                now = datetime.utcnow()
                
                # Sample login activities
                ActivityLog.log_activity(admin_user, 'login')
                
                # Add a small delay and log department access
                log1 = ActivityLog(
                    user_id=admin_user.id,
                    username=admin_user.username,
                    name=admin_user.name,
                    position=admin_user.position or 'System Administrator',
                    action='access',
                    department='ADMIN',
                    timestamp=now - timedelta(minutes=5)
                )
                db.session.add(log1)
                
                # Sample logout
                log2 = ActivityLog(
                    user_id=admin_user.id,
                    username=admin_user.username,
                    name=admin_user.name,
                    position=admin_user.position or 'System Administrator',
                    action='logout',
                    department='ADMIN',
                    timestamp=now - timedelta(minutes=2)
                )
                db.session.add(log2)
                
                # Another login session
                log3 = ActivityLog(
                    user_id=admin_user.id,
                    username=admin_user.username,
                    name=admin_user.name,
                    position=admin_user.position or 'System Administrator',
                    action='login',
                    timestamp=now
                )
                db.session.add(log3)
                
                db.session.commit()
                
                print("✓ Sample activity logs created successfully!")
                
                # Display current logs
                logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(10).all()
                print(f"\nCurrent activity logs ({len(logs)} entries):")
                print("-" * 80)
                for log in logs:
                    print(f"{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | {log.name} | {log.action.upper()} | {log.department or 'N/A'}")
                
            else:
                print("✗ Admin user not found. Please ensure the application has been initialized.")
                return False
                
        except Exception as e:
            print(f"✗ Error creating sample logs: {e}")
            db.session.rollback()
            return False
    
    return True

if __name__ == '__main__':
    print("Creating sample activity logs...")
    success = create_sample_logs()
    
    if success:
        print("\nSample data created successfully!")
        print("You can now view the activity logs in the admin panel at: http://127.0.0.1:5000/admin/logs")
    else:
        print("\nFailed to create sample data. Please check the error messages above.")