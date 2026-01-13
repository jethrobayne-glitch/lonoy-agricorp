from .user import db
from datetime import datetime

class EmployeeDocument(db.Model):
    __tablename__ = 'employee_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)  # Stored filename
    original_name = db.Column(db.String(255), nullable=False)  # Original filename
    file_path = db.Column(db.String(500), nullable=False)  # Full file path
    file_size = db.Column(db.Integer)  # File size in bytes
    mime_type = db.Column(db.String(100))  # File MIME type
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    employee = db.relationship('Employee', back_populates='documents')
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'filename': self.filename,
            'original_name': self.original_name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None
        }
    
    def __repr__(self):
        return f'<EmployeeDocument {self.original_name} for Employee {self.employee_id}>'