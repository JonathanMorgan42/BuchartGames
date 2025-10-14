"""Admin routes - Team, Game, and Score management."""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user

from app.services import TeamService, GameService, ScoreService
from app.forms import TeamForm, GameForm, LiveScoringForm
from app.models import Team

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

        if len(participants) >= 1:
            form.participant1FirstName.data = participants[0].firstName
            form.participant1LastName.data = participants[0].lastName

        if len(participants) >= 2:
            form.participant2FirstName.data = participants[1].firstName
            form.participant2LastName.data = participants[1].lastName

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
        form_data = {
            'name': form.name.data,
            'type': form.type.data,
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

        GameService.create_game(form_data, penalties_data)
        flash('Game created successfully!', 'success')
        return redirect(url_for('main.games'))

    return render_template('admin/add_game.html', form=form)


@admin_bp.route('/games/edit/<int:game_id>', methods=['GET', 'POST'])
@login_required
def edit_game(game_id):
    """Edit game."""
    game = GameService.get_game_by_id(game_id)
    form = GameForm(obj=game)

    if form.validate_on_submit():
        form_data = {
            'name': form.name.data,
            'type': form.type.data,
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

    return render_template('admin/edit_game.html', form=form, game=game, penalties_json=penalties_dict)


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