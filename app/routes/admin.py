"""Admin routes - Team, Game, Score, and Game Night management."""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func

from app.services import TeamService, GameService, ScoreService, TournamentService, GameNightService
from app.forms import TeamForm, GameForm, LiveScoringForm
from app.forms.tournament_forms import TournamentSetupForm, MatchScoreForm
from app.forms.game_night_forms import GameNightForm
from app.models import Team, Game, Tournament, Match, GameNight

admin_bp = Blueprint('admin', __name__)


# ============================================================================
# TEAM MANAGEMENT
# ============================================================================

@admin_bp.route('/teams/add', methods=['GET', 'POST'])
@login_required
def add_team():
    """Add new team."""
    form = TeamForm()

    if form.validate_on_submit():
        participants_data = [
            {
                'firstName': form.participant1FirstName.data,
                'lastName': form.participant1LastName.data
            },
            {
                'firstName': form.participant2FirstName.data,
                'lastName': form.participant2LastName.data
            }
        ]

        # Add optional participants (3-6)
        for i in range(3, 7):
            first_name_field = getattr(form, f'participant{i}FirstName', None)
            last_name_field = getattr(form, f'participant{i}LastName', None)

            if first_name_field and last_name_field:
                first_name = first_name_field.data
                last_name = last_name_field.data

                # Only add if at least first name is provided
                if first_name and first_name.strip():
                    participants_data.append({
                        'firstName': first_name,
                        'lastName': last_name if last_name else ''
                    })

        TeamService.create_team(form.name.data, participants_data, form.color.data)
        flash('Team created successfully!', 'success')
        return redirect(url_for('main.teams'))

    return render_template('admin/add_team.html', form=form)


@admin_bp.route('/teams/edit/<int:team_id>', methods=['GET', 'POST'])
@login_required
def edit_team(team_id):
    """Edit team."""
    team = TeamService.get_team_by_id(team_id)
    form = TeamForm()

    if request.method == 'GET':
        participants = team.participants.all()
        form.name.data = team.name
        form.color.data = team.color

        # Populate all participant fields (1-6)
        for i, participant in enumerate(participants, start=1):
            if i <= 6:
                first_name_field = getattr(form, f'participant{i}FirstName', None)
                last_name_field = getattr(form, f'participant{i}LastName', None)

                if first_name_field and last_name_field:
                    first_name_field.data = participant.firstName
                    last_name_field.data = participant.lastName

    if form.validate_on_submit():
        participants_data = [
            {
                'firstName': form.participant1FirstName.data,
                'lastName': form.participant1LastName.data
            },
            {
                'firstName': form.participant2FirstName.data,
                'lastName': form.participant2LastName.data
            }
        ]

        # Add optional participants (3-6)
        for i in range(3, 7):
            first_name_field = getattr(form, f'participant{i}FirstName', None)
            last_name_field = getattr(form, f'participant{i}LastName', None)

            if first_name_field and last_name_field:
                first_name = first_name_field.data
                last_name = last_name_field.data

                # Only add if at least first name is provided
                if first_name and first_name.strip():
                    participants_data.append({
                        'firstName': first_name,
                        'lastName': last_name if last_name else ''
                    })

        TeamService.update_team(team_id, form.name.data, participants_data, form.color.data)
        flash('Team updated successfully!', 'success')
        return redirect(url_for('main.teams'))

    return render_template('admin/edit_team.html', form=form, team=team)


@admin_bp.route('/teams/delete/<int:team_id>', methods=['POST'])
@login_required
def delete_team(team_id):
    """Delete team."""
    try:
        TeamService.delete_team(team_id)
        flash('Team deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting team: {str(e)}', 'error')

    return redirect(url_for('main.teams'))


# ============================================================================
# GAME MANAGEMENT
# ============================================================================

