from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class ProfileForm(FlaskForm):
    username = StringField("Логин", validators=[DataRequired(), Length(min=3, max=32)])
    city = StringField("Город", validators=[DataRequired(), Length(min=2, max=80)])
    bio = TextAreaField("О себе", validators=[Optional(), Length(max=300)])
    avatar = FileField(
        "Аватар",
        validators=[Optional(), FileAllowed(["png", "jpg", "jpeg", "gif", "webp"], "Только изображения.")],
    )
    submit = SubmitField("Сохранить профиль")
