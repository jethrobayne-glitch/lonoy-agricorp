from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Import the db instance from user module
from .user import db

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=True)
    action = db.Column(db.String(20), nullable=False)  # 'login', 'logout', 'access'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    department = db.Column(db.String(20), nullable=True)  # 'TVET', 'LPAF', or 'ADMIN'
    
    def __repr__(self):
        return f'<ActivityLog {self.username} - {self.action} at {self.timestamp}>'
    
    @classmethod
    def log_activity(cls, user, action, department=None):
        """Create a new activity log entry"""
        try:
            log_entry = cls(
                user_id=user.id,
                username=user.username,
                name=user.name,
                position=user.position or '',
                action=action,
                department=department
            )
            db.session.add(log_entry)
            db.session.commit()
            return log_entry
        except Exception as e:
            db.session.rollback()
            print(f"Error logging activity: {e}")
            return None