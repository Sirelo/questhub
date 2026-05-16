from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.forms.challenge import CheckInForm, CommentForm, ExpeditionForm
from app.repository import (
    add_comment,
    create_expedition as create_expedition_record,
    create_participation,
    delete_participation,
    find_participation,
    get_expedition_by_id,
    list_comments,
    list_public_expeditions,
    list_recent_checkins,
    save_checkin,
    update_expedition,
)
from app.services.badge_service import evaluate_user_badges
from app.services.upload_service import save_image


challenges_bp = Blueprint("challenges", __name__, url_prefix="/expeditions")


@challenges_bp.route("/")
def list_expeditions():
    expeditions = list_public_expeditions(
        search=request.args.get("search", "").strip(),
        category=request.args.get("category", "").strip(),
        difficulty=request.args.get("difficulty", "").strip(),
        city=request.args.get("city", "").strip(),
    )
    return render_template("challenges/list.html", expeditions=expeditions)


@challenges_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_expedition():
    form = ExpeditionForm()
    if form.validate_on_submit():
        cover_filename = None
        if form.cover.data:
            try:
                cover_filename = save_image(form.cover.data, "covers")
            except (OSError, ValueError):
                flash("Не удалось обработать обложку.", "danger")
                return render_template("challenges/form.html", form=form, title="Новая экспедиция")

        expedition_id = create_expedition_record(
            title=form.title.data.strip(),
            summary=form.summary.data.strip(),
            description=form.description.data.strip(),
            category=form.category.data,
            difficulty=form.difficulty.data,
            city=form.city.data.strip(),
            duration_days=form.duration_days.data,
            target_points=form.target_points.data,
            is_public=form.is_public.data,
            creator_id=current_user.id,
            cover_filename=cover_filename,
        )
        evaluate_user_badges(current_user)
        flash("Экспедиция создана.", "success")
        return redirect(url_for("challenges.expedition_detail", expedition_id=expedition_id))

    return render_template("challenges/form.html", form=form, title="Новая экспедиция")


@challenges_bp.route("/<int:expedition_id>", methods=["GET", "POST"])
def expedition_detail(expedition_id: int):
    expedition = get_expedition_by_id(expedition_id)
    if expedition is None:
        abort(404)

    comment_form = CommentForm()
    participation = None
    checkin_form = None

    if current_user.is_authenticated:
        participation = find_participation(current_user.id, expedition.id)
        if participation:
            checkin_form = CheckInForm()

    if current_user.is_authenticated and comment_form.validate_on_submit():
        add_comment(current_user.id, expedition.id, comment_form.text.data.strip())
        flash("Комментарий добавлен.", "success")
        return redirect(url_for("challenges.expedition_detail", expedition_id=expedition.id))

    return render_template(
        "challenges/detail.html",
        expedition=expedition,
        comment_form=comment_form,
        checkin_form=checkin_form,
        participation=participation,
        recent_checkins=list_recent_checkins(expedition.id, 6),
        comments=list_comments(expedition.id),
    )


@challenges_bp.route("/<int:expedition_id>/edit", methods=["GET", "POST"])
@login_required
def edit_expedition(expedition_id: int):
    expedition = get_expedition_by_id(expedition_id)
    if expedition is None:
        abort(404)
    if expedition.creator_id != current_user.id:
        abort(403)

    form = ExpeditionForm(
        title=expedition.title,
        summary=expedition.summary,
        description=expedition.description,
        category=expedition.category,
        difficulty=expedition.difficulty,
        city=expedition.city,
        duration_days=expedition.duration_days,
        target_points=expedition.target_points,
        is_public=expedition.is_public,
    )
    if form.validate_on_submit():
        cover_filename = None
        if form.cover.data:
            try:
                cover_filename = save_image(form.cover.data, "covers")
            except (OSError, ValueError):
                flash("Не удалось обработать новую обложку.", "danger")
                return render_template("challenges/form.html", form=form, title="Редактирование экспедиции")

        update_expedition(
            expedition_id=expedition.id,
            title=form.title.data.strip(),
            summary=form.summary.data.strip(),
            description=form.description.data.strip(),
            category=form.category.data,
            difficulty=form.difficulty.data,
            city=form.city.data.strip(),
            duration_days=form.duration_days.data,
            target_points=form.target_points.data,
            is_public=form.is_public.data,
            cover_filename=cover_filename,
        )
        flash("Экспедиция обновлена.", "success")
        return redirect(url_for("challenges.expedition_detail", expedition_id=expedition.id))

    return render_template("challenges/form.html", form=form, title="Редактирование экспедиции")


@challenges_bp.route("/<int:expedition_id>/join", methods=["POST"])
@login_required
def join_expedition(expedition_id: int):
    expedition = get_expedition_by_id(expedition_id)
    if expedition is None:
        abort(404)

    if find_participation(current_user.id, expedition.id):
        flash("Вы уже участвуете в этой экспедиции.", "warning")
    else:
        create_participation(current_user.id, expedition.id)
        evaluate_user_badges(current_user)
        flash("Вы присоединились к экспедиции.", "success")
    return redirect(url_for("challenges.expedition_detail", expedition_id=expedition.id))


@challenges_bp.route("/<int:expedition_id>/leave", methods=["POST"])
@login_required
def leave_expedition(expedition_id: int):
    if find_participation(current_user.id, expedition_id) is None:
        abort(404)
    delete_participation(current_user.id, expedition_id)
    flash("Участие отменено.", "info")
    return redirect(url_for("challenges.list_expeditions"))


@challenges_bp.route("/<int:expedition_id>/checkin", methods=["POST"])
@login_required
def add_checkin(expedition_id: int):
    expedition = get_expedition_by_id(expedition_id)
    if expedition is None:
        abort(404)

    participation = find_participation(current_user.id, expedition.id)
    if participation is None:
        abort(404)

    form = CheckInForm()
    if not form.validate_on_submit():
        flash("Проверьте форму отметки прогресса.", "danger")
        return redirect(url_for("challenges.expedition_detail", expedition_id=expedition.id))

    if not participation.can_check_in():
        flash("Сегодня вы уже отмечали прогресс.", "warning")
        return redirect(url_for("challenges.expedition_detail", expedition_id=expedition.id))

    proof_filename = None
    if form.proof.data:
        try:
            proof_filename = save_image(form.proof.data, "proofs")
        except (OSError, ValueError):
            flash("Не удалось обработать файл доказательства.", "danger")
            return redirect(url_for("challenges.expedition_detail", expedition_id=expedition.id))

    points = 10 if expedition.difficulty == "easy" else 15 if expedition.difficulty == "medium" else 20
    save_checkin(
        participation=participation,
        expedition=expedition,
        user_id=current_user.id,
        note=form.note.data.strip(),
        mood=form.mood.data,
        proof_filename=proof_filename,
        points=points,
    )
    evaluate_user_badges(current_user)
    flash("Прогресс сохранен.", "success")
    return redirect(url_for("challenges.expedition_detail", expedition_id=expedition.id))
