from datetime import datetime, date
from app import db
from app.models import GameNight, Team, Game


class GameNightService:

    @staticmethod
    def create_game_night(name, game_date=None):
        """
        Create a new game night session.
        Automatically sets as working context if no other working context exists.

        Args:
            name: Name of the game night
            game_date: Date of the game night (defaults to today)

        Returns:
            The created GameNight object
        """
        if game_date is None:
            game_date = date.today()

        # Convert string date to date object if needed
        if isinstance(game_date, str):
            game_date = datetime.strptime(game_date, '%Y-%m-%d').date()

        # Check if there's already a working context
        has_working_context = GameNight.query.filter_by(is_working_context=True).first() is not None

        game_night = GameNight(
            name=name,
            date=game_date,
            is_active=False,  # Don't automatically activate
            is_working_context=not has_working_context,  # Set as working context if none exists
            is_completed=False
        )

        db.session.add(game_night)
        db.session.commit()

        return game_night

    @staticmethod
    def set_active_game_night(game_night_id):
        """
        Set a game night as active. Deactivates all other game nights.

        Args:
            game_night_id: ID of the game night to activate

        Returns:
            The activated GameNight object
        """
        # Deactivate all game nights
        GameNight.query.update({'is_active': False})

        # Activate the selected one
        game_night = GameNight.query.get_or_404(game_night_id)
        game_night.is_active = True

        db.session.commit()

        return game_night

    @staticmethod
    def get_active_game_night():
        """
        Get the currently active game night (visible to public).

        Returns:
            The active GameNight object or None if no active session
        """
        return GameNight.query.filter_by(is_active=True).first()

    @staticmethod
    def get_working_context_game_night():
        """
        Get the game night currently being worked on (admin context).
        This is the game night that teams and games will be added to.

        Returns:
            The working context GameNight object or None if no working context
        """
        return GameNight.query.filter_by(is_working_context=True).first()

    @staticmethod
    def set_working_context(game_night_id):
        """
        Set a game night as the working context.
        Only one game night can be the working context at a time.

        Args:
            game_night_id: ID of the game night to set as working context

        Returns:
            The updated GameNight object
        """
        # Deactivate all working contexts
        GameNight.query.update({'is_working_context': False})

        # Set the selected one as working context
        game_night = GameNight.query.get_or_404(game_night_id)
        game_night.is_working_context = True

        db.session.commit()

        return game_night

    @staticmethod
    def get_all_game_nights(order='desc'):
        """
        Get all game nights, ordered by date.

        Args:
            order: 'desc' for newest first, 'asc' for oldest first

        Returns:
            List of GameNight objects
        """
        query = GameNight.query

        if order == 'desc':
            query = query.order_by(GameNight.date.desc(), GameNight.created_at.desc())
        else:
            query = query.order_by(GameNight.date.asc(), GameNight.created_at.asc())

        return query.all()

    @staticmethod
    def get_completed_game_nights():
        """
        Get all completed game nights, newest first.

        Returns:
            List of completed GameNight objects
        """
        return GameNight.query.filter_by(is_completed=True).order_by(
            GameNight.date.desc(),
            GameNight.ended_at.desc()
        ).all()

    @staticmethod
    def get_game_night_by_id(game_night_id):
        """
        Get a specific game night by ID.

        Args:
            game_night_id: ID of the game night

        Returns:
            GameNight object or 404 error
        """
        return GameNight.query.get_or_404(game_night_id)

    @staticmethod
    def get_game_night_details(game_night_id):
        """
        Get full details of a game night including teams, games, and leaderboard.

        Args:
            game_night_id: ID of the game night

        Returns:
            Dictionary with game night details
        """
        game_night = GameNight.query.get_or_404(game_night_id)

        teams = game_night.get_leaderboard()
        games = game_night.games.order_by(Game.sequence_number).all()
        completed_games = [g for g in games if g.isCompleted]
        upcoming_games = [g for g in games if not g.isCompleted]
        winner = game_night.get_winner()

        return {
            'game_night': game_night,
            'teams': teams,
            'games': games,
            'completed_games': completed_games,
            'upcoming_games': upcoming_games,
            'winner': winner
        }

    @staticmethod
    def end_game_night(game_night_id):
        """
        End a game night session. Marks it as completed and inactive.
        Locks all edits by finalizing the data.

        Args:
            game_night_id: ID of the game night to end

        Returns:
            The ended GameNight object
        """
        game_night = GameNight.query.get_or_404(game_night_id)
        game_night.finalize()

        return game_night

    @staticmethod
    def wipe_game_night_data(game_night_id):
        """
        Wipe all data from a game night (teams and games).
        Useful for resetting the active session.

        Args:
            game_night_id: ID of the game night to wipe

        Returns:
            The wiped GameNight object
        """
        game_night = GameNight.query.get_or_404(game_night_id)

        # Delete all games (which will cascade delete scores and penalties)
        Game.query.filter_by(game_night_id=game_night_id).delete()

        # Delete all teams (which will cascade delete participants)
        Team.query.filter_by(game_night_id=game_night_id).delete()

        db.session.commit()

        return game_night

    @staticmethod
    def delete_game_night(game_night_id):
        """
        Permanently delete a game night and all associated data.

        Args:
            game_night_id: ID of the game night to delete
        """
        game_night = GameNight.query.get_or_404(game_night_id)

        db.session.delete(game_night)
        db.session.commit()

    @staticmethod
    def update_game_night(game_night_id, name=None, game_date=None):
        """
        Update game night details.

        Args:
            game_night_id: ID of the game night
            name: New name (optional)
            game_date: New date (optional)

        Returns:
            The updated GameNight object
        """
        game_night = GameNight.query.get_or_404(game_night_id)

        if name:
            game_night.name = name

        if game_date:
            if isinstance(game_date, str):
                game_date = datetime.strptime(game_date, '%Y-%m-%d').date()
            game_night.date = game_date

        db.session.commit()

        return game_night
