from .user import db
from datetime import datetime

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    department = db.Column(db.String(10), nullable=False, default='TVET')  # TVET or LPAF
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with documents
    documents = db.relationship('EmployeeDocument', back_populates='employee', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert employee object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'position': self.position,
            'job_description': self.job_description,
            'department': self.department,
            'documents_count': len(self.documents) if self.documents else 0,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def __repr__(self):
        return f'<Employee {self.name} - {self.position}>'