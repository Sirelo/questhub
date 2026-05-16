from __future__ import annotations

from app.models import Expedition, User
from app.repository import (
    average_user_streak,
    count_created_expeditions,
    count_user_checkins,
    count_user_participations,
    leaderboard_data,
    list_public_expeditions,
    sum_user_points,
)


def dashboard_stats(user: User) -> dict[str, int | float]:
    return {
        "created_count": count_created_expeditions(user.id),
        "active_count": count_user_participations(user.id, "active"),
        "completed_count": count_user_participations(user.id, "completed"),
        "total_checkins": count_user_checkins(user.id),
        "total_points": sum_user_points(user.id),
        "average_streak": average_user_streak(user.id),
    }


def leaderboard(limit: int = 10) -> list[dict[str, object]]:
    return leaderboard_data(limit)


def public_feed(limit: int = 6) -> list[Expedition]:
    return list_public_expeditions(limit=limit)
