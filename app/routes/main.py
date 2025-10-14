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


@main_bp.route('/games/score/<int:game_id>', methods=['GET', 'POST'])
def public_score_game(game_id):
    """Public scoring page for games with public_input enabled."""
    from flask import request, flash, redirect
    from app.forms import LiveScoringForm
    from app.models import Team

    game = GameService.get_game_by_id(game_id)

    # Check if public scoring is allowed
    if not game.public_input:
        flash('Public scoring is not enabled for this game.', 'error')
        return redirect(url_for('main.games'))

    teams = Team.query.all()
    existing_scores = ScoreService.get_existing_scores_dict(game_id)

    form = LiveScoringForm()
    form.game_id.data = game_id

    # Handle form POST
    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Collect scores from form
            scores_data = {}
            for team in teams:
                score_value = request.form.get(f'score-{team.id}')
                points = request.form.get(f'points-input-{team.id}')
                notes = request.form.get(f'notes-{team.id}')

                if score_value or points:
                    scores_data[team.id] = {}

                    if score_value:
                        try:
                            scores_data[team.id]['score'] = float(score_value)
                        except (ValueError, TypeError):
                            pass

                    if points:
                        try:
                            scores_data[team.id]['points'] = int(points)
                        except (ValueError, TypeError):
                            pass

                    if notes:
                        scores_data[team.id]['notes'] = notes

            # Save scores
            ScoreService.save_scores(
                game_id,
                scores_data,
                form.is_completed.data
            )

            flash('Scores saved successfully!', 'success')
            return redirect(url_for('main.games'))
        except Exception as e:
            flash(f'Error saving scores: {str(e)}', 'error')

    penalties = game.penalties.all()

    # Convert penalties to dictionaries for JSON serialization
    penalties_dict = [{
        'id': p.id,
        'name': p.name,
        'value': p.value,
        'unit': 'seconds' if game.metric_type == 'time' else 'points',
        'stackable': p.stackable
    } for p in penalties]

    # Convert teams to dictionaries for JSON serialization
    teams_dict = [{
        'id': t.id,
        'name': t.name,
        'color': t.color
    } for t in teams]

    # Convert existing_scores to dictionaries for JSON serialization
    existing_scores_dict = {}
    for team_id, score in existing_scores.items():
        existing_scores_dict[team_id] = {
            'score_value': score.score_value,
            'points': score.points,
            'notes': score.notes
        }

    return render_template(
        'public/public_scoring.html',
        form=form,
        game=game,
        teams=teams,
        teams_json=teams_dict,
        existing_scores=existing_scores,
        existing_scores_json=existing_scores_dict,
        penalties=penalties_dict
    )


@main_bp.route('/playground')
def playground():
    """Simulation playground for exploring hypothetical game outcomes."""
    teams = TeamService.get_all_teams(sort_by_points=True)
    games = GameService.get_all_games(ordered=True)

    # Separate completed and upcoming games
    completed_games = [g for g in games if g.isCompleted]
    upcoming_games = [g for g in games if not g.isCompleted]

    # Convert to serializable dictionaries for JavaScript
    teams_json = [{
        'id': team.id,
        'name': team.name,
        'color': team.color,
        'totalPoints': team.totalPoints or 0
    } for team in teams]

    upcoming_games_json = [{
        'id': game.id,
        'name': game.name,
        'type': game.type,
        'sequence_number': game.sequence_number,
        'point_scheme': game.point_scheme
    } for game in upcoming_games]

    def getScore(team_id, game_id):
        """Helper function for templates to get score."""
        return ScoreService.get_score(team_id, game_id)

    return render_template(
        'public/playground.html',
        teams=teams,
        teams_json=teams_json,
        games=games,
        completed_games=completed_games,
        upcoming_games=upcoming_games,
        upcoming_games_json=upcoming_games_json,
        getScore=getScore
    )