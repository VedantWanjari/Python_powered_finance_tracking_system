"""
app/utils/decorators.py
───────────────────────
Reusable function decorators for cross-cutting concerns.
"""

import functools
import time
import logging
from flask import request, g
from app.utils.response_formatter import error_response

logger = logging.getLogger(__name__)


def timing_decorator(fn):
    """
    Log how long the wrapped function takes to execute.
    Useful for spotting slow endpoints during development.
    """
    @functools.wraps(fn)   # preserve the original function's name/docstring
    def wrapper(*args, **kwargs):
        start = time.perf_counter()           # high-resolution timer
        result = fn(*args, **kwargs)          # call the actual view function
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.debug("⏱  %s took %.2f ms", fn.__name__, elapsed_ms)
        return result
    return wrapper


def validate_json(fn):
    """
    Reject requests whose Content-Type is not application/json.

    Many auth/transaction endpoints only accept JSON bodies;
    this guard gives a clear error instead of a cryptic KeyError later.
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        # request.is_json checks the Content-Type header
        if not request.is_json:
            return error_response(
                "Request body must be JSON (Content-Type: application/json)",
                status_code=400,
            )
        return fn(*args, **kwargs)
    return wrapper


def handle_exceptions(fn):
    """
    Catch any unhandled exception inside a view and return a 500 JSON response.

    This is a safety net – specific exceptions should be caught in services
    and re-raised as domain exceptions (ResourceNotFound, etc.) that the
    global error handler already handles.  This decorator catches anything
    that slips through.
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:   # noqa: BLE001
            import uuid
            error_id = str(uuid.uuid4())
            logger.exception("Unhandled exception in %s [%s]", fn.__name__, error_id)
            # Return a generic message – never expose internal details
            return error_response(
                "An unexpected error occurred. Please try again later.",
                status_code=500,
                error_id=error_id,
            )
    return wrapper
