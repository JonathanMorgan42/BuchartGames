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
            ('strategy', 'Strategy'),
            ('custom', 'Custom Type...')
        ],
        validators=[DataRequired()]
    )
    custom_type = StringField('Custom Game Type', validators=[])
    sequence_number = IntegerField(
        'Game Sequence Number',
        validators=[DataRequired()],
        default=0
    )
    point_scheme = IntegerField(
        'Point Multiplier',
        validators=[DataRequired(), NumberRange(min=1, max=100, message='Multiplier must be between 1 and 100')],
        default=1
    )
    metric_type = SelectField(
        'Scoring Method',
        choices=[
            ('score', 'Score Input'),
            ('time', 'Time (Stopwatch)')
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