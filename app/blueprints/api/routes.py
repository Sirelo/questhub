from flask import Blueprint, abort, jsonify

from app.repository import get_expedition_by_id, get_user_by_id, list_user_badges
from app.services.stats_service import dashboard_stats, leaderboard, public_feed


api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.get("/expeditions")
def expeditions_api():
    expeditions = public_feed(limit=1000)
    return jsonify(
        [
            {
                "id": expedition.id,
                "title": expedition.title,
                "summary": expedition.summary,
                "category": expedition.category,
                "difficulty": expedition.difficulty,
                "city": expedition.city,
                "duration_days": expedition.duration_days,
                "target_points": expedition.target_points,
                "participants_count": expedition.participants_count,
                "completion_rate": expedition.completion_rate,
            }
            for expedition in expeditions
        ]
    )


@api_bp.get("/expeditions/<int:expedition_id>")
def expedition_api(expedition_id: int):
    expedition = get_expedition_by_id(expedition_id)
    if expedition is None:
        abort(404)

    return jsonify(
        {
            "id": expedition.id,
            "title": expedition.title,
            "summary": expedition.summary,
            "description": expedition.description,
            "category": expedition.category,
            "difficulty": expedition.difficulty,
            "city": expedition.city,
            "duration_days": expedition.duration_days,
            "target_points": expedition.target_points,
            "creator": expedition.creator.username if expedition.creator else "",
            "participants_count": expedition.participants_count,
            "checkins_count": expedition.checkins_count,
            "completion_rate": expedition.completion_rate,
        }
    )


@api_bp.get("/users/<int:user_id>/stats")
def user_stats_api(user_id: int):
    user = get_user_by_id(user_id)
    if user is None:
        abort(404)

    stats = dashboard_stats(user)
    stats["username"] = user.username
    stats["badges"] = [
        {
            "title": item.badge.title,
            "icon": item.badge.icon,
            "reason": item.reason,
        }
        for item in list_user_badges(user.id)
    ]
    return jsonify(stats)


@api_bp.get("/leaderboard")
def leaderboard_api():
    return jsonify(
        [
            {
                "position": row["position"],
                "username": row["user"].username,
                "points": row["points"],
                "best_streak": row["best_streak"],
                "checkins": row["checkins"],
            }
            for row in leaderboard(20)
        ]
    )
