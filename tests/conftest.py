import base64
from io import BytesIO

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.database import init_db
from app.repository import create_user
from app.services.seed_service import seed_badges


def make_test_image(filename: str = "test.png") -> tuple[BytesIO, str]:
    png_bytes = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9sX0XKAAAAAASUVORK5CYII="
    )
    return BytesIO(png_bytes), filename


@pytest.fixture()
def app(tmp_path):
    upload_dir = tmp_path / "uploads"
    database_path = tmp_path / "test.db"
    app = create_app("testing")
    app.config.update(
        SECRET_KEY="testing-secret",
        UPLOAD_ROOT=upload_dir,
        DATABASE_PATH=database_path,
    )

    with app.app_context():
        init_db()
        seed_badges()
        yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture()
def user(app):
    with app.app_context():
        user_id = create_user(
            username="tester",
            email="tester@example.com",
            city="Москва",
            bio="Тестовый пользователь",
            password_hash=generate_password_hash("secret123"),
        )
        return user_id
