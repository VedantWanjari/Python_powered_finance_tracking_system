"""
app/config.py
─────────────
Centralised configuration management.

Three environments are provided:
  • DevelopmentConfig  – local MySQL, debug on
  • TestingConfig      – SQLite in-memory, no auth checks
  • ProductionConfig   – strict settings, no debug

The active config is chosen by the FLASK_ENV environment variable
(or passed explicitly to the app factory).
"""

import os                        # standard-library env-var access
from pathlib import Path
from urllib.parse import quote_plus  # URL-encode credentials for DB URI
from dotenv import load_dotenv   # loads .env file into os.environ

# Resolve the .env file relative to this file (app/config.py → project root/.env)
# so it is found regardless of the current working directory.
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_ENV_FILE)


class BaseConfig:
    """Settings shared by every environment."""

    # ── Security ──────────────────────────────────────────────────────────
    # Used to sign session cookies – MUST be long and random in production
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

    # ── SQLAlchemy ────────────────────────────────────────────────────────
    # Disable the modification-tracking feature (we don't need it, saves RAM)
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # ── Session cookies ───────────────────────────────────────────────────
    SESSION_COOKIE_HTTPONLY: bool = True   # JS cannot read the cookie
    SESSION_COOKIE_SAMESITE: str = "Lax"  # CSRF mitigation

    # ── Pagination defaults ───────────────────────────────────────────────
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # ── Analytics cache ───────────────────────────────────────────────────
    # How many seconds before a cached result is considered stale
    CACHE_TIMEOUT: int = int(os.getenv("CACHE_TIMEOUT", 300))

    # ── Rate limiting ─────────────────────────────────────────────────────
    RATELIMIT_DEFAULT: str = os.getenv("RATELIMIT_DEFAULT", "100 per minute")
    RATELIMIT_STORAGE_URL: str = "memory://"  # in-process store (no Redis needed)


class DevelopmentConfig(BaseConfig):
    """Local development – MySQL, verbose errors, debug mode."""

    DEBUG: bool = True

    # Build MySQL connection URL from individual env vars for clarity.
    # quote_plus encodes special characters (e.g. @, #, %) in credentials
    # that would otherwise break URL parsing.
    SQLALCHEMY_DATABASE_URI: str = (
        "mysql+pymysql://"
        f"{quote_plus(os.getenv('MYSQL_USER', 'root'))}:"
        f"{quote_plus(os.getenv('MYSQL_PASSWORD', ''))}@"
        f"{os.getenv('MYSQL_HOST', 'localhost')}:"
        f"{os.getenv('MYSQL_PORT', '3306')}/"
        f"{os.getenv('MYSQL_DATABASE', 'finance_tracker')}"
    )

    # Show generated SQL in the console – handy for debugging queries
    SQLALCHEMY_ECHO: bool = False


class TestingConfig(BaseConfig):
    """
    CI / pytest environment.

    Uses SQLite in-memory so no MySQL instance is required.
    TESTING=True tells Flask to propagate exceptions (no 500 wrappers).
    WTF_CSRF_ENABLED=False removes CSRF so test clients can POST freely.
    """

    TESTING: bool = True
    DEBUG: bool = True

    # SQLite in-memory – created fresh for each test session
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"

    # Disable rate limiting during tests (avoids 429s on repeated calls)
    RATELIMIT_ENABLED: bool = False

    # Short cache TTL so cache-behaviour tests run quickly
    CACHE_TIMEOUT: int = 5

    WTF_CSRF_ENABLED: bool = False


class ProductionConfig(BaseConfig):
    """Production – strict security, no debug output."""

    DEBUG: bool = False
    TESTING: bool = False

    SESSION_COOKIE_SECURE: bool = True   # HTTPS only

    SQLALCHEMY_DATABASE_URI: str = (
        "mysql+pymysql://"
        f"{quote_plus(os.getenv('MYSQL_USER', 'root'))}:"
        f"{quote_plus(os.getenv('MYSQL_PASSWORD', ''))}@"
        f"{os.getenv('MYSQL_HOST', 'localhost')}:"
        f"{os.getenv('MYSQL_PORT', '3306')}/"
        f"{os.getenv('MYSQL_DATABASE', 'finance_tracker')}"
    )


# ── Config registry ───────────────────────────────────────────────────────────
# Maps the string value of FLASK_ENV to the matching class.
# The app factory uses this dict to pick the right config at startup.
config_by_name: dict = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

# Default to development so bare `flask run` works out of the box
DEFAULT_CONFIG: str = os.getenv("FLASK_ENV", "development")
