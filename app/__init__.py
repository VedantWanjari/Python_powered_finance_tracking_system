import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.config import config_by_name, DEFAULT_CONFIG

db = SQLAlchemy()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)

def create_app(config_name: str = DEFAULT_CONFIG) -> Flask:
    app = Flask(__name__)

    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    _register_blueprints(app)

    _register_error_handlers(app)

    _register_request_hooks(app)

    _configure_logging(app)

    return app

def _register_blueprints(app: Flask) -> None:
    from app.routes.auth import auth_bp
    from app.routes.transactions import transactions_bp
    from app.routes.analytics import analytics_bp
    from app.routes.users import users_bp

    app.register_blueprint(auth_bp,         url_prefix="/api/auth")
    app.register_blueprint(transactions_bp, url_prefix="/api/transactions")
    app.register_blueprint(analytics_bp,    url_prefix="/api/analytics")
    app.register_blueprint(users_bp,        url_prefix="/api/users")

def _register_error_handlers(app: Flask) -> None:
    from app.middleware.error_handler import (
        handle_400, handle_401, handle_403,
        handle_404, handle_405, handle_429, handle_500,
    )
    app.register_error_handler(400, handle_400)
    app.register_error_handler(401, handle_401)
    app.register_error_handler(403, handle_403)
    app.register_error_handler(404, handle_404)
    app.register_error_handler(405, handle_405)
    app.register_error_handler(429, handle_429)
    app.register_error_handler(500, handle_500)

def _register_request_hooks(app: Flask) -> None:
    from app.middleware.request_logger import log_request_start, log_request_end
    app.before_request(log_request_start)
    app.after_request(log_request_end)

def _configure_logging(app: Flask) -> None:
    from app.utils.logger import setup_logger
    setup_logger(app)
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)
