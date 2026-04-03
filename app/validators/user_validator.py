"""
app/validators/user_validator.py
─────────────────────────────────
Marshmallow schemas for user-related input validation.
"""

import re
from marshmallow import Schema, fields, validates, ValidationError, validate

# Password rules: ≥8 chars, ≥1 uppercase, ≥1 digit, ≥1 special char
PASSWORD_MIN_LENGTH = 8
SPECIAL_CHARS = set("!@#$%^&*()_+-=[]{}|;':\",./<>?")
VALID_ROLES = {"viewer", "analyst", "admin"}


class UserRegistrationSchema(Schema):
    """Validates POST /api/auth/register body."""

    username = fields.String(
        required=True,
        validate=validate.Length(min=3, max=64),
    )
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)  # never serialised
    # Default role for new registrations; can be overridden by admin
    role = fields.String(load_default="viewer")

    @validates("username")
    def validate_username(self, value: str) -> str:
        """Usernames must be alphanumeric + underscores only."""
        if not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise ValidationError(
                "Username may only contain letters, digits, and underscores."
            )
        return value   # preserve original case

    @validates("password")
    def validate_password(self, value: str) -> str:
        """Enforce password strength rules."""
        errors = []
        if len(value) < PASSWORD_MIN_LENGTH:
            errors.append(f"Password must be at least {PASSWORD_MIN_LENGTH} characters.")
        if not any(c.isupper() for c in value):
            errors.append("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in value):
            errors.append("Password must contain at least one digit.")
        if not any(c in SPECIAL_CHARS for c in value):
            errors.append("Password must contain at least one special character.")
        if errors:
            raise ValidationError(errors)
        return value

    @validates("role")
    def validate_role(self, value: str) -> str:
        if value not in VALID_ROLES:
            raise ValidationError(f"Role must be one of: {', '.join(sorted(VALID_ROLES))}.")
        return value


class UserLoginSchema(Schema):
    """Validates POST /api/auth/login body."""
    username = fields.String(required=True)
    password = fields.String(required=True, load_only=True)


class UserUpdateSchema(Schema):
    """Validates PUT /api/auth/me (profile update)."""
    email    = fields.Email(load_default=None)
    username = fields.String(load_default=None, validate=validate.Length(min=3, max=64))

    @validates("username")
    def validate_username(self, value: str) -> str:
        if value and not re.match(r"^[a-zA-Z0-9_]+$", value):
            raise ValidationError(
                "Username may only contain letters, digits, and underscores."
            )
        return value.lower() if value else value


class AdminUserUpdateSchema(Schema):
    """Validates PUT /api/users/<id> (admin changes role/status)."""
    role      = fields.String(load_default=None)
    is_active = fields.Boolean(load_default=None)

    @validates("role")
    def validate_role(self, value: str) -> str:
        if value and value not in VALID_ROLES:
            raise ValidationError(f"Role must be one of: {', '.join(sorted(VALID_ROLES))}.")
        return value
