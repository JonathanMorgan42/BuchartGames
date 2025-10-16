from app import db


class Game(db.Model):
    __tablename__ = 'game'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=True)
    isCompleted = db.Column(db.Boolean, default=False)
    sequence_number = db.Column(db.Integer, default=0)
    point_scheme = db.Column(db.Integer, default=1)
    metric_type = db.Column(db.String(20), default='score')
    scoring_direction = db.Column(db.String(20), default='lower_better')
    public_input = db.Column(db.Boolean, default=False)
    game_night_id = db.Column(db.Integer, db.ForeignKey('game_night.id'), nullable=True, index=True)

    scores = db.relationship('Score', back_populates='game', lazy='dynamic', cascade='all, delete-orphan')
    penalties = db.relationship('Penalty', back_populates='game', lazy='dynamic', cascade='all, delete-orphan')
    game_night = db.relationship('GameNight', back_populates='games')
