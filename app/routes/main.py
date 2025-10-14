"""Public routes."""
from flask import Blueprint, render_template

from app.services import TeamService, GameService, ScoreService
from app.models import Score

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Homepage with comprehensive leaderboard."""
    teams = TeamService.get_all_teams(sort_by_points=True)
    games = GameService.get_all_games(ordered=True)

    # Separate completed and upcoming games
    completed_games = [g for g in games if g.isCompleted]
    upcoming_games = [g for g in games if not g.isCompleted]

    def getScore(team_id, game_id):
        """Helper function for templates to get score."""
        return ScoreService.get_score(team_id, game_id)

    return render_template(
        'public/index.html',
        teams=teams,
        games=games,
        completed_games=completed_games,
        upcoming_games=upcoming_games,
        getScore=getScore
    )


@main_bp.route('/teams')
def teams():
    """Teams listing page."""
    teams = TeamService.get_all_teams(sort_by_points=True)
    return render_template('public/teams.html', teams=teams)


@main_bp.route('/games')
def games():
    """Games listing page."""
    games = GameService.get_all_games(ordered=True)
    teams = TeamService.get_all_teams(sort_by_points=False)

    return render_template(
        'public/games.html',
        games=games,
        teams=teams,
        Score=Score
    )


@main_bp.route('/games/scores/<int:game_id>')
def view_game_scores(game_id):
    """View scores for a specific game."""
    game = GameService.get_game_by_id(game_id)
    scores = ScoreService.get_scores_for_game(game_id, ordered=True)

    return render_template(
        'public/view_scores.html',
        game=game,
        scores=scores
    )