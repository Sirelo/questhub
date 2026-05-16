from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegistrationForm(FlaskForm):
    username = StringField(
        "Логин",
        validators=[DataRequired(), Length(min=3, max=32)],
    )
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    city = StringField("Город", validators=[DataRequired(), Length(min=2, max=80)])
    password = PasswordField(
        "Пароль",
        validators=[DataRequired(), Length(min=6, max=64)],
    )
    confirm_password = PasswordField(
        "Повторите пароль",
        validators=[DataRequired(), EqualTo("password")],
    )
    bio = TextAreaField("О себе", validators=[Length(max=300)])
    submit = SubmitField("Создать аккаунт")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    submit = SubmitField("Войти")
