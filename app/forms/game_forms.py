"""Game management forms."""
from flask_wtf import FlaskForm
from wtforms import (
    StringField, SelectField, IntegerField,
    BooleanField, SubmitField, TextAreaField
)
from wtforms.validators import DataRequired, NumberRange


class GameForm(FlaskForm):
    """Game creation/editing form."""
    name = StringField('Game Name', validators=[DataRequired()])
    type = SelectField(
        'Game Type',
        choices=[
            ('trivia', 'Trivia'),
            ('physical', 'Physical Challenge'),
            ('strategy', 'Strategy')
        ],
        validators=[DataRequired()]
    )
    sequence_number = IntegerField(
        'Game Sequence Number',
        validators=[DataRequired()],
        default=0
    )
    point_scheme = SelectField(
        'Points Distribution',
        choices=[
            (1, 'Standard (1, 2, 3, 4, 5, 6...)'),
            (2, 'Double (2, 4, 6, 8, 10, 12...)'),
            (4, 'Quadruple (4, 8, 12, 16, 20, 24...)')
        ],
        validators=[DataRequired()],
        coerce=int
    )
    metric_type = SelectField(
        'Scoring Method',
        choices=[
            ('manual', 'Manual Score Input'),
            ('time', 'Time (Stopwatch)'),
            ('count', 'Counter')
        ],
        validators=[DataRequired()]
    )
    scoring_direction = SelectField(
        'Scoring Direction',
        choices=[
            ('lower_better', 'Lower is Better (e.g., time-based)'),
            ('higher_better', 'Higher is Better (e.g., points-based)')
        ],
        validators=[DataRequired()],
        default='lower_better'
    )
    public_input = BooleanField('Allow Public Score Input', default=False)
    submit = SubmitField('Save Game')


class LiveScoringForm(FlaskForm):
    """Live scoring form."""
    game_id = StringField('Game ID', validators=[DataRequired()])
    game_notes = TextAreaField('Game Notes')
    is_completed = BooleanField('Mark game as completed', default=True)
    submit = SubmitField('Save Final Scores')