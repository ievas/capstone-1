from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Email, Length



class TranslationForm(FlaskForm):
    """Form for entering a translation."""

    translation = TextAreaField('translation', validators=[DataRequired()])
    word = HiddenField("word")