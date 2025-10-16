from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FieldList, FormField
from wtforms.validators import DataRequired, Regexp, Optional


class ParticipantForm(FlaskForm):
    firstName = StringField('First Name')
    lastName = StringField('Last Name')


class TeamForm(FlaskForm):
    name = StringField('Team Name', validators=[DataRequired()])
    color = StringField('Team Color', validators=[
        DataRequired(), Regexp(r'^#[0-9A-Fa-f]{6}$', message='Must be a valid hex color code')
    ], default='#3b82f6')

    # Keep individual fields for easier validation and backwards compatibility
    participant1FirstName = StringField('First Name', validators=[DataRequired()])
    participant1LastName = StringField('Last Name', validators=[DataRequired()])
    participant2FirstName = StringField('First Name', validators=[DataRequired()])
    participant2LastName = StringField('Last Name', validators=[DataRequired()])

    # Additional participants (optional)
    participant3FirstName = StringField('First Name', validators=[Optional()])
    participant3LastName = StringField('Last Name', validators=[Optional()])
    participant4FirstName = StringField('First Name', validators=[Optional()])
    participant4LastName = StringField('Last Name', validators=[Optional()])
    participant5FirstName = StringField('First Name', validators=[Optional()])
    participant5LastName = StringField('Last Name', validators=[Optional()])
    participant6FirstName = StringField('First Name', validators=[Optional()])
    participant6LastName = StringField('Last Name', validators=[Optional()])

    submit = SubmitField('Save Team')
