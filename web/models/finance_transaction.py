from datetime import datetime
from .user import db

class FinanceTransaction(db.Model):
    """Model for finance transactions (income and expenses)"""
    __tablename__ = 'finance_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    source = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    units = db.Column(db.Integer, nullable=False, default=1)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    receipt = db.Column(db.Text, nullable=True)
    department = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'transaction_type': self.transaction_type,
            'source': self.source,
            'description': self.description or '',
            'units': self.units or 1,
            'amount': float(self.amount) if self.amount else 0,
            'receipt': self.receipt or '',
            'department': self.department,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }
    
    def __repr__(self):
        return f'<FinanceTransaction {self.transaction_type} - {self.source} - {self.amount}>'
