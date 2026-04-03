"""
app/utils/response_formatter.py
────────────────────────────────
Helpers that produce consistent JSON response envelopes.

Every API response (success or error) uses the same top-level structure:
  {
    "status":    "success" | "error",
    "message":   "Human-readable summary",
    "data":      <payload or null>,
    "timestamp": "2024-03-15T10:30:00Z"
  }

Consistency here means front-end clients only need one parser,
and monitoring tools can grep for "status":"error" reliably.
"""

import datetime
from flask import jsonify
from typing import Any, Optional


def _now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None).isoformat() + "Z"


def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
):
    """
    Build a 2xx JSON response.

    Args:
        data:        Payload to include (dict, list, or None).
        message:     Human-readable success message.
        status_code: HTTP status code (default 200).

    Returns:
        Flask Response tuple (json_body, status_code).
    """
    body = {
        "status":    "success",
        "message":   message,
        "data":      data,
        "timestamp": _now_iso(),
    }
    return jsonify(body), status_code


def error_response(
    message: str,
    status_code: int = 400,
    errors: Optional[Any] = None,
    error_id: Optional[str] = None,
):
    """
    Build an error JSON response.

    Args:
        message:     Short description of what went wrong.
        status_code: HTTP status code (4xx or 5xx).
        errors:      Field-level validation errors dict (optional).
        error_id:    UUID for this specific error event (for log correlation).

    Returns:
        Flask Response tuple (json_body, status_code).
    """
    body = {
        "status":    "error",
        "message":   message,
        "data":      None,
        "timestamp": _now_iso(),
    }
    # Include field errors only when present (keeps response lean otherwise)
    if errors is not None:
        body["errors"] = errors
    # Include error_id when provided so users can quote it in support tickets
    if error_id is not None:
        body["error_id"] = error_id
    return jsonify(body), status_code


def paginated_response(
    items: list,
    total: int,
    page: int,
    per_page: int,
    message: str = "Success",
):
    """
    Build a paginated list response with metadata.

    Args:
        items:    The current page's records (already serialised to dicts).
        total:    Total number of records across all pages.
        page:     Current page number (1-based).
        per_page: Number of items per page.
        message:  Human-readable summary.

    Returns:
        Flask Response tuple (json_body, 200).
    """
    import math
    total_pages = math.ceil(total / per_page) if per_page > 0 else 0

    body = {
        "status":  "success",
        "message": message,
        "data":    items,
        "pagination": {
            "total":       total,          # total rows in DB matching filters
            "page":        page,           # current page (1-indexed)
            "per_page":    per_page,       # items returned on this page
            "total_pages": total_pages,    # how many pages exist in total
            "has_next":    page < total_pages,
            "has_prev":    page > 1,
        },
        "timestamp": _now_iso(),
    }
    return jsonify(body), 200
