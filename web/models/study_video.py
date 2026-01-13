from datetime import datetime
from .user import db

class StudyVideo(db.Model):
    __tablename__ = 'study_videos'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    duration = db.Column(db.String(50))  # Store as "HH:MM:SS" or seconds
    mime_type = db.Column(db.String(100))
    thumbnail_path = db.Column(db.String(500))
    folder_id = db.Column(db.Integer, db.ForeignKey('study_folders.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'filename': self.filename,
            'original_name': self.original_name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'duration': self.duration,
            'mime_type': self.mime_type,
            'thumbnail_path': self.thumbnail_path,
            'folder_id': self.folder_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