@admin_bp.route('/games/add', methods=['GET', 'POST'])
@login_required
def add_game():
    """Add new game."""
    form = GameForm()

    if form.validate_on_submit():
        # Check if tournament mode is enabled
        create_as_tournament = request.form.get('create_as_tournament') == 'on'

        # Handle custom game type
        game_type = form.type.data
        if game_type == 'custom' and form.custom_type.data:
            game_type = form.custom_type.data.strip()

        # Override type to 'tournament' if checkbox is checked
        if create_as_tournament:
            game_type = 'tournament'

        form_data = {
            'name': form.name.data,
            'type': game_type,
            'sequence_number': form.sequence_number.data,
            'point_scheme': form.point_scheme.data,
            'metric_type': form.metric_type.data,
            'scoring_direction': form.scoring_direction.data,
            'public_input': form.public_input.data
        }

        # Collect penalties from form
        penalties_data = []
        penalties_dict = request.form.to_dict(flat=False)
        penalty_count = 0

        while f'penalties[{penalty_count}][name]' in penalties_dict:
            penalty = {
                'name': penalties_dict[f'penalties[{penalty_count}][name]'][0],
                'value': int(penalties_dict[f'penalties[{penalty_count}][value]'][0]),
                'stackable': f'penalties[{penalty_count}][stackable]' in penalties_dict
            }
            penalties_data.append(penalty)
            penalty_count += 1

        game = GameService.create_game(form_data, penalties_data)
        flash('Game created successfully!', 'success')

        # Redirect to tournament setup if tournament mode
        if create_as_tournament:
            flash('Now set up the tournament bracket', 'info')
            return redirect(url_for('admin.setup_tournament', game_id=game.id))

        return redirect(url_for('main.games'))

    # Get next available sequence number
    max_sequence = Game.query.with_entities(func.max(Game.sequence_number)).scalar()
    next_sequence = (max_sequence or 0) + 1

    # Get existing games for reference
    existing_games = Game.query.order_by(Game.sequence_number).all()

    # Set default sequence number if not already set
    if not form.sequence_number.data:
        form.sequence_number.data = next_sequence

    team_count = Team.query.count()
    return render_template('admin/add_game.html', form=form, team_count=team_count,
                         next_sequence=next_sequence, existing_games=existing_games)


@admin_bp.route('/games/edit/<int:game_id>', methods=['GET', 'POST'])
@login_required
def edit_game(game_id):
    """Edit game."""
    game = GameService.get_game_by_id(game_id)
    form = GameForm(obj=game)

    if form.validate_on_submit():
        # Handle custom game type
        game_type = form.type.data
        if game_type == 'custom' and form.custom_type.data:
            game_type = form.custom_type.data.strip()

        form_data = {
            'name': form.name.data,
            'type': game_type,
            'sequence_number': form.sequence_number.data,
            'point_scheme': form.point_scheme.data,
            'metric_type': form.metric_type.data,
            'scoring_direction': form.scoring_direction.data,
            'public_input': form.public_input.data
        }

        # Collect penalties from form
        penalties_data = []
        penalties_dict = request.form.to_dict(flat=False)
        penalty_count = 0

        while f'penalties[{penalty_count}][name]' in penalties_dict:
            penalty = {
                'name': penalties_dict[f'penalties[{penalty_count}][name]'][0],
                'value': int(penalties_dict[f'penalties[{penalty_count}][value]'][0]),
                'stackable': f'penalties[{penalty_count}][stackable]' in penalties_dict
            }
            penalties_data.append(penalty)
            penalty_count += 1

        try:
            GameService.update_game(game_id, form_data, penalties_data)
            flash('Game updated successfully!', 'success')
            return redirect(url_for('main.games'))
        except Exception as e:
            flash(f'Error updating game: {str(e)}', 'error')

    # Convert penalties to dictionaries for JSON serialization
    penalties = game.penalties.all()
    penalties_dict = [{
        'id': p.id,
        'name': p.name,
        'value': p.value,
        'stackable': p.stackable
    } for p in penalties]

    # Get existing games for reference (excluding current game)
    existing_games = Game.query.filter(Game.id != game_id).order_by(Game.sequence_number).all()

    team_count = Team.query.count()
    return render_template('admin/edit_game.html', form=form, game=game, penalties_json=penalties_dict,
                         team_count=team_count, existing_games=existing_games)


@admin_bp.route('/games/delete/<int:game_id>', methods=['POST'])
@login_required
def delete_game(game_id):
    """Delete game."""
    try:
        game = GameService.get_game_by_id(game_id)
        game_name = game.name
        GameService.delete_game(game_id)
        flash(f'Game "{game_name}" has been deleted', 'success')
    except Exception as e:
        flash(f'Error deleting game: {str(e)}', 'error')

    return redirect(url_for('main.games'))


# ============================================================================
# SCORE MANAGEMENT
# ============================================================================

@admin_bp.route('/scores/edit/<int:game_id>', methods=['GET', 'POST'])
@login_required
def edit_scores(game_id):
    """Live scoring page."""
    game = GameService.get_game_by_id(game_id)
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

    return render_template(
        'admin/live_scoring.html',
        form=form,
        game=game,
        teams=teams,
        teams_json=teams_dict,
        existing_scores=existing_scores,
        existing_scores_json=existing_scores_dict,
        penalties=penalties_dict
    )


