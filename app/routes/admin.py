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
            'lower_is_better': form.lower_is_better.data
        }

        GameService.create_game(form_data)
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
            'lower_is_better': form.lower_is_better.data
        }

        try:
            GameService.update_game(game_id, form_data)
            flash('Game updated successfully!', 'success')
            return redirect(url_for('main.games'))
        except Exception as e:
            flash(f'Error updating game: {str(e)}', 'error')

    return render_template('admin/edit_game.html', form=form, game=game)


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

    return render_template(
        'admin/live_scoring.html',
        form=form,
        game=game,
        teams=teams,
        existing_scores=existing_scores
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