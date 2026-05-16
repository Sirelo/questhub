from __future__ import annotations

from datetime import date, datetime
from sqlite3 import Row

from app.database import get_db
from app.models import Badge, CheckIn, Comment, Expedition, Participation, User, UserBadge


def now_text() -> str:
    return datetime.now().isoformat(sep=" ", timespec="seconds")


def parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.now()
    return datetime.fromisoformat(value)


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def user_from_row(row: Row, prefix: str = "") -> User:
    return User(
        id=row[f"{prefix}id"],
        username=row[f"{prefix}username"],
        email=row[f"{prefix}email"],
        password_hash=row[f"{prefix}password_hash"],
        city=row[f"{prefix}city"],
        bio=row[f"{prefix}bio"],
        avatar_filename=row[f"{prefix}avatar_filename"],
        created_at=parse_datetime(row[f"{prefix}created_at"]),
        last_seen=parse_datetime(row[f"{prefix}last_seen"]),
    )


def badge_from_row(row: Row, prefix: str = "") -> Badge:
    return Badge(
        id=row[f"{prefix}id"],
        code=row[f"{prefix}code"],
        title=row[f"{prefix}title"],
        description=row[f"{prefix}description"],
        icon=row[f"{prefix}icon"],
    )


def expedition_from_row(row: Row, prefix: str = "") -> Expedition:
    creator = None
    if f"{prefix}creator_username" in row.keys():
        creator = User(
            id=row[f"{prefix}creator_id"],
            username=row[f"{prefix}creator_username"],
            email=row[f"{prefix}creator_email"],
            password_hash=row[f"{prefix}creator_password_hash"],
            city=row[f"{prefix}creator_city"],
            bio=row[f"{prefix}creator_bio"],
            avatar_filename=row[f"{prefix}creator_avatar_filename"],
            created_at=parse_datetime(row[f"{prefix}creator_created_at"]),
            last_seen=parse_datetime(row[f"{prefix}creator_last_seen"]),
        )

    return Expedition(
        id=row[f"{prefix}id"],
        title=row[f"{prefix}title"],
        summary=row[f"{prefix}summary"],
        description=row[f"{prefix}description"],
        category=row[f"{prefix}category"],
        difficulty=row[f"{prefix}difficulty"],
        city=row[f"{prefix}city"],
        duration_days=row[f"{prefix}duration_days"],
        target_points=row[f"{prefix}target_points"],
        is_public=bool(row[f"{prefix}is_public"]),
        cover_filename=row[f"{prefix}cover_filename"],
        created_at=parse_datetime(row[f"{prefix}created_at"]),
        updated_at=parse_datetime(row[f"{prefix}updated_at"]),
        creator_id=row[f"{prefix}creator_id"],
        creator=creator,
        participants_count=row[f"{prefix}participants_count"] if f"{prefix}participants_count" in row.keys() else 0,
        checkins_count=row[f"{prefix}checkins_count"] if f"{prefix}checkins_count" in row.keys() else 0,
        completion_rate=row[f"{prefix}completion_rate"] if f"{prefix}completion_rate" in row.keys() else 0,
    )


def participation_from_row(row: Row, prefix: str = "") -> Participation:
    return Participation(
        id=row[f"{prefix}id"],
        joined_at=parse_datetime(row[f"{prefix}joined_at"]),
        status=row[f"{prefix}status"],
        streak_days=row[f"{prefix}streak_days"],
        total_points=row[f"{prefix}total_points"],
        last_checkin_date=parse_date(row[f"{prefix}last_checkin_date"]),
        user_id=row[f"{prefix}user_id"],
        expedition_id=row[f"{prefix}expedition_id"],
    )


def comment_from_row(row: Row) -> Comment:
    author = User(
        id=row["user_id"],
        username=row["username"],
        email=row["email"],
        password_hash=row["password_hash"],
        city=row["city"],
        bio=row["bio"],
        avatar_filename=row["avatar_filename"],
        created_at=parse_datetime(row["user_created_at"]),
        last_seen=parse_datetime(row["last_seen"]),
    )
    return Comment(
        id=row["id"],
        text=row["text"],
        created_at=parse_datetime(row["created_at"]),
        user_id=row["user_id"],
        expedition_id=row["expedition_id"],
        author=author,
    )


def checkin_from_row(row: Row) -> CheckIn:
    user = User(
        id=row["user_id"],
        username=row["username"],
        email=row["email"],
        password_hash=row["password_hash"],
        city=row["city"],
        bio=row["bio"],
        avatar_filename=row["avatar_filename"],
        created_at=parse_datetime(row["user_created_at"]),
        last_seen=parse_datetime(row["last_seen"]),
    )
    return CheckIn(
        id=row["id"],
        note=row["note"],
        mood=row["mood"],
        proof_filename=row["proof_filename"],
        points_earned=row["points_earned"],
        created_at=parse_datetime(row["created_at"]),
        checkin_day=parse_date(row["checkin_day"]) or date.today(),
        user_id=row["user_id"],
        expedition_id=row["expedition_id"],
        participation_id=row["participation_id"],
        user=user,
    )


def user_badge_from_row(row: Row) -> UserBadge:
    badge = Badge(
        id=row["badge_id"],
        code=row["code"],
        title=row["title"],
        description=row["description"],
        icon=row["icon"],
    )
    return UserBadge(
        id=row["id"],
        awarded_at=parse_datetime(row["awarded_at"]),
        reason=row["reason"],
        user_id=row["user_id"],
        badge_id=row["badge_id"],
        badge=badge,
    )


def create_user(username: str, email: str, city: str, bio: str, password_hash: str) -> int:
    conn = get_db()
    now = now_text()
    cursor = conn.execute(
        """
        INSERT INTO users (username, email, password_hash, city, bio, avatar_filename, created_at, last_seen)
        VALUES (?, ?, ?, ?, ?, NULL, ?, ?)
        """,
        (username, email, password_hash, city, bio, now, now),
    )
    conn.commit()
    return cursor.lastrowid


def update_user_last_seen(user_id: int) -> None:
    conn = get_db()
    conn.execute("UPDATE users SET last_seen = ? WHERE id = ?", (now_text(), user_id))
    conn.commit()


def update_user_profile(user_id: int, username: str, city: str, bio: str, avatar_filename: str | None = None) -> None:
    conn = get_db()
    if avatar_filename is None:
        conn.execute(
            "UPDATE users SET username = ?, city = ?, bio = ? WHERE id = ?",
            (username, city, bio, user_id),
        )
    else:
        conn.execute(
            "UPDATE users SET username = ?, city = ?, bio = ?, avatar_filename = ? WHERE id = ?",
            (username, city, bio, avatar_filename, user_id),
        )
    conn.commit()


def get_user_by_id(user_id: int) -> User | None:
    row = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return user_from_row(row) if row else None


def get_user_by_email(email: str) -> User | None:
    row = get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    return user_from_row(row) if row else None


def get_user_by_username(username: str) -> User | None:
    row = get_db().execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    return user_from_row(row) if row else None


def list_users() -> list[User]:
    rows = get_db().execute("SELECT * FROM users ORDER BY username").fetchall()
    return [user_from_row(row) for row in rows]


def count_created_expeditions(user_id: int) -> int:
    row = get_db().execute("SELECT COUNT(*) AS count FROM expeditions WHERE creator_id = ?", (user_id,)).fetchone()
    return int(row["count"])


def count_user_participations(user_id: int, status: str | None = None) -> int:
    if status is None:
        row = get_db().execute("SELECT COUNT(*) AS count FROM participations WHERE user_id = ?", (user_id,)).fetchone()
    else:
        row = get_db().execute(
            "SELECT COUNT(*) AS count FROM participations WHERE user_id = ? AND status = ?",
            (user_id, status),
        ).fetchone()
    return int(row["count"])


def count_user_checkins(user_id: int) -> int:
    row = get_db().execute("SELECT COUNT(*) AS count FROM checkins WHERE user_id = ?", (user_id,)).fetchone()
    return int(row["count"])


def sum_user_points(user_id: int) -> int:
    row = get_db().execute(
        "SELECT COALESCE(SUM(total_points), 0) AS points FROM participations WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    return int(row["points"])


def average_user_streak(user_id: int) -> float:
    row = get_db().execute(
        "SELECT AVG(streak_days) AS average_streak FROM participations WHERE user_id = ?",
        (user_id,),
    ).fetchone()
    return round(float(row["average_streak"] or 0), 1)


def list_user_participations(user_id: int) -> list[Participation]:
    rows = get_db().execute(
        "SELECT * FROM participations WHERE user_id = ? ORDER BY joined_at DESC",
        (user_id,),
    ).fetchall()
    return [participation_from_row(row) for row in rows]


def list_user_badges(user_id: int) -> list[UserBadge]:
    rows = get_db().execute(
        """
        SELECT ub.id, ub.awarded_at, ub.reason, ub.user_id, ub.badge_id,
               b.code, b.title, b.description, b.icon
        FROM user_badges ub
        JOIN badges b ON b.id = ub.badge_id
        WHERE ub.user_id = ?
        ORDER BY ub.awarded_at DESC
        """,
        (user_id,),
    ).fetchall()
    return [user_badge_from_row(row) for row in rows]


def user_has_badge(user_id: int, code: str) -> bool:
    row = get_db().execute(
        """
        SELECT 1
        FROM user_badges ub
        JOIN badges b ON b.id = ub.badge_id
        WHERE ub.user_id = ? AND b.code = ?
        LIMIT 1
        """,
        (user_id, code),
    ).fetchone()
    return row is not None


def find_badge_by_code(code: str) -> Badge | None:
    row = get_db().execute("SELECT * FROM badges WHERE code = ?", (code,)).fetchone()
    return badge_from_row(row) if row else None


def create_badge(code: str, title: str, description: str, icon: str) -> None:
    conn = get_db()
    conn.execute(
        "INSERT OR IGNORE INTO badges (code, title, description, icon) VALUES (?, ?, ?, ?)",
        (code, title, description, icon),
    )
    conn.commit()


def award_badge(user_id: int, badge_id: int, reason: str) -> None:
    conn = get_db()
    conn.execute(
        "INSERT OR IGNORE INTO user_badges (awarded_at, reason, user_id, badge_id) VALUES (?, ?, ?, ?)",
        (now_text(), reason, user_id, badge_id),
    )
    conn.commit()


def list_public_expeditions(
    limit: int | None = None,
    search: str = "",
    category: str = "",
    difficulty: str = "",
    city: str = "",
) -> list[Expedition]:
    sql = """
    SELECT e.*,
           u.id AS creator_id,
           u.username AS creator_username,
           u.email AS creator_email,
           u.password_hash AS creator_password_hash,
           u.city AS creator_city,
           u.bio AS creator_bio,
           u.avatar_filename AS creator_avatar_filename,
           u.created_at AS creator_created_at,
           u.last_seen AS creator_last_seen,
           (SELECT COUNT(*) FROM participations p WHERE p.expedition_id = e.id) AS participants_count,
           (SELECT COUNT(*) FROM checkins c WHERE c.expedition_id = e.id) AS checkins_count,
           COALESCE((
               SELECT ROUND(100.0 * SUM(CASE WHEN p.status = 'completed' THEN 1 ELSE 0 END) / COUNT(*))
               FROM participations p
               WHERE p.expedition_id = e.id
           ), 0) AS completion_rate
    FROM expeditions e
    JOIN users u ON u.id = e.creator_id
    WHERE e.is_public = 1
    """
    params: list[object] = []
    if search:
        like_value = f"%{search}%"
        sql += " AND (e.title LIKE ? OR e.summary LIKE ? OR e.description LIKE ?)"
        params.extend([like_value, like_value, like_value])
    if category:
        sql += " AND e.category = ?"
        params.append(category)
    if difficulty:
        sql += " AND e.difficulty = ?"
        params.append(difficulty)
    if city:
        sql += " AND e.city LIKE ?"
        params.append(f"%{city}%")
    sql += " ORDER BY e.created_at DESC"
    if limit is not None:
        sql += " LIMIT ?"
        params.append(limit)

    rows = get_db().execute(sql, params).fetchall()
    return [expedition_from_row(row) for row in rows]


def list_owned_expeditions(user_id: int, limit: int | None = None) -> list[Expedition]:
    sql = """
    SELECT e.*,
           (SELECT COUNT(*) FROM participations p WHERE p.expedition_id = e.id) AS participants_count,
           (SELECT COUNT(*) FROM checkins c WHERE c.expedition_id = e.id) AS checkins_count,
           0 AS completion_rate
    FROM expeditions e
    WHERE e.creator_id = ?
    ORDER BY e.created_at DESC
    """
    params: list[object] = [user_id]
    if limit is not None:
        sql += " LIMIT ?"
        params.append(limit)
    rows = get_db().execute(sql, params).fetchall()
    return [expedition_from_row(row) for row in rows]


def get_expedition_by_id(expedition_id: int) -> Expedition | None:
    row = get_db().execute(
        """
        SELECT e.*,
               u.id AS creator_id,
               u.username AS creator_username,
               u.email AS creator_email,
               u.password_hash AS creator_password_hash,
               u.city AS creator_city,
               u.bio AS creator_bio,
               u.avatar_filename AS creator_avatar_filename,
               u.created_at AS creator_created_at,
               u.last_seen AS creator_last_seen,
               (SELECT COUNT(*) FROM participations p WHERE p.expedition_id = e.id) AS participants_count,
               (SELECT COUNT(*) FROM checkins c WHERE c.expedition_id = e.id) AS checkins_count,
               COALESCE((
                   SELECT ROUND(100.0 * SUM(CASE WHEN p.status = 'completed' THEN 1 ELSE 0 END) / COUNT(*))
                   FROM participations p
                   WHERE p.expedition_id = e.id
               ), 0) AS completion_rate
        FROM expeditions e
        JOIN users u ON u.id = e.creator_id
        WHERE e.id = ?
        """,
        (expedition_id,),
    ).fetchone()
    return expedition_from_row(row) if row else None


def get_expedition_by_title(title: str) -> Expedition | None:
    row = get_db().execute(
        """
        SELECT e.*,
               u.id AS creator_id,
               u.username AS creator_username,
               u.email AS creator_email,
               u.password_hash AS creator_password_hash,
               u.city AS creator_city,
               u.bio AS creator_bio,
               u.avatar_filename AS creator_avatar_filename,
               u.created_at AS creator_created_at,
               u.last_seen AS creator_last_seen,
               (SELECT COUNT(*) FROM participations p WHERE p.expedition_id = e.id) AS participants_count,
               (SELECT COUNT(*) FROM checkins c WHERE c.expedition_id = e.id) AS checkins_count,
               COALESCE((
                   SELECT ROUND(100.0 * SUM(CASE WHEN p.status = 'completed' THEN 1 ELSE 0 END) / COUNT(*))
                   FROM participations p
                   WHERE p.expedition_id = e.id
               ), 0) AS completion_rate
        FROM expeditions e
        JOIN users u ON u.id = e.creator_id
        WHERE e.title = ?
        """,
        (title,),
    ).fetchone()
    return expedition_from_row(row) if row else None


def create_expedition(
    title: str,
    summary: str,
    description: str,
    category: str,
    difficulty: str,
    city: str,
    duration_days: int,
    target_points: int,
    is_public: bool,
    creator_id: int,
    cover_filename: str | None,
) -> int:
    conn = get_db()
    now = now_text()
    cursor = conn.execute(
        """
        INSERT INTO expeditions (
            title, summary, description, category, difficulty, city,
            duration_days, target_points, is_public, cover_filename,
            created_at, updated_at, creator_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            title,
            summary,
            description,
            category,
            difficulty,
            city,
            duration_days,
            target_points,
            int(is_public),
            cover_filename,
            now,
            now,
            creator_id,
        ),
    )
    conn.commit()
    return cursor.lastrowid


def update_expedition(
    expedition_id: int,
    title: str,
    summary: str,
    description: str,
    category: str,
    difficulty: str,
    city: str,
    duration_days: int,
    target_points: int,
    is_public: bool,
    cover_filename: str | None = None,
) -> None:
    conn = get_db()
    if cover_filename is None:
        conn.execute(
            """
            UPDATE expeditions
            SET title = ?, summary = ?, description = ?, category = ?, difficulty = ?,
                city = ?, duration_days = ?, target_points = ?, is_public = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                title,
                summary,
                description,
                category,
                difficulty,
                city,
                duration_days,
                target_points,
                int(is_public),
                now_text(),
                expedition_id,
            ),
        )
    else:
        conn.execute(
            """
            UPDATE expeditions
            SET title = ?, summary = ?, description = ?, category = ?, difficulty = ?,
                city = ?, duration_days = ?, target_points = ?, is_public = ?, cover_filename = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                title,
                summary,
                description,
                category,
                difficulty,
                city,
                duration_days,
                target_points,
                int(is_public),
                cover_filename,
                now_text(),
                expedition_id,
            ),
        )
    conn.commit()


def find_participation(user_id: int, expedition_id: int) -> Participation | None:
    row = get_db().execute(
        "SELECT * FROM participations WHERE user_id = ? AND expedition_id = ?",
        (user_id, expedition_id),
    ).fetchone()
    return participation_from_row(row) if row else None


def create_participation(user_id: int, expedition_id: int) -> int:
    conn = get_db()
    cursor = conn.execute(
        """
        INSERT INTO participations (joined_at, status, streak_days, total_points, last_checkin_date, user_id, expedition_id)
        VALUES (?, 'active', 0, 0, NULL, ?, ?)
        """,
        (now_text(), user_id, expedition_id),
    )
    conn.commit()
    return cursor.lastrowid


def update_participation_progress(
    participation_id: int,
    status: str,
    streak_days: int,
    total_points: int,
    last_checkin_date: str | None,
) -> None:
    conn = get_db()
    conn.execute(
        """
        UPDATE participations
        SET status = ?, streak_days = ?, total_points = ?, last_checkin_date = ?
        WHERE id = ?
        """,
        (status, streak_days, total_points, last_checkin_date, participation_id),
    )
    conn.commit()


def create_checkin_record(
    participation_id: int,
    user_id: int,
    expedition_id: int,
    note: str,
    mood: str,
    points_earned: int,
    checkin_day: str,
    proof_filename: str | None = None,
) -> None:
    conn = get_db()
    conn.execute(
        """
        INSERT INTO checkins (
            note, mood, proof_filename, points_earned, created_at, checkin_day,
            user_id, expedition_id, participation_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            note,
            mood,
            proof_filename,
            points_earned,
            f"{checkin_day} 18:00:00",
            checkin_day,
            user_id,
            expedition_id,
            participation_id,
        ),
    )
    conn.commit()


