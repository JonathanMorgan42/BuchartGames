from datetime import datetime
from app import db


class GameNight(db.Model):
    __tablename__ = 'game_night'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=False, index=True)
    is_completed = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    teams = db.relationship('Team', back_populates='game_night', lazy='dynamic', cascade='all, delete-orphan')
    games = db.relationship('Game', back_populates='game_night', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def total_games(self):
        """Get total number of games in this game night."""
        return self.games.count()

    @property
    def completed_games(self):
        """Get number of completed games."""
        return self.games.filter_by(isCompleted=True).count()

    def get_leaderboard(self):
        """Get sorted leaderboard for this game night."""
        teams = self.teams.all()
        # Sort by total points descending
        return sorted(teams, key=lambda t: t.totalPoints or 0, reverse=True)

    def get_winner(self):
        """Get the winning team (team with highest points)."""
        leaderboard = self.get_leaderboard()
        return leaderboard[0] if leaderboard else None

    def finalize(self):
        """Mark game night as completed and lock all edits."""
        self.is_completed = True
        self.is_active = False
        self.ended_at = datetime.utcnow()
        db.session.commit()

    def __repr__(self):
        return f'<GameNight {self.name} - {self.date}>'
