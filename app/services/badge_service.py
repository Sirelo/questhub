from __future__ import annotations

from app.models import User
from app.repository import (
    award_badge,
    count_created_expeditions,
    count_user_participations,
    find_badge_by_code,
    list_user_participations,
    sum_user_points,
    user_has_badge,
)


BADGE_RULES = {
    "first_expedition": "Создана первая экспедиция.",
    "first_join": "Первое участие в чужой экспедиции.",
    "streak_3": "Серия из 3 дней подряд.",
    "streak_7": "Серия из 7 дней подряд.",
    "points_100": "Набрано 100 баллов прогресса.",
    "mentor": "Создано 3 экспедиции.",
}


def ensure_badge(user: User, code: str) -> None:
    badge = find_badge_by_code(code)
    if badge is None or user_has_badge(user.id, code):
        return
    award_badge(user.id, badge.id, BADGE_RULES[code])


def evaluate_user_badges(user: User) -> None:
    participations = list_user_participations(user.id)
    if count_created_expeditions(user.id) >= 1:
        ensure_badge(user, "first_expedition")
    if count_created_expeditions(user.id) >= 3:
        ensure_badge(user, "mentor")
    if count_user_participations(user.id) >= 1:
        ensure_badge(user, "first_join")
    if any(item.streak_days >= 3 for item in participations):
        ensure_badge(user, "streak_3")
    if any(item.streak_days >= 7 for item in participations):
        ensure_badge(user, "streak_7")
    if sum_user_points(user.id) >= 100:
        ensure_badge(user, "points_100")
