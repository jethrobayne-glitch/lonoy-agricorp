from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Import the db instance from user module
from .user import db

class TVETInventoryFolder(db.Model):
    """Model for TVET inventory folders"""
    __tablename__ = 'tvet_inventory_folders'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship with materials
    materials = db.relationship('TVETInventoryMaterial', backref='folder', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<TVETInventoryFolder {self.name}>'

class TVETCoreCompetency(db.Model):
    """Model for TVET core competencies"""
    __tablename__ = 'tvet_core_competencies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship with materials
    materials = db.relationship('TVETInventoryMaterial', backref='competency', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<TVETCoreCompetency {self.name}>'

class TVETCategory(db.Model):
    """Model for TVET material categories"""
    __tablename__ = 'tvet_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship with materials
    materials = db.relationship('TVETInventoryMaterial', backref='category', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<TVETCategory {self.name}>'

class TVETInspectionRemark(db.Model):
    """Model for TVET inspection remarks"""
    __tablename__ = 'tvet_inspection_remarks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship with materials
    materials = db.relationship('TVETInventoryMaterial', backref='inspection_remark_ref', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<TVETInspectionRemark {self.name}>'

class TVETInventoryMaterial(db.Model):
    """Model for TVET inventory materials"""
    __tablename__ = 'tvet_inventory_materials'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    folder_id = db.Column(db.Integer, db.ForeignKey('tvet_inventory_folders.id'), nullable=True)
    competency_id = db.Column(db.Integer, db.ForeignKey('tvet_core_competencies.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('tvet_categories.id'), nullable=True)
    inspection_remark_id = db.Column(db.Integer, db.ForeignKey('tvet_inspection_remarks.id'), nullable=True)
    
    # Material details
    item = db.Column(db.String(200), nullable=False)
    specification = db.Column(db.Text, nullable=True)
    quantity_required = db.Column(db.Integer, nullable=False, default=0)
    quantity_on_site = db.Column(db.Integer, nullable=False, default=0)
    quantity_y1 = db.Column(db.Integer, nullable=False, default=0)
    quantity_y2 = db.Column(db.Integer, nullable=False, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    @property
    def difference(self):
        """Calculate the difference between required and on-site quantities"""
        return self.quantity_on_site - self.quantity_required
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'folder_id': self.folder_id,
            'competency_id': self.competency_id,
            'category_id': self.category_id,
            'inspection_remark_id': self.inspection_remark_id,
            'item': self.item,
            'specification': self.specification or '',
            'quantity_required': self.quantity_required,
            'quantity_on_site': self.quantity_on_site,
            'quantity_y1': self.quantity_y1,
            'quantity_y2': self.quantity_y2,
            'difference': self.difference,
            'folder_name': self.folder.name if self.folder else None,
            'competency_name': self.competency.name if self.competency else None,
            'category_name': self.category.name if self.category else None,
            'inspection_remark': self.inspection_remark_ref.name if self.inspection_remark_ref else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<TVETInventoryMaterial {self.item}>'