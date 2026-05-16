from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import generate_password_hash

from app.forms.auth import LoginForm, RegistrationForm
from app.forms.profile import ProfileForm
from app.repository import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    list_user_badges,
    update_user_last_seen,
    update_user_profile,
)
from app.services.badge_service import evaluate_user_badges
from app.services.upload_service import save_image


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.before_app_request
def touch_last_seen() -> None:
    if current_user.is_authenticated:
        update_user_last_seen(current_user.id)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegistrationForm()
    if form.validate_on_submit():
        if get_user_by_email(form.email.data.strip().lower()):
            flash("Пользователь с таким email уже существует.", "danger")
        elif get_user_by_username(form.username.data.strip()):
            flash("Такой логин уже занят.", "danger")
        else:
            user_id = create_user(
                username=form.username.data.strip(),
                email=form.email.data.strip().lower(),
                city=form.city.data.strip(),
                bio=(form.bio.data or "").strip(),
                password_hash=generate_password_hash(form.password.data),
            )
            evaluate_user_badges(get_user_by_id(user_id))
            flash("Аккаунт создан. Теперь войдите.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = get_user_by_email(form.email.data.strip().lower())
        if user is None or not user.check_password(form.password.data):
            flash("Неверный email или пароль.", "danger")
        else:
            login_user(user)
            flash("Вы вошли в аккаунт.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.dashboard"))

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = ProfileForm(
        username=current_user.username,
        city=current_user.city,
        bio=current_user.bio,
    )
    if form.validate_on_submit():
        duplicate_user = get_user_by_username(form.username.data.strip())
        if duplicate_user and duplicate_user.id != current_user.id:
            flash("Такой логин уже используется.", "danger")
        else:
            avatar_filename = None
            if form.avatar.data:
                try:
                    avatar_filename = save_image(form.avatar.data, "avatars")
                except (OSError, ValueError):
                    flash("Не удалось обработать аватар.", "danger")
                    return render_template(
                        "profile.html",
                        form=form,
                        user_badges=list_user_badges(current_user.id),
                    )

            update_user_profile(
                user_id=current_user.id,
                username=form.username.data.strip(),
                city=form.city.data.strip(),
                bio=(form.bio.data or "").strip(),
                avatar_filename=avatar_filename,
            )
            refreshed_user = get_user_by_id(current_user.id)
            evaluate_user_badges(refreshed_user)
            flash("Профиль обновлен.", "success")
            return redirect(url_for("auth.profile"))

    return render_template(
        "profile.html",
        form=form,
        user_badges=list_user_badges(current_user.id),
    )
