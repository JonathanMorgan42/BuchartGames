"""Game service - business logic for games."""
from app import db
from app.models import Game, Score


class GameService:
    """Service class for game operations."""

    @staticmethod
    def get_all_games(ordered=True):
        """
        Get all games.

        Args:
            ordered: If True, order by sequence_number

        Returns:
            List of Game objects
        """
        if ordered:
            return Game.query.order_by(Game.sequence_number).all()
        return Game.query.all()

    @staticmethod
    def get_game_by_id(game_id):
        """Get game by ID."""
        return Game.query.get_or_404(game_id)

    @staticmethod
    def create_game(form_data):
        """
        Create a new game.

        Args:
            form_data: Dict with game data from form

        Returns:
            Created Game object
        """
        game = Game(
            name=form_data['name'],
            type=form_data['type'],
            sequence_number=form_data['sequence_number'],
            point_scheme=form_data['point_scheme'],
            metric_type=form_data['metric_type'],
            lower_is_better=form_data.get('lower_is_better', True),
            isCompleted=False
        )
        db.session.add(game)
        db.session.commit()
        return game

    @staticmethod
    def update_game(game_id, form_data):
        """
        Update game.

        Args:
            game_id: Game ID
            form_data: Dict with updated game data
        """
        game = Game.query.get_or_404(game_id)

        game.name = form_data['name']
        game.type = form_data['type']
        game.sequence_number = form_data['sequence_number']
        game.point_scheme = form_data['point_scheme']
        game.metric_type = form_data['metric_type']
        game.lower_is_better = form_data.get('lower_is_better', True)

        db.session.commit()
        return game

    @staticmethod
    def delete_game(game_id):
        """
        Delete game and all associated scores.

        Args:
            game_id: Game ID to delete
        """
        game = Game.query.get_or_404(game_id)

        # Delete associated scores
        Score.query.filter_by(game_id=game_id).delete()

        # Delete game
        db.session.delete(game)
        db.session.commit()

    @staticmethod
    def get_completed_games():
        """Get all completed games."""
        return Game.query.filter_by(isCompleted=True).order_by(Game.sequence_number).all()

    @staticmethod
    def get_upcoming_games():
        """Get all upcoming games."""
        return Game.query.filter_by(isCompleted=False).order_by(Game.sequence_number).all()