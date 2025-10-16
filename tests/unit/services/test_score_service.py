"""Unit tests for ScoreService."""
import pytest
from app.services.score_service import ScoreService
from app.models import Score, Game


class TestScoreService:
    """Test score service operations."""

    def test_get_existing_scores_dict(self, db_session, game, teams):
        """Test getting existing scores as dictionary."""
        # Create scores
        score1 = Score(game_id=game.id, team_id=teams[0].id, score_value=100, points=3)
        score2 = Score(game_id=game.id, team_id=teams[1].id, score_value=90, points=2)
        db_session.add_all([score1, score2])
        db_session.commit()

        scores_dict = ScoreService.get_existing_scores_dict(game.id)

        assert len(scores_dict) == 2
        assert teams[0].id in scores_dict
        assert teams[1].id in scores_dict
        assert scores_dict[teams[0].id].score_value == 100
        assert scores_dict[teams[1].id].score_value == 90

    def test_save_scores_create_new(self, db_session, game, teams):
        """Test saving new scores."""
        scores_data = {
            teams[0].id: {'score': 100.0, 'points': 3, 'notes': 'Great job'},
            teams[1].id: {'score': 90.0, 'points': 2, 'notes': 'Good work'}
        }

        ScoreService.save_scores(game.id, scores_data, is_completed=False)

        # Verify scores were created
        score1 = Score.query.filter_by(game_id=game.id, team_id=teams[0].id).first()
        score2 = Score.query.filter_by(game_id=game.id, team_id=teams[1].id).first()

        assert score1 is not None
        assert score1.score_value == 100.0
        assert score1.points == 3
        assert score1.notes == 'Great job'

        assert score2 is not None
        assert score2.score_value == 90.0
        assert score2.points == 2

    def test_save_scores_update_existing(self, db_session, game, teams):
        """Test updating existing scores."""
        # Create initial scores
        score1 = Score(game_id=game.id, team_id=teams[0].id, score_value=100, points=3)
        db_session.add(score1)
        db_session.commit()

        # Update scores
        scores_data = {
            teams[0].id: {'score': 150.0, 'points': 5, 'notes': 'Updated'}
        }

        ScoreService.save_scores(game.id, scores_data, is_completed=False)

        # Verify score was updated
        db_session.refresh(score1)
        assert score1.score_value == 150.0
        assert score1.points == 5
        assert score1.notes == 'Updated'

    def test_save_scores_marks_game_complete(self, db_session, game, teams):
        """Test that saving scores can mark game as complete."""
        scores_data = {
            teams[0].id: {'score': 100.0, 'points': 3}
        }

        ScoreService.save_scores(game.id, scores_data, is_completed=True)

        # Verify game is marked complete
        db_session.refresh(game)
        assert game.isCompleted is True

    def test_save_scores_updates_team_totals(self, db_session, game, teams):
        """Test that saving scores updates team total points."""
        original_points = teams[0].totalPoints

        scores_data = {
            teams[0].id: {'score': 100.0, 'points': 10}
        }

        ScoreService.save_scores(game.id, scores_data, is_completed=False)

        # Verify team total was updated
        db_session.refresh(teams[0])
        assert teams[0].totalPoints == original_points + 10

    def test_save_scores_with_only_points(self, db_session, game, teams):
        """Test saving scores with only points (no score value)."""
        scores_data = {
            teams[0].id: {'points': 5}
        }

        ScoreService.save_scores(game.id, scores_data, is_completed=False)

        score = Score.query.filter_by(game_id=game.id, team_id=teams[0].id).first()
        assert score is not None
        assert score.points == 5
        assert score.score_value is None

    def test_save_scores_with_only_score(self, db_session, game, teams):
        """Test saving scores with only score value (no points)."""
        scores_data = {
            teams[0].id: {'score': 100.0}
        }

        ScoreService.save_scores(game.id, scores_data, is_completed=False)

        score = Score.query.filter_by(game_id=game.id, team_id=teams[0].id).first()
        assert score is not None
        assert score.score_value == 100.0

    def test_save_scores_with_notes(self, db_session, game, teams):
        """Test saving scores with notes."""
        scores_data = {
            teams[0].id: {
                'score': 100.0,
                'points': 3,
                'notes': 'Excellent performance'
            }
        }

        ScoreService.save_scores(game.id, scores_data, is_completed=False)

        score = Score.query.filter_by(game_id=game.id, team_id=teams[0].id).first()
        assert score.notes == 'Excellent performance'

    def test_save_scores_empty_data(self, db_session, game):
        """Test saving with empty scores data."""
        ScoreService.save_scores(game.id, {}, is_completed=False)

        # Should not create any scores
        scores = Score.query.filter_by(game_id=game.id).all()
        assert len(scores) == 0

    def test_calculate_points_higher_better(self, db_session, game_night, teams):
        """Test automatic point calculation for higher_better games."""
        game = Game(
            name='Higher Better Game',
            type='standard',
            sequence_number=1,
            game_night_id=game_night.id,
            point_scheme=1,  # Standard scheme
            metric_type='score',
            scoring_direction='higher_better'
        )
        db_session.add(game)
        db_session.commit()

        # Save scores - higher score should get more points
        scores_data = {
            teams[0].id: {'score': 100.0},
            teams[1].id: {'score': 90.0},
            teams[2].id: {'score': 80.0}
        }

        ScoreService.save_scores(game.id, scores_data, is_completed=False)

        # Verify points were calculated correctly
        score1 = Score.query.filter_by(game_id=game.id, team_id=teams[0].id).first()
        score2 = Score.query.filter_by(game_id=game.id, team_id=teams[1].id).first()
        score3 = Score.query.filter_by(game_id=game.id, team_id=teams[2].id).first()

        # Higher scores should get more points
        assert score1.points >= score2.points
        assert score2.points >= score3.points

    def test_calculate_points_lower_better(self, db_session, game_night, teams):
        """Test automatic point calculation for lower_better games."""
        game = Game(
            name='Lower Better Game',
            type='standard',
            sequence_number=1,
            game_night_id=game_night.id,
            point_scheme=1,
            metric_type='time',
            scoring_direction='lower_better'
        )
        db_session.add(game)
        db_session.commit()

        # Save scores - lower score should get more points
        scores_data = {
            teams[0].id: {'score': 60.0},
            teams[1].id: {'score': 70.0},
            teams[2].id: {'score': 80.0}
        }

        ScoreService.save_scores(game.id, scores_data, is_completed=False)

        # Verify points were calculated correctly
        score1 = Score.query.filter_by(game_id=game.id, team_id=teams[0].id).first()
        score2 = Score.query.filter_by(game_id=game.id, team_id=teams[1].id).first()
        score3 = Score.query.filter_by(game_id=game.id, team_id=teams[2].id).first()

        # Lower scores should get more points
        assert score1.points >= score2.points
        assert score2.points >= score3.points
