import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flasgger import Swagger

from app.config import config_by_name, DEFAULT_CONFIG

db = SQLAlchemy()
migrate = Migrate()
limiter = Limiter(key_func=get_remote_address)

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
    "uiversion": 3,
}

SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "Finance Tracker API",
        "description": (
            "A Python-powered personal finance tracking REST API.\n\n"
            "**Authentication:** Session-based. Call `POST /api/auth/login` first — "
            "the server sets an HTTP-only cookie that is sent automatically on every "
            "subsequent request.\n\n"
            "**Admin credentials:**\n"
            "- Username: `admin`\n"
            "- Password: `Admin@1234`\n\n"
            "Use the `/api/auth/login` endpoint below, then explore the rest of the API."
        ),
        "version": "1.0.0",
        "contact": {"name": "Vedant Wanjari"},
    },
    "basePath": "/",
    "securityDefinitions": {
        "cookieAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Cookie",
            "description": "Session cookie obtained from POST /api/auth/login",
        }
    },
    "consumes": ["application/json"],
    "produces": ["application/json"],
    "tags": [
        {"name": "Auth", "description": "Authentication and profile management"},
        {"name": "Transactions", "description": "Create, read, update, delete and export transactions"},
        {"name": "Analytics", "description": "Dashboard, trends and reporting endpoints"},
        {"name": "Users", "description": "Admin-only user management"},
    ],
    "definitions": {
        "UserResponse": {
            "type": "object",
            "properties": {
                "id":         {"type": "integer", "example": 1},
                "username":   {"type": "string",  "example": "vedant"},
                "email":      {"type": "string",  "example": "vedant@example.com"},
                "role":       {"type": "string",  "enum": ["viewer", "analyst", "admin"], "example": "viewer"},
                "is_active":  {"type": "boolean", "example": True},
                "created_at": {"type": "string",  "format": "date-time", "example": "2024-01-01T00:00:00"},
                "updated_at": {"type": "string",  "format": "date-time", "example": "2024-01-01T00:00:00"},
            },
        },
    },
}


def create_app(config_name: str = DEFAULT_CONFIG) -> Flask:
    app = Flask(__name__)

    app.config.from_object(config_by_name[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)
    Swagger(app, config=SWAGGER_CONFIG, template=SWAGGER_TEMPLATE)

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
