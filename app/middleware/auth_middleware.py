import functools
import logging
from flask import session, g, request, abort
from app import db
from app.models.user import User

logger = logging.getLogger(__name__)

def login_required(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")

        if not user_id:
            logger.debug("Unauthenticated request to %s", request.path)
            abort(401)

        user = db.session.get(User, user_id)

        if user is None or not user.is_active:
            session.clear()
            abort(401)

        g.current_user = user
        return fn(*args, **kwargs)

    return wrapper
