from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField
from wtforms.validators import InputRequired, Length, Email

# Vores registrerings form som bruger wtforms


class SignupForm(FlaskForm):
    name = StringField(validators=[InputRequired(), Length(
        min=2, max=12)], render_kw={"placeholder": "Navn"})

    email = StringField('Email', validators=[InputRequired(), Email(), Length(
        min=4, max=20)], render_kw={"placeholder": "Email"})

    password = PasswordField(validators=[InputRequired(), Length(
        min=8, max=20)], render_kw={"placeholder": "Kodeord"})

    submit = SubmitField("Opret en bruger")

# Log ind form


class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Email"})

    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Kodeord"})
    # render_kw --> tilføj ekstra felt i ens html som placeholder eller en class

    submit = SubmitField("Log ind")

# Make post form


class PostForm(FlaskForm):
    content = StringField(validators=[InputRequired()])
    image_path = FileField(validators=[FileAllowed(
        ['jpg', 'png'], 'jpg og png format kun tilladt')])
    submit = SubmitField("Slå op")

# Fitness form


class FitnessForm(FlaskForm):
    distance = FloatField(validators=[InputRequired()], render_kw={
                          "placeholder": "Distance"})
    calories = IntegerField(validators=[InputRequired()], render_kw={
                            "placeholder": "Kalorier forbrændt"})
    submit = SubmitField("Tilføj data")
