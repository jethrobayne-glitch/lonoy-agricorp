from .user import db
from datetime import datetime

class Certificate(db.Model):
    __tablename__ = 'certificates'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)  # Stored filename
    original_name = db.Column(db.String(255), nullable=False)  # Original filename
    file_path = db.Column(db.String(500), nullable=False)  # Full file path
    file_size = db.Column(db.Integer)  # File size in bytes
    mime_type = db.Column(db.String(100))  # File MIME type
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    student = db.relationship('Student', back_populates='certificates')
    
    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'filename': self.filename,
            'original_name': self.original_name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None
        }
    
    def __repr__(self):
        return f'<Certificate {self.original_name} for Student {self.student_id}>'