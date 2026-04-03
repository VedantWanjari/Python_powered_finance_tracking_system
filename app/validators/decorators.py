"""
app/validators/decorators.py
──────────────────────────────
`@validate_schema` decorator – validates request JSON against a Marshmallow schema.

Usage:
    @bp.route("/", methods=["POST"])
    @login_required
    @validate_schema(TransactionCreateSchema)
    def create():
        data = g.validated_data   # already clean + deserialized
        ...
"""

import functools
import logging
from flask import request, g
from marshmallow import ValidationError as MarshmallowValidationError
from app.utils.response_formatter import error_response

logger = logging.getLogger(__name__)


def validate_schema(schema_class):
    """
    Decorator factory: parse and validate JSON body against *schema_class*.

    On success:  sets g.validated_data = deserialized dict, calls the view.
    On failure:  returns 400 with field-level errors before calling the view.

    Args:
        schema_class: A Marshmallow Schema class (not an instance).
    """
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            # Ensure the request body is JSON first
            if not request.is_json:
                return error_response(
                    "Content-Type must be application/json", status_code=400
                )

            raw_data = request.get_json(silent=True) or {}

            schema = schema_class()   # instantiate schema on every request
            try:
                # load() parses raw_data and runs all validators
                g.validated_data = schema.load(raw_data)
            except MarshmallowValidationError as exc:
                # exc.messages is a dict like {"amount": ["Must be positive"]}
                logger.debug("Validation failed: %s", exc.messages)
                return error_response(
                    "Validation failed. Please check the errors field.",
                    status_code=400,
                    errors=exc.messages,
                )

            return fn(*args, **kwargs)
        return wrapper
    return decorator
