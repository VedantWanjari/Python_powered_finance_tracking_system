"""
app/middleware/role_middleware.py
──────────────────────────────────
Role-Based Access Control (RBAC) decorators.

Role hierarchy (least → most privileged):
  viewer < analyst < admin

Higher roles inherit all permissions of lower roles.
"""

import functools
import logging
from flask import g, abort
from app.middleware.auth_middleware import login_required

logger = logging.getLogger(__name__)

# Ordered list of roles – index = privilege level
ROLE_HIERARCHY = ["viewer", "analyst", "admin"]


def require_role(*roles: str):
    """
    Decorator factory: restrict an endpoint to users with one of *roles*.

    Automatically applies login_required first so routes only need one decorator.

    Args:
        *roles: Allowed role names (e.g. "admin", "analyst").

    Usage:
        @analytics_bp.route("/trends")
        @require_role("analyst", "admin")
        def trends():
            ...
    """
    def decorator(fn):
        @functools.wraps(fn)
        @login_required              # ensure g.current_user is set first
        def wrapper(*args, **kwargs):
            user_role = g.current_user.role

            # Check if the user's role meets the minimum required level
            if user_role not in roles:
                # Also allow any role that is higher than the required minimum
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
                    abort(403)   # triggers handle_403 error handler

            return fn(*args, **kwargs)
        return wrapper
    return decorator


# ── Convenience aliases ───────────────────────────────────────────────────────

def admin_required(fn):
    """Shorthand for @require_role('admin')."""
    return require_role("admin")(fn)


def analyst_required(fn):
    """Shorthand for @require_role('analyst', 'admin')."""
    return require_role("analyst", "admin")(fn)
