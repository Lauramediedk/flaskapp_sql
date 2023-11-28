from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length

#Vores registrerings form som bruger wtforms
class SignupForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(
        min=2, max=12)], render_kw={"placeholder": "Navn"})

    email = StringField(validators=[InputRequired(), Length(
        min=2, max=20)], render_kw={"placeholder": "Email"})

    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Kodeord"})

    submit = SubmitField("Opret en bruger")