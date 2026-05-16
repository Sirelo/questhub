from __future__ import annotations

import sqlite3
from pathlib import Path

from flask import current_app, g


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    city TEXT NOT NULL DEFAULT 'Не указан',
    bio TEXT NOT NULL DEFAULT '',
    avatar_filename TEXT,
    created_at TEXT NOT NULL,
    last_seen TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS expeditions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    summary TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    city TEXT NOT NULL,
    duration_days INTEGER NOT NULL DEFAULT 7,
    target_points INTEGER NOT NULL DEFAULT 50,
    is_public INTEGER NOT NULL DEFAULT 1,
    cover_filename TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    creator_id INTEGER NOT NULL,
    FOREIGN KEY (creator_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS participations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    joined_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    streak_days INTEGER NOT NULL DEFAULT 0,
    total_points INTEGER NOT NULL DEFAULT 0,
    last_checkin_date TEXT,
    user_id INTEGER NOT NULL,
    expedition_id INTEGER NOT NULL,
    UNIQUE(user_id, expedition_id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (expedition_id) REFERENCES expeditions (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS checkins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    note TEXT NOT NULL,
    mood TEXT NOT NULL DEFAULT 'energized',
    proof_filename TEXT,
    points_earned INTEGER NOT NULL DEFAULT 10,
    created_at TEXT NOT NULL,
    checkin_day TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    expedition_id INTEGER NOT NULL,
    participation_id INTEGER NOT NULL,
    UNIQUE(participation_id, checkin_day),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (expedition_id) REFERENCES expeditions (id) ON DELETE CASCADE,
    FOREIGN KEY (participation_id) REFERENCES participations (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    created_at TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    expedition_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (expedition_id) REFERENCES expeditions (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    icon TEXT NOT NULL DEFAULT '*'
);

CREATE TABLE IF NOT EXISTS user_badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    awarded_at TEXT NOT NULL,
    reason TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    badge_id INTEGER NOT NULL,
    UNIQUE(user_id, badge_id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    FOREIGN KEY (badge_id) REFERENCES badges (id) ON DELETE CASCADE
);
"""


def init_app(app) -> None:
    app.teardown_appcontext(close_db)


def get_db() -> sqlite3.Connection:
    if "db_conn" not in g:
        database_path = Path(current_app.config["DATABASE_PATH"])
        database_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(database_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.db_conn = conn
    return g.db_conn


def close_db(_error=None) -> None:
    conn = g.pop("db_conn", None)
    if conn is not None:
        conn.close()


def init_db() -> None:
    conn = get_db()
    conn.executescript(SCHEMA_SQL)
    conn.commit()
