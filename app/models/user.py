from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash


@dataclass
class User(UserMixin):
    id: int
    username: str
    email: str
    password_hash: str
    city: str
    bio: str
    avatar_filename: str | None
    created_at: datetime
    last_seen: datetime

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def avatar_url(self) -> str:
        if self.avatar_filename:
            return f"uploads/avatars/{self.avatar_filename}"
        return "https://placehold.co/240x240?text=QuestHub"
