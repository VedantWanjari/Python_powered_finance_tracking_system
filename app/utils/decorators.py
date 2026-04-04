import functools
import time
import logging
from flask import request, g
from app.utils.response_formatter import error_response

logger = logging.getLogger(__name__)

def timing_decorator(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        logger.debug("  %s took %.2f ms", fn.__name__, elapsed_ms)
        return result
    return wrapper

def validate_json(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            return error_response(
                "Request body must be JSON (Content-Type: application/json)",
                status_code=400,
            )
        return fn(*args, **kwargs)
    return wrapper

def handle_exceptions(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            import uuid
            error_id = str(uuid.uuid4())
            logger.exception("Unhandled exception in %s [%s]", fn.__name__, error_id)
            return error_response(
                "An unexpected error occurred. Please try again later.",
                status_code=500,
                error_id=error_id,
            )
    return wrapper
