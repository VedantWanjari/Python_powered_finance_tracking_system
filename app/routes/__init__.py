"""app/routes/__init__.py – expose all route blueprints."""

from app.routes.auth import auth_bp             # noqa: F401
from app.routes.transactions import transactions_bp  # noqa: F401
from app.routes.analytics import analytics_bp   # noqa: F401
from app.routes.users import users_bp           # noqa: F401
