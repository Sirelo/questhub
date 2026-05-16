from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (
    BooleanField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional


IMAGE_EXTENSIONS = ["png", "jpg", "jpeg", "gif", "webp"]


class ExpeditionForm(FlaskForm):
    title = StringField("Название", validators=[DataRequired(), Length(min=5, max=120)])
    summary = StringField("Краткое описание", validators=[DataRequired(), Length(min=10, max=200)])
    description = TextAreaField("Подробное описание", validators=[DataRequired(), Length(min=30, max=3000)])
    category = SelectField(
        "Категория",
        choices=[
            ("photo", "Фото"),
            ("study", "Учёба"),
            ("fitness", "Активность"),
            ("eco", "Экология"),
            ("creative", "Творчество"),
            ("city", "Город"),
        ],
        validators=[DataRequired()],
    )
    difficulty = SelectField(
        "Сложность",
        choices=[("easy", "Лёгкий"), ("medium", "Средний"), ("hard", "Сложный")],
        validators=[DataRequired()],
    )
    city = StringField("Город", validators=[DataRequired(), Length(min=2, max=80)])
    duration_days = IntegerField("Длительность", validators=[DataRequired(), NumberRange(min=3, max=90)])
    target_points = IntegerField("Цель в баллах", validators=[DataRequired(), NumberRange(min=20, max=1000)])
    is_public = BooleanField("Показывать в общей ленте", default=True)
    cover = FileField("Обложка", validators=[Optional(), FileAllowed(IMAGE_EXTENSIONS, "Только изображения.")])
    submit = SubmitField("Сохранить")


class CheckInForm(FlaskForm):
    note = TextAreaField("Что удалось сделать сегодня", validators=[DataRequired(), Length(min=10, max=500)])
    mood = SelectField(
        "Состояние",
        choices=[
            ("energized", "Есть энергия"),
            ("focused", "Удалось сосредоточиться"),
            ("steady", "Иду в темпе"),
            ("tired", "Было тяжело, но я справился"),
        ],
        validators=[DataRequired()],
    )
    proof = FileField("Фото-доказательство", validators=[Optional(), FileAllowed(IMAGE_EXTENSIONS, "Только изображения.")])
    submit = SubmitField("Отметить прогресс")


class CommentForm(FlaskForm):
    text = TextAreaField("Комментарий", validators=[DataRequired(), Length(min=2, max=300)])
    submit = SubmitField("Отправить")