@admin_bp.route('/scores/save/<int:game_id>', methods=['POST'])
@login_required
def save_scores(game_id):
    """AJAX endpoint for saving scores."""
    data = request.json

    try:
        ScoreService.save_scores(
            game_id,
            data.get('scores', {}),
            data.get('isCompleted', False),
            data.get('notes')
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# ============================================================================
# TOURNAMENT MANAGEMENT
# ============================================================================

@admin_bp.route('/tournament/create', methods=['GET', 'POST'])
@login_required
def create_tournament_direct():
    """Create a tournament directly (combines game creation and tournament setup)."""
    from app.forms.tournament_forms import TournamentSetupForm

    if request.method == 'POST':
        form = TournamentSetupForm()
        if form.validate_on_submit():
            # Create the game first
            game_name = request.form.get('game_name', 'Tournament')
            sequence_number = Game.query.with_entities(func.max(Game.sequence_number)).scalar() or 0
            sequence_number += 1

            game_data = {
                'name': game_name,
                'type': 'tournament',
                'sequence_number': sequence_number,
                'point_scheme': 1,
                'metric_type': 'score',
                'scoring_direction': 'higher_better',
                'public_input': False
            }

            game = GameService.create_game(game_data, [])

            # Create tournament
            try:
                # Get included teams (filter out unchecked teams)
                included_team_ids = request.form.getlist('included_teams')
                included_team_ids = [int(tid) for tid in included_team_ids] if included_team_ids else None

                tournament = TournamentService.create_tournament(
                    game_id=game.id,
                    pairing_type=form.pairing_type.data,
                    bracket_style=form.bracket_style.data,
                    public_edit=form.public_edit.data,
                    included_team_ids=included_team_ids
                )
                flash(f'Tournament "{game_name}" created successfully!', 'success')
                return redirect(url_for('admin.view_tournament', game_id=game.id))
            except Exception as e:
                # If tournament creation fails, delete the game
                GameService.delete_game(game.id)
                flash(f'Error creating tournament: {str(e)}', 'error')
                return redirect(url_for('main.games'))

    # GET request - show form
    form = TournamentSetupForm()
    # Get teams from active game night
    active_gn = GameNightService.get_active_game_night()
    if active_gn:
        teams = Team.query.filter_by(game_night_id=active_gn.id).all()
    else:
        teams = Team.query.all()
    return render_template('admin/create_tournament_direct.html', form=form, teams=teams)


@admin_bp.route('/tournament/setup/<int:game_id>', methods=['GET', 'POST'])
@login_required
def setup_tournament(game_id):
    """Setup tournament bracket for a game."""
    game = GameService.get_game_by_id(game_id)

    # Check if tournament already exists
    existing_tournament = TournamentService.get_tournament_by_game(game_id)
    if existing_tournament:
        flash('Tournament already exists for this game', 'info')
        return redirect(url_for('admin.view_tournament', game_id=game_id))

    form = TournamentSetupForm()
    form.game_id.data = game_id

    if form.validate_on_submit():
        try:
            # Get included teams (filter out unchecked teams)
            included_team_ids = request.form.getlist('included_teams')
            included_team_ids = [int(tid) for tid in included_team_ids] if included_team_ids else None

            # Parse manual pairings if provided
            manual_pairings = None
            if form.pairing_type.data == 'manual':
                manual_pairings_json = request.form.get('manual_pairings', '[]')
                try:
                    import json
                    pairings_list = json.loads(manual_pairings_json)
                    if pairings_list:
                        manual_pairings = [(p[0], p[1]) for p in pairings_list]
                except (json.JSONDecodeError, IndexError, KeyError):
                    flash('Error parsing manual pairings. Using random pairing instead.', 'warning')

            tournament = TournamentService.create_tournament(
                game_id=game_id,
                pairing_type=form.pairing_type.data,
                bracket_style=form.bracket_style.data,
                public_edit=form.public_edit.data,
                manual_pairings=manual_pairings,
                included_team_ids=included_team_ids
            )
            flash('Tournament bracket created successfully!', 'success')
            return redirect(url_for('admin.view_tournament', game_id=game_id))
        except Exception as e:
            flash(f'Error creating tournament: {str(e)}', 'error')
            import traceback
            traceback.print_exc()

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
    return render_template('admin/setup_tournament.html', form=form, game=game, teams=teams)


@admin_bp.route('/tournament/view/<int:game_id>')
@login_required
def view_tournament(game_id):
    """View and manage tournament bracket."""
    game = GameService.get_game_by_id(game_id)
    tournament = TournamentService.get_tournament_by_game(game_id)

    if not tournament:
        flash('No tournament found for this game', 'error')
        return redirect(url_for('main.games'))

    bracket_data = TournamentService.get_bracket_structure(tournament.id)

    return render_template('admin/view_tournament.html',
                         game=game,
                         tournament=tournament,
                         bracket=bracket_data['bracket'],
                         rounds=bracket_data['rounds'])


@admin_bp.route('/tournament/match/<int:match_id>/score', methods=['POST'])
@login_required
def score_match(match_id):
    """Update match score and advance winner."""
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


@admin_bp.route('/tournament/reset/<int:tournament_id>', methods=['POST'])
@login_required
def reset_tournament(tournament_id):
    """Reset tournament to initial state."""
    try:
        TournamentService.reset_tournament(tournament_id)
        tournament = Tournament.query.get_or_404(tournament_id)
        flash('Tournament has been reset', 'success')
        return redirect(url_for('admin.view_tournament', game_id=tournament.game_id))
    except Exception as e:
        flash(f'Error resetting tournament: {str(e)}', 'error')
        return redirect(url_for('main.games'))


# ============================================================================
# GAME NIGHT MANAGEMENT
# ============================================================================

@admin_bp.route('/game-nights')
@login_required
def game_night_management():
    """Game night management dashboard."""
    game_nights = GameNightService.get_all_game_nights(order='desc')
    active_game_night = GameNightService.get_active_game_night()

    return render_template(
        'admin/game_night_management.html',
        game_nights=game_nights,
        active_game_night=active_game_night
    )


@admin_bp.route('/game-nights/create', methods=['GET', 'POST'])
@login_required
def create_game_night():
    """Create a new game night."""
    form = GameNightForm()

    if form.validate_on_submit():
        try:
            game_night = GameNightService.create_game_night(
                name=form.name.data,
                game_date=form.date.data
            )
            flash(f'Game Night "{game_night.name}" created successfully!', 'success')
            return redirect(url_for('admin.game_night_management'))
        except Exception as e:
            flash(f'Error creating game night: {str(e)}', 'error')

    return render_template('admin/create_game_night.html', form=form)


@admin_bp.route('/game-nights/<int:game_night_id>/activate', methods=['POST'])
@login_required
def activate_game_night(game_night_id):
    """Set a game night as active."""
    try:
        game_night = GameNightService.set_active_game_night(game_night_id)
        flash(f'"{game_night.name}" is now the active game night!', 'success')
    except Exception as e:
        flash(f'Error activating game night: {str(e)}', 'error')

    return redirect(url_for('admin.game_night_management'))


@admin_bp.route('/game-nights/<int:game_night_id>/end', methods=['POST'])
@login_required
def end_game_night(game_night_id):
    """End/finalize a game night."""
    try:
        game_night = GameNightService.end_game_night(game_night_id)
        flash(f'Game Night "{game_night.name}" has been ended and finalized!', 'success')
    except Exception as e:
        flash(f'Error ending game night: {str(e)}', 'error')

    return redirect(url_for('admin.game_night_management'))


@admin_bp.route('/game-nights/<int:game_night_id>/wipe', methods=['POST'])
@login_required
def wipe_game_night(game_night_id):
    """Wipe data from a game night."""
    try:
        game_night = GameNightService.wipe_game_night_data(game_night_id)
        flash(f'All data cleared from "{game_night.name}"!', 'success')
    except Exception as e:
        flash(f'Error wiping game night: {str(e)}', 'error')

    return redirect(url_for('admin.game_night_management'))


@admin_bp.route('/game-nights/<int:game_night_id>/delete', methods=['POST'])
@login_required
def delete_game_night(game_night_id):
    """Delete a game night permanently."""
    try:
        game_night = GameNightService.get_game_night_by_id(game_night_id)
        game_night_name = game_night.name

        GameNightService.delete_game_night(game_night_id)
        flash(f'Game Night "{game_night_name}" has been deleted!', 'success')
    except Exception as e:
        flash(f'Error deleting game night: {str(e)}', 'error')

    return redirect(url_for('admin.game_night_management'))