"""Score model."""
from app import db


class Score(db.Model):
    """Score model."""
    __tablename__ = 'score'
    
    id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Integer, default=0)
    score_value = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    
    team = db.relationship('Team', back_populates='scores')
    game = db.relationship('Game', back_populates='scores')
