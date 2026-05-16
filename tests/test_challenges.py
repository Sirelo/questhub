import base64
from io import BytesIO

from werkzeug.security import generate_password_hash

from app.repository import (
    create_user,
    find_participation,
    get_expedition_by_title,
    get_user_by_email,
)


def make_test_image(filename: str = "test.png") -> tuple[BytesIO, str]:
    png_bytes = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9sX0XKAAAAAASUVORK5CYII="
    )
    return BytesIO(png_bytes), filename


def login(client, email: str, password: str) -> None:
    client.post(
        "/auth/login",
        data={"email": email, "password": password},
        follow_redirects=True,
    )


def test_expedition_flow_and_api(client, app):
    with app.app_context():
        create_user(
            username="creator",
            email="creator@example.com",
            city="Пермь",
            bio="Создатель",
            password_hash=generate_password_hash("secret123"),
        )
        create_user(
            username="explorer",
            email="explorer@example.com",
            city="Томск",
            bio="Участник",
            password_hash=generate_password_hash("secret123"),
        )

    login(client, "creator@example.com", "secret123")
    image, filename = make_test_image("cover.png")
    create_response = client.post(
        "/expeditions/create",
        data={
            "title": "Город без спешки",
            "summary": "Семидневная практика осознанных прогулок",
            "description": "Каждый день участник гуляет без спешки, замечает новые детали и записывает наблюдение в дневник.",
            "category": "city",
            "difficulty": "medium",
            "city": "Пермь",
            "duration_days": 7,
            "target_points": 80,
            "is_public": "y",
            "cover": (image, filename),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert create_response.status_code == 200
    assert "Экспедиция создана".encode("utf-8") in create_response.data

    with app.app_context():
        expedition = get_expedition_by_title("Город без спешки")
        assert expedition is not None
        expedition_id = expedition.id

    client.get("/auth/logout", follow_redirects=True)
    login(client, "explorer@example.com", "secret123")

    join_response = client.post(f"/expeditions/{expedition_id}/join", follow_redirects=True)
    assert join_response.status_code == 200
    assert "присоединились".encode("utf-8") in join_response.data

    proof_image, proof_name = make_test_image("proof.png")
    checkin_response = client.post(
        f"/expeditions/{expedition_id}/checkin",
        data={
            "note": "Нашел новый тихий маршрут через старый район и сделал заметки о деталях города.",
            "mood": "focused",
            "proof": (proof_image, proof_name),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert checkin_response.status_code == 200
    assert "Прогресс сохранен".encode("utf-8") in checkin_response.data

    with app.app_context():
        explorer = get_user_by_email("explorer@example.com")
        participation = find_participation(explorer.id, expedition_id)
        assert participation is not None
        assert participation.total_points > 0
        assert participation.streak_days == 1

    expeditions_api = client.get("/api/expeditions")
    assert expeditions_api.status_code == 200
    expeditions_payload = expeditions_api.get_json()
    assert any(item["title"] == "Город без спешки" for item in expeditions_payload)

    leaderboard_api = client.get("/api/leaderboard")
    assert leaderboard_api.status_code == 200
    leaderboard_payload = leaderboard_api.get_json()
    assert any(row["username"] == "explorer" for row in leaderboard_payload)