def delete_participation(user_id: int, expedition_id: int) -> None:
    conn = get_db()
    conn.execute("DELETE FROM participations WHERE user_id = ? AND expedition_id = ?", (user_id, expedition_id))
    conn.commit()


def add_comment(user_id: int, expedition_id: int, text: str) -> None:
    conn = get_db()
    conn.execute(
        "INSERT INTO comments (text, created_at, user_id, expedition_id) VALUES (?, ?, ?, ?)",
        (text, now_text(), user_id, expedition_id),
    )
    conn.commit()


def list_comments(expedition_id: int) -> list[Comment]:
    rows = get_db().execute(
        """
        SELECT c.*, u.username, u.email, u.password_hash, u.city, u.bio, u.avatar_filename,
               u.created_at AS user_created_at, u.last_seen
        FROM comments c
        JOIN users u ON u.id = c.user_id
        WHERE c.expedition_id = ?
        ORDER BY c.created_at DESC
        """,
        (expedition_id,),
    ).fetchall()
    return [comment_from_row(row) for row in rows]


def list_recent_checkins(expedition_id: int, limit: int = 6) -> list[CheckIn]:
    rows = get_db().execute(
        """
        SELECT c.*, u.username, u.email, u.password_hash, u.city, u.bio, u.avatar_filename,
               u.created_at AS user_created_at, u.last_seen
        FROM checkins c
        JOIN users u ON u.id = c.user_id
        WHERE c.expedition_id = ?
        ORDER BY c.created_at DESC
        LIMIT ?
        """,
        (expedition_id, limit),
    ).fetchall()
    return [checkin_from_row(row) for row in rows]


