from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default='')
    position = db.Column(db.String(100), nullable=True, default='')
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'admin' or 'user'
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def can_access_role(self, role):
        """Check if user can access a specific role"""
        if self.user_type == 'admin':
            return role in ['tvet', 'lpaf', 'admin']
        elif self.user_type == 'user':
            return role in ['tvet', 'lpaf']
        return False
    
    def get_id(self):
        """Return the user ID as required by Flask-Login"""
        return str(self.id)
    
    def is_authenticated(self):
        """Return True if the user is authenticated"""
        return True
    
    def is_active(self):
        """Return True if the user is active"""
        return True
    
    def is_anonymous(self):
        """Return False as this is not an anonymous user"""
        return False
    
    def __repr__(self):
        return f'<User {self.username}>'