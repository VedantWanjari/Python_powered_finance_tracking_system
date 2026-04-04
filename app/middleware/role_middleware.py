import functools
import logging
from flask import g, abort
from app.middleware.auth_middleware import login_required

logger = logging.getLogger(__name__)

ROLE_HIERARCHY = ["viewer", "analyst", "admin"]

def require_role(*roles: str):
    def decorator(fn):
        @functools.wraps(fn)
        @login_required
        def wrapper(*args, **kwargs):
            user_role = g.current_user.role

            if user_role not in roles:
                min_required_level = min(
                    ROLE_HIERARCHY.index(r) for r in roles
                    if r in ROLE_HIERARCHY
                )
                user_level = ROLE_HIERARCHY.index(user_role) if user_role in ROLE_HIERARCHY else -1

                if user_level < min_required_level:
                    logger.warning(
                        "Forbidden: user %s (role=%s) tried to access %s",
                        g.current_user.id, user_role, fn.__name__
                    )
                    abort(403)

            return fn(*args, **kwargs)
        return wrapper
    return decorator

def admin_required(fn):
    return require_role("admin")(fn)

def analyst_required(fn):
    return require_role("analyst", "admin")(fn)
