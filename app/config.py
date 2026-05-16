import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(BASE_DIR / "instance" / "app.db")))
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    UPLOAD_ROOT = BASE_DIR / "app" / "static" / "uploads"
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    DATABASE_PATH = BASE_DIR / "instance" / "test.db"


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
}
