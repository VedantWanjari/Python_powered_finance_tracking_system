"""
app/middleware/request_logger.py
─────────────────────────────────
Before / after request hooks for structured access logging.

Logs each request's method, path, user, and response time in one line:
  2024-03-15 10:30:00  INFO  POST /api/transactions  user=42  200  12.3ms
"""

import time
import logging
from flask import request, g, session

logger = logging.getLogger(__name__)


def log_request_start() -> None:
    """
    Record request start time before the view function runs.
    Flask calls this for every incoming request (registered via before_request).
    """
    g._request_start_time = time.perf_counter()   # high-resolution timer


def log_request_end(response):
    """
    Log the completed request after the view function returns.
    Flask calls this for every response (registered via after_request).

    Args:
        response: The Flask Response object about to be sent to the client.

    Returns:
        The response (unchanged) – after_request must return a response.
    """
    elapsed_ms = (
        (time.perf_counter() - g._request_start_time) * 1000
        if hasattr(g, "_request_start_time") else 0
    )
    user_id = session.get("user_id", "anon")   # "anon" for unauthenticated

    logger.info(
        "%s %s  user=%s  status=%s  %.1fms",
        request.method,
        request.path,
        user_id,
        response.status_code,
        elapsed_ms,
    )
    return response   # must return the response unchanged
