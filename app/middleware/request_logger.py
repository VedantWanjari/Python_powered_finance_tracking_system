import time
import logging
from flask import request, g, session

logger = logging.getLogger(__name__)

def log_request_start() -> None:
    g._request_start_time = time.perf_counter()

def log_request_end(response):
    elapsed_ms = (
        (time.perf_counter() - g._request_start_time) * 1000
        if hasattr(g, "_request_start_time") else 0
    )
    user_id = session.get("user_id", "anon")

    logger.info(
        "%s %s  user=%s  status=%s  %.1fms",
        request.method,
        request.path,
        user_id,
        response.status_code,
        elapsed_ms,
    )
    return response
