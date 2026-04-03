"""
app/middleware/auth_middleware.py
──────────────────────────────────
Session-based authentication middleware.

After a successful POST /api/auth/login, the server stores the user's ID
in the Flask session (a signed, HTTP-only cookie).  Subsequent requests
include this cookie automatically.

`login_required` reads the session, loads the User, and stores it in
Flask's `g` (request-context global) so route handlers can access
`g.current_user` without re-querying the database.
"""

import functools
import logging
from flask import session, g, request, abort
from app import db
from app.models.user import User

logger = logging.getLogger(__name__)


def login_required(fn):
    """
    Decorator that ensures the caller is authenticated.

    Sets g.current_user to the authenticated User ORM object.
    Aborts with 401 if the session has no user_id or the user is inactive.

    Usage:
        @transactions_bp.route("/")
        @login_required
        def list_transactions():
            user = g.current_user
            ...
    """
    @functools.wraps(fn)   # keep original function name (important for routing)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")   # read from signed session cookie

        if not user_id:
            # No session → not logged in
            logger.debug("Unauthenticated request to %s", request.path)
            abort(401)   # triggers handle_401 error handler

        # Load from DB every request to catch deactivated accounts immediately
        user = db.session.get(User, user_id)

        if user is None or not user.is_active:
            # User deleted / deactivated after login → clear stale session
            session.clear()
            abort(401)

        # Store on g so downstream decorators and view functions can use it
        g.current_user = user
        return fn(*args, **kwargs)

    return wrapper