def save_checkin(participation: Participation, expedition: Expedition, user_id: int, note: str, mood: str, proof_filename: str | None, points: int) -> None:
    participation.register_checkin(points, expedition.target_points)
    conn = get_db()
    today = date.today().isoformat()
    created_at = now_text()
    conn.execute(
        """
        UPDATE participations
        SET status = ?, streak_days = ?, total_points = ?, last_checkin_date = ?
        WHERE id = ?
        """,
        (
            participation.status,
            participation.streak_days,
            participation.total_points,
            participation.last_checkin_date.isoformat() if participation.last_checkin_date else None,
            participation.id,
        ),
    )
    conn.execute(
        """
        INSERT INTO checkins (
            note, mood, proof_filename, points_earned, created_at, checkin_day,
            user_id, expedition_id, participation_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            note,
            mood,
            proof_filename,
            points,
            created_at,
            today,
            user_id,
            expedition.id,
            participation.id,
        ),
    )
    conn.commit()


def leaderboard_data(limit: int = 10) -> list[dict[str, object]]:
    rows = get_db().execute(
        """
        SELECT u.*,
               COALESCE(SUM(p.total_points), 0) AS points,
               COALESCE(MAX(p.streak_days), 0) AS best_streak,
               (SELECT COUNT(*) FROM checkins c WHERE c.user_id = u.id) AS checkins
        FROM users u
        LEFT JOIN participations p ON p.user_id = u.id
        GROUP BY u.id
        ORDER BY points DESC, best_streak DESC, LOWER(u.username) ASC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    result = []
    for position, row in enumerate(rows, start=1):
        result.append(
            {
                "position": position,
                "user": user_from_row(row),
                "points": int(row["points"]),
                "best_streak": int(row["best_streak"]),
                "checkins": int(row["checkins"]),
            }
        )
    return result
