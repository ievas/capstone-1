from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, HiddenField
from wtforms.validators import InputRequired, Email, Length




class TranslationForm(FlaskForm):
    """Form for entering a translation."""

    translation = TextAreaField('Translation', validators=[InputRequired()])
    word = HiddenField("word")

class RegisterForm(FlaskForm):
    """Register a new user."""

    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[Length(min=5)])
    first_name = StringField('Firstname', validators=[InputRequired()])
    last_name = StringField('Lastname', validators=[InputRequired()])
    email = StringField('E-mail', validators=[InputRequired(), Email()])
    


class SignInForm(FlaskForm):
    """Sign in."""
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[Length(min=5)])