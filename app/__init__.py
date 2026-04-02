"""
app/__init__.py
───────────────
Flask application factory.

Using a factory function (create_app) instead of a module-level app object
lets us create multiple instances with different configs — essential for
running tests alongside the dev server without state leaking between them.
"""

import logging                          # standard-library logging
from flask import Flask                 # core web framework
from flask_sqlalchemy import SQLAlchemy # ORM integration
from flask_migrate import Migrate       # Alembic migration wrapper
from flask_limiter import Limiter       # rate limiting
from flask_limiter.util import get_remote_address  # IP extractor for limiter
from flask_cors import CORS             # Cross-Origin Resource Sharing

from app.config import config_by_name, DEFAULT_CONFIG  # our config registry

# ── Extension instances (no app attached yet) ─────────────────────────────────
# Creating extensions here and calling .init_app(app) later is the
# "application factory pattern" – it lets multiple apps share the same extension.
db = SQLAlchemy()       # shared database session / metadata
migrate = Migrate()     # handles `flask db upgrade` etc.
limiter = Limiter(key_func=get_remote_address)  # rate-limit by client IP


def create_app(config_name: str = DEFAULT_CONFIG) -> Flask:
    """
    Create and configure a Flask application instance.

    Args:
        config_name: Key into config_by_name dict.
                     Defaults to the FLASK_ENV environment variable.

    Returns:
        A fully configured Flask app ready to serve requests.
    """
    # ── App instance ──────────────────────────────────────────────────────
    app = Flask(__name__)  # __name__ helps Flask locate templates/static files

    # Load configuration object from registry
    app.config.from_object(config_by_name[config_name])

    # ── Initialise extensions with this app ───────────────────────────────
    db.init_app(app)        # bind SQLAlchemy to app
    migrate.init_app(app, db)  # bind Alembic migrations
    limiter.init_app(app)   # bind rate limiter

    # Allow the React dev server (localhost:3000) to send credentials
    CORS(app, supports_credentials=True, origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ])

    # ── Register blueprints (route groups) ────────────────────────────────
    _register_blueprints(app)

    # ── Register global error handlers ────────────────────────────────────
    _register_error_handlers(app)

    # ── Register before/after request hooks ───────────────────────────────
    _register_request_hooks(app)

    # ── Configure logging ─────────────────────────────────────────────────
    _configure_logging(app)

    return app


def _register_blueprints(app: Flask) -> None:
    """Attach all route blueprints to the app under their URL prefixes."""
    # Import here (not at module level) to avoid circular imports with db
    from app.routes.auth import auth_bp
    from app.routes.transactions import transactions_bp
    from app.routes.analytics import analytics_bp
    from app.routes.users import users_bp
    from app.routes.categories import categories_bp

    app.register_blueprint(auth_bp,         url_prefix="/api/auth")
    app.register_blueprint(transactions_bp, url_prefix="/api/transactions")
    app.register_blueprint(analytics_bp,    url_prefix="/api/analytics")
    app.register_blueprint(users_bp,        url_prefix="/api/users")
    app.register_blueprint(categories_bp,   url_prefix="/api/categories")


def _register_error_handlers(app: Flask) -> None:
    """Attach JSON error handlers so every HTTP error returns consistent JSON."""
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
    """Register before_request / after_request lifecycle hooks."""
    from app.middleware.request_logger import log_request_start, log_request_end
    app.before_request(log_request_start)
    app.after_request(log_request_end)


def _configure_logging(app: Flask) -> None:
    """
    Set up root logger so all app.logger calls go to stdout + log file.
    Keeps logging consistent whether running via `flask run` or pytest.
    """
    from app.utils.logger import setup_logger
    setup_logger(app)
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)
