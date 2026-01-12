from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class AttackTechnique(db.Model):
    """Model for storing attack techniques from Atomic Red Team"""
    __tablename__ = 'attack_techniques'
    
    id = db.Column(db.Integer, primary_key=True)
    technique_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    tactic = db.Column(db.String(100))
    platform = db.Column(db.String(200))
    
    # Raw data from Atomic Red Team
    raw_data = db.Column(db.Text)
    
    # LLM processed data
    llm_summary = db.Column(db.Text)
    llm_analysis = db.Column(db.Text)
    llm_processed_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'technique_id': self.technique_id,
            'name': self.name,
            'description': self.description,
            'tactic': self.tactic,
            'platform': self.platform,
            'llm_summary': self.llm_summary,
            'llm_analysis': self.llm_analysis,
            'llm_processed_at': self.llm_processed_at.isoformat() if self.llm_processed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<AttackTechnique {self.technique_id}: {self.name}>'


class AtomicTest(db.Model):
    """Model for storing individual atomic tests"""
    __tablename__ = 'atomic_tests'
    
    id = db.Column(db.Integer, primary_key=True)
    technique_id = db.Column(db.String(50), db.ForeignKey('attack_techniques.technique_id'), nullable=False, index=True)
    test_number = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    supported_platforms = db.Column(db.String(200))
    executor = db.Column(db.String(50))
    command = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    technique = db.relationship('AttackTechnique', backref='atomic_tests')
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'technique_id': self.technique_id,
            'test_number': self.test_number,
            'name': self.name,
            'description': self.description,
            'supported_platforms': self.supported_platforms,
            'executor': self.executor,
            'command': self.command,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<AtomicTest {self.technique_id}.{self.test_number}: {self.name}>'
