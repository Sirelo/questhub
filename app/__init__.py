from pathlib import Path

from flask import Flask

from app.blueprints.api.routes import api_bp
from app.blueprints.auth.routes import auth_bp
from app.blueprints.challenges.routes import challenges_bp
from app.blueprints.errors.routes import errors_bp
from app.blueprints.main.routes import main_bp
from app.config import config_by_name
from app.database import init_app as init_database_app
from app.database import init_db
from app.extensions import login_manager
from app.models import Badge, User
from app.repository import get_user_by_id
from app.services.seed_service import seed_badges, seed_demo_data


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app_config = config_by_name[config_name or "development"]
    app.config.from_object(app_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_ROOT"]).mkdir(parents=True, exist_ok=True)

    init_database_app(app)
    login_manager.init_app(app)
    register_user_loader()

    register_blueprints(app)
    register_shell_context(app)
    register_cli_commands(app)
    register_template_helpers(app)

    with app.app_context():
        init_db()
        seed_badges()
        if not app.config.get("TESTING"):
            seed_demo_data()

    return app


def register_user_loader() -> None:
    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        return get_user_by_id(int(user_id))


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(challenges_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(errors_bp)


def register_shell_context(app: Flask) -> None:
    @app.shell_context_processor
    def shell_context() -> dict[str, object]:
        return {"User": User, "Badge": Badge}


def register_cli_commands(app: Flask) -> None:
    @app.cli.command("init-db")
    def init_db_command() -> None:
        init_db()
        seed_badges()
        print("Database initialized.")

    @app.cli.command("seed-demo")
    def seed_demo_command() -> None:
        init_db()
        seed_badges()
        seed_demo_data()
        print("Demo data created.")


def register_template_helpers(app: Flask) -> None:
    @app.context_processor
    def inject_globals() -> dict[str, object]:
        return {
            "difficulty_labels": {
                "easy": "Легкий",
                "medium": "Средний",
                "hard": "Сложный",
            },
            "category_labels": {
                "photo": "Фото",
                "study": "Учеба",
                "fitness": "Активность",
                "eco": "Экология",
                "creative": "Творчество",
                "city": "Город",
            },
        }
