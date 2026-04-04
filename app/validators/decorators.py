import functools
import logging
from flask import request, g
from marshmallow import ValidationError as MarshmallowValidationError
from app.utils.response_formatter import error_response

logger = logging.getLogger(__name__)

def validate_schema(schema_class):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return error_response(
                    "Content-Type must be application/json", status_code=400
                )

            raw_data = request.get_json(silent=True) or {}

            schema = schema_class()
            try:
                g.validated_data = schema.load(raw_data)
            except MarshmallowValidationError as exc:
                logger.debug("Validation failed: %s", exc.messages)
                return error_response(
                    "Validation failed. Please check the errors field.",
                    status_code=400,
                    errors=exc.messages,
                )

            return fn(*args, **kwargs)
        return wrapper
    return decorator
