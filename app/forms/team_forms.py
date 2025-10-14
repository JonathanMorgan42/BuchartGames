"""Team forms."""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp


class TeamForm(FlaskForm):
    """Team form."""
    name = StringField('Team Name', validators=[DataRequired()])
    color = StringField('Team Color', validators=[
        DataRequired(), Regexp(r'^#[0-9A-Fa-f]{6}$', message='Must be a valid hex color code')
    ], default='#3b82f6')
    participant1FirstName = StringField('First Name', validators=[DataRequired()])
    participant1LastName = StringField('Last Name', validators=[DataRequired()])
    participant2FirstName = StringField('First Name', validators=[DataRequired()])
    participant2LastName = StringField('Last Name', validators=[DataRequired()])
    submit = SubmitField('Save Team')
