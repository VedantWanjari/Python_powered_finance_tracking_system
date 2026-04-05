import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class BaseConfig:

    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "Lax"

    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    CACHE_TIMEOUT: int = int(os.getenv("CACHE_TIMEOUT", 300))

    RATELIMIT_DEFAULT: str = os.getenv("RATELIMIT_DEFAULT", "100 per minute")
    RATELIMIT_STORAGE_URL: str = "memory://"

class DevelopmentConfig(BaseConfig):

    DEBUG: bool = True

    SQLALCHEMY_DATABASE_URI: str = (
        "mysql+pymysql://"
        f"{quote_plus(os.getenv('MYSQL_USER', 'root'))}:"
        f"{quote_plus(os.getenv('MYSQL_PASSWORD', ''))}@"
        f"{os.getenv('MYSQL_HOST', 'localhost')}:"
        f"{os.getenv('MYSQL_PORT', '3306')}/"
        f"{os.getenv('MYSQL_DATABASE', 'finance_tracker')}"
    )

    SQLALCHEMY_ECHO: bool = False

class TestingConfig(BaseConfig):

    TESTING: bool = True
    DEBUG: bool = True

    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"

    RATELIMIT_ENABLED: bool = False

    CACHE_TIMEOUT: int = 5

    WTF_CSRF_ENABLED: bool = False

def _build_prod_db_uri() -> str:
    url = os.getenv("DATABASE_URL")
    if url:
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url
    return (
        "mysql+pymysql://"
        f"{quote_plus(os.getenv('MYSQL_USER', 'root'))}:"
        f"{quote_plus(os.getenv('MYSQL_PASSWORD', ''))}@"
        f"{os.getenv('MYSQL_HOST', 'localhost')}:"
        f"{os.getenv('MYSQL_PORT', '3306')}/"
        f"{os.getenv('MYSQL_DATABASE', 'finance_tracker')}"
    )


class ProductionConfig(BaseConfig):

    DEBUG: bool = False
    TESTING: bool = False

    SESSION_COOKIE_SECURE: bool = True

    SQLALCHEMY_DATABASE_URI: str = _build_prod_db_uri()

config_by_name: dict = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

DEFAULT_CONFIG: str = os.getenv("FLASK_ENV", "development")
