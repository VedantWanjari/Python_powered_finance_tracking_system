"""
app/middleware/error_handler.py
───────────────────────────────
Global Flask error handlers.

Every HTTP error (400–500) and every domain AppError raised in services
is intercepted here and converted to a consistent JSON response envelope.

Having a single place for error formatting means:
  • The API surface is predictable (clients parse one shape)
  • Error IDs (UUIDs) appear in logs for cross-referencing support tickets
"""

import uuid
import logging
from flask import jsonify
from app.services.exceptions import AppError, ValidationError

logger = logging.getLogger(__name__)


def _make_error(message: str, status_code: int, errors=None) -> tuple:
    """Build a standardised error JSON body."""
    import datetime
    error_id = str(uuid.uuid4())   # unique ID for log correlation
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


# ── HTTP error handlers ───────────────────────────────────────────────────────

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
    # Log the full exception for internal debugging
    logger.exception("Internal server error: %s", e)
    # Return a generic message – never leak stack traces to clients
    return _make_error("Internal server error. Please try again later.", 500)


# ── Domain exception handler (used by routes) ─────────────────────────────────

def handle_app_error(exc: AppError) -> tuple:
    """
    Convert an AppError subclass into the appropriate HTTP response.

    Call this from route exception handlers:
        except AppError as exc:
            return handle_app_error(exc)
    """
    errors = getattr(exc, "errors", None)   # ValidationError carries field errors
    return _make_error(exc.message, exc.status_code, errors=errors)
