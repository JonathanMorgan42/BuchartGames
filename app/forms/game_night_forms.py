"""Forms for game night management."""
from flask_wtf import FlaskForm
from wtforms import StringField, DateField
from wtforms.validators import DataRequired, Length
from datetime import date


class GameNightForm(FlaskForm):
    """Form for creating/editing game nights."""

    name = StringField(
        'Game Night Name',
        validators=[
            DataRequired(message='Name is required'),
            Length(min=3, max=200, message='Name must be between 3 and 200 characters')
        ],
        render_kw={'placeholder': 'e.g., Epic Game Night, Summer Championship'}
    )

    date = DateField(
        'Date',
        validators=[DataRequired(message='Date is required')],
        default=date.today,
        format='%Y-%m-%d',
        render_kw={'type': 'date'}
    )
