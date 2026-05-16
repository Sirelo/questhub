from flask import Blueprint, render_template
from flask_login import current_user, login_required

from app.repository import list_owned_expeditions, list_user_badges
from app.services.stats_service import dashboard_stats, leaderboard, public_feed


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("index.html", featured_expeditions=public_feed())


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template(
        "dashboard.html",
        stats=dashboard_stats(current_user),
        leaderboard_rows=leaderboard(5),
        owned_expeditions=list_owned_expeditions(current_user.id, limit=4),
        user_badges=list_user_badges(current_user.id),
    )


@main_bp.route("/leaderboard")
def leaderboard_page():
    return render_template("leaderboard.html", leaderboard_rows=leaderboard(20))
