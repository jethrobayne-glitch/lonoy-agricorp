from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Import the db instance from user module
from .user import db

class LPAFInventoryFolder(db.Model):
    """Model for LPAF inventory folders"""
    __tablename__ = 'lpaf_inventory_folders'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship with materials
    materials = db.relationship('LPAFInventoryMaterial', backref='folder', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<LPAFInventoryFolder {self.name}>'

class LPAFProduction(db.Model):
    """Model for LPAF production types"""
    __tablename__ = 'lpaf_productions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship with materials
    materials = db.relationship('LPAFInventoryMaterial', backref='production', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<LPAFProduction {self.name}>'

class LPAFStatus(db.Model):
    """Model for LPAF inventory status"""
    __tablename__ = 'lpaf_statuses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship with materials
    materials = db.relationship('LPAFInventoryMaterial', backref='status', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<LPAFStatus {self.name}>'

class LPAFInventoryMaterial(db.Model):
    """Model for LPAF inventory materials"""
    __tablename__ = 'lpaf_inventory_materials'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    folder_id = db.Column(db.Integer, db.ForeignKey('lpaf_inventory_folders.id'), nullable=True)
    production_id = db.Column(db.Integer, db.ForeignKey('lpaf_productions.id'), nullable=True)
    status_id = db.Column(db.Integer, db.ForeignKey('lpaf_statuses.id'), nullable=True)
    
    # Material details
    item_name = db.Column(db.String(200), nullable=False)
    item_code = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'folder_id': self.folder_id,
            'production_id': self.production_id,
            'status_id': self.status_id,
            'item_name': self.item_name,
            'item_code': self.item_code or '',
            'description': self.description or '',
            'folder_name': self.folder.name if self.folder else None,
            'production_name': self.production.name if self.production else None,
            'status_name': self.status.name if self.status else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<LPAFInventoryMaterial {self.item_name}>'