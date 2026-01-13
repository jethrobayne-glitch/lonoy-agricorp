from datetime import datetime
from .user import db

class StudyFolder(db.Model):
    __tablename__ = 'study_folders'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    parent_folder_id = db.Column(db.Integer, db.ForeignKey('study_folders.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Self-referential relationship for nested folders
    subfolders = db.relationship('StudyFolder', backref=db.backref('parent', remote_side=[id]), lazy=True)
    
    # Relationship with videos
    videos = db.relationship('StudyVideo', backref='folder', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_folder_id': self.parent_folder_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'subfolder_count': len(self.subfolders),
            'video_count': len(self.videos)
        }
