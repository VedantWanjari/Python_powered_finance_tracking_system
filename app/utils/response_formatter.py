import datetime
from flask import jsonify
from typing import Any, Optional

def _now_iso() -> str:
    return datetime.datetime.now(datetime.UTC).replace(tzinfo=None).isoformat() + "Z"

def success_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
):
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
    body = {
        "status":    "error",
        "message":   message,
        "data":      None,
        "timestamp": _now_iso(),
    }
    if errors is not None:
        body["errors"] = errors
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
    import math
    total_pages = math.ceil(total / per_page) if per_page > 0 else 0

    body = {
        "status":  "success",
        "message": message,
        "data":    items,
        "pagination": {
            "total":       total,
            "page":        page,
            "per_page":    per_page,
            "total_pages": total_pages,
            "has_next":    page < total_pages,
            "has_prev":    page > 1,
        },
        "timestamp": _now_iso(),
    }
    return jsonify(body), 200
