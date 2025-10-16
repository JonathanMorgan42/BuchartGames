"""Public routes."""
from flask import Blueprint, render_template, request, jsonify

from app.services import TeamService, GameService, ScoreService, TournamentService, GameNightService
from app.models import Score, Tournament

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Homepage with comprehensive leaderboard."""
    # Get active game night
    active_game_night = GameNightService.get_active_game_night()

    # Filter teams and games by active game night
    game_night_id = active_game_night.id if active_game_night else None
    teams = TeamService.get_all_teams(sort_by_points=True, game_night_id=game_night_id)
    games = GameService.get_all_games(ordered=True, game_night_id=game_night_id)

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
        getScore=getScore,
        active_game_night=active_game_night
    )


@main_bp.route('/teams')
def teams():
    """Teams listing page."""
    active_game_night = GameNightService.get_active_game_night()
    game_night_id = active_game_night.id if active_game_night else None

    teams = TeamService.get_all_teams(sort_by_points=True, game_night_id=game_night_id)
    return render_template('public/teams.html', teams=teams, active_game_night=active_game_night)


@main_bp.route('/games')
def games():
    """Games listing page."""
    active_game_night = GameNightService.get_active_game_night()
    game_night_id = active_game_night.id if active_game_night else None

    games = GameService.get_all_games(ordered=True, game_night_id=game_night_id)
    teams = TeamService.get_all_teams(sort_by_points=False, game_night_id=game_night_id)

    return render_template(
        'public/games.html',
        games=games,
        teams=teams,
        Score=Score,
        active_game_night=active_game_night
    )


@main_bp.route('/games/scores/<int:game_id>')
def view_game_scores(game_id):
    """View scores for a specific game."""
    game = GameService.get_game_by_id(game_id)
    scores = ScoreService.get_scores_for_game(game_id, ordered=True)
    active_game_night = GameNightService.get_active_game_night()

    return render_template(
        'public/view_scores.html',
        game=game,
        scores=scores,
        active_game_night=active_game_night
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

    # Get teams from the same game night as the game
    if game.game_night_id:
        teams = Team.query.filter_by(game_night_id=game.game_night_id).all()
    else:
        # Fallback to active game night teams
        active_gn = GameNightService.get_active_game_night()
        if active_gn:
            teams = Team.query.filter_by(game_night_id=active_gn.id).all()
        else:
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

    active_game_night = GameNightService.get_active_game_night()

    return render_template(
        'public/public_scoring.html',
        form=form,
        game=game,
        teams=teams,
        teams_json=teams_dict,
        existing_scores=existing_scores,
        existing_scores_json=existing_scores_dict,
        penalties=penalties_dict,
        active_game_night=active_game_night
    )


@main_bp.route('/playground')
def playground():
    """Simulation playground for exploring hypothetical game outcomes."""
    # Get active game night to filter teams and games
    active_game_night = GameNightService.get_active_game_night()
    game_night_id = active_game_night.id if active_game_night else None

    teams = TeamService.get_all_teams(sort_by_points=True, game_night_id=game_night_id)
    games = GameService.get_all_games(ordered=True, game_night_id=game_night_id)

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
        getScore=getScore,
        active_game_night=active_game_night
    )


@main_bp.route('/tournament/<int:game_id>')
def view_tournament_public(game_id):
    """Public view of tournament bracket."""
    game = GameService.get_game_by_id(game_id)
    tournament = TournamentService.get_tournament_by_game(game_id)
    active_game_night = GameNightService.get_active_game_night()

    if not tournament:
        from flask import flash, redirect, url_for
        flash('No tournament found for this game', 'error')
        return redirect(url_for('main.games'))

    bracket_data = TournamentService.get_bracket_structure(tournament.id)

    return render_template('public/view_tournament.html',
                         game=game,
                         tournament=tournament,
                         bracket=bracket_data['bracket'],
                         rounds=bracket_data['rounds'],
                         active_game_night=active_game_night)


@main_bp.route('/tournament/match/<int:match_id>/score', methods=['POST'])
def score_match_public(match_id):
    """Public endpoint for scoring matches (when public_edit is enabled)."""
    from app.models import Match

    match = Match.query.get_or_404(match_id)
    tournament = match.tournament

    # Check if public editing is allowed
    if not tournament.public_edit:
        return jsonify({'success': False, 'error': 'Public editing not allowed'}), 403

    data = request.json

    try:
        TournamentService.update_match_result(
            match_id=match_id,
            team1_score=data.get('team1_score'),
            team2_score=data.get('team2_score'),
            winner_team_id=data.get('winner_team_id')
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@main_bp.route('/history')
def history():
    """View all completed game night history."""
    game_nights = GameNightService.get_completed_game_nights()
    active_game_night = GameNightService.get_active_game_night()

    return render_template(
        'public/history.html',
        game_nights=game_nights,
        active_game_night=active_game_night
    )


@main_bp.route('/history/<int:game_night_id>')
def history_detail(game_night_id):
    """View detailed information about a specific game night."""
    details = GameNightService.get_game_night_details(game_night_id)
    active_game_night = GameNightService.get_active_game_night()

    def getScore(team_id, game_id):
        """Helper function for templates to get score."""
        return ScoreService.get_score(team_id, game_id)

    return render_template(
        'public/history_detail.html',
        game_night=details['game_night'],
        teams=details['teams'],
        games=details['games'],
        completed_games=details['completed_games'],
        upcoming_games=details['upcoming_games'],
        winner=details['winner'],
        getScore=getScore,
        active_game_night=active_game_night
    )