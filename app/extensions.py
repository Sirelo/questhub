from flask_login import LoginManager


login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Сначала войдите в аккаунт."
login_manager.login_message_category = "warning"
