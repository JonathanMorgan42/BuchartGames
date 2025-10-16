from app import db


class Team(db.Model):
    __tablename__ = 'team'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    color = db.Column(db.String(7), nullable=False, default='#3b82f6')
    game_night_id = db.Column(db.Integer, db.ForeignKey('game_night.id'), nullable=True, index=True)

    scores = db.relationship('Score', back_populates='team', lazy='dynamic', cascade='all, delete-orphan')
    participants = db.relationship('Participant', back_populates='team', lazy='dynamic', cascade='all, delete-orphan')
    game_night = db.relationship('GameNight', back_populates='teams')
    
    @property
    def totalPoints(self):
        return sum(score.points for score in self.scores)
    
    @property
    def games_played(self):
        return self.scores.count()
    
    def __repr__(self):
        return f'<Team {self.name}>'
