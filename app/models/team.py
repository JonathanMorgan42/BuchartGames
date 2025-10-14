"""Team model."""
from app import db


class Team(db.Model):
    """Team model."""
    __tablename__ = 'team'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    color = db.Column(db.String(7), nullable=False, default='#3b82f6')
    
    scores = db.relationship('Score', back_populates='team', lazy='dynamic', cascade='all, delete-orphan')
    participants = db.relationship('Participant', back_populates='team', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def totalPoints(self):
        return sum(score.points for score in self.scores)
    
    @property
    def games_played(self):
        return self.scores.count()
    
    def __repr__(self):
        return f'<Team {self.name}>'
