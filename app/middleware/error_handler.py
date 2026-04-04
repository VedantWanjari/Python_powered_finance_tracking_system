import uuid
import logging
from flask import jsonify
from app.services.exceptions import AppError, ValidationError

logger = logging.getLogger(__name__)

def _make_error(message: str, status_code: int, errors=None) -> tuple:
    import datetime
    error_id = str(uuid.uuid4())
    logger.warning("HTTP %s [%s]: %s", status_code, error_id, message)
    body = {
        "status":    "error",
        "message":   message,
        "data":      None,
        "error_id":  error_id,
        "timestamp": datetime.datetime.now(datetime.UTC).replace(tzinfo=None).isoformat() + "Z",
    }
    if errors:
        body["errors"] = errors
    return jsonify(body), status_code

def handle_400(e):
    return _make_error(str(e) or "Bad request.", 400)

def handle_401(e):
    return _make_error(str(e) or "Authentication required.", 401)

def handle_403(e):
    return _make_error(str(e) or "Access denied.", 403)

def handle_404(e):
    return _make_error(str(e) or "Resource not found.", 404)

def handle_405(e):
    return _make_error(str(e) or "Method not allowed.", 405)

def handle_429(e):
    return _make_error("Too many requests. Please slow down.", 429)

def handle_500(e):
    logger.exception("Internal server error: %s", e)
    return _make_error("Internal server error. Please try again later.", 500)

def handle_app_error(exc: AppError) -> tuple:
    errors = getattr(exc, "errors", None)
    return _make_error(exc.message, exc.status_code, errors=errors)
