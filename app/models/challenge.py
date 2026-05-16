from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from app.models.user import User


@dataclass
class Badge:
    id: int
    code: str
    title: str
    description: str
    icon: str = "*"


@dataclass
class UserBadge:
    id: int
    awarded_at: datetime
    reason: str
    user_id: int
    badge_id: int
    badge: Badge | None = None


@dataclass
class Expedition:
    id: int
    title: str
    summary: str
    description: str
    category: str
    difficulty: str
    city: str
    duration_days: int
    target_points: int
    is_public: bool
    cover_filename: str | None
    created_at: datetime
    updated_at: datetime
    creator_id: int
    creator: User | None = None
    participants_count: int = 0
    checkins_count: int = 0
    completion_rate: int = 0

    @property
    def cover_url(self) -> str:
        if self.cover_filename:
            return f"uploads/covers/{self.cover_filename}"
        return "https://placehold.co/1200x600?text=QuestHub"


@dataclass
class Participation:
    id: int
    joined_at: datetime
    status: str
    streak_days: int
    total_points: int
    last_checkin_date: date | None
    user_id: int
    expedition_id: int

    def can_check_in(self) -> bool:
        return self.last_checkin_date != date.today()

    def register_checkin(self, points: int, target_points: int) -> None:
        today = date.today()
        if self.last_checkin_date == today:
            raise ValueError("Вы уже отметили прогресс сегодня.")

        yesterday = date.fromordinal(today.toordinal() - 1)
        if self.last_checkin_date == yesterday:
            self.streak_days += 1
        else:
            self.streak_days = 1

        self.last_checkin_date = today
        self.total_points += points
        if self.total_points >= target_points:
            self.status = "completed"


@dataclass
class CheckIn:
    id: int
    note: str
    mood: str
    proof_filename: str | None
    points_earned: int
    created_at: datetime
    checkin_day: date
    user_id: int
    expedition_id: int
    participation_id: int
    user: User | None = None

    @property
    def proof_url(self) -> str | None:
        if self.proof_filename:
            return f"uploads/proofs/{self.proof_filename}"
        return None


@dataclass
class Comment:
    id: int
    text: str
    created_at: datetime
    user_id: int
    expedition_id: int
    author: User | None = None
