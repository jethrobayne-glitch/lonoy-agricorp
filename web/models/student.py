from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Import the db instance from user.py
from .user import db

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    batch = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    address = db.Column(db.Text, nullable=False)
    contact_no = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with certificates
    certificates = db.relationship('Certificate', back_populates='student', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert student object to dictionary"""
        return {
            'id': self.id,
            'batch': self.batch,
            'name': self.name,
            'age': self.age,
            'address': self.address,
            'contact_no': self.contact_no,
            'certificates_count': len(self.certificates) if self.certificates else 0,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def __repr__(self):
        return f'<Student {self.name} - {self.batch}>'