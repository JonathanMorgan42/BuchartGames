"""Game model."""
from app import db


class Game(db.Model):
    """Game model."""
    __tablename__ = 'game'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=True)
    isCompleted = db.Column(db.Boolean, default=False)
    sequence_number = db.Column(db.Integer, default=0)
    point_scheme = db.Column(db.Integer, default=1)
    metric_type = db.Column(db.String(20), default='manual')
    lower_is_better = db.Column(db.Boolean, default=True)
    
    scores = db.relationship('Score', back_populates='game', lazy='dynamic', cascade='all, delete-orphan')
