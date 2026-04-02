"""
app/routes/auth.py
───────────────────
Authentication endpoints: register, login, logout, profile.

All endpoints live under the /api/auth prefix (set in app/__init__.py).
"""

import logging
from flask import Blueprint, request, session, g

from app.validators.user_validator import (
    UserRegistrationSchema, UserLoginSchema, UserUpdateSchema,
)
from app.validators.decorators import validate_schema
from app.middleware.auth_middleware import login_required
from app.services.user_service import UserService
from app.services.exceptions import AppError
from app.middleware.error_handler import handle_app_error
from app.utils.response_formatter import success_response

logger = logging.getLogger(__name__)

# Blueprint groups related routes; url_prefix set in app factory
auth_bp = Blueprint("auth", __name__)


# ── POST /api/auth/register ───────────────────────────────────────────────────

@auth_bp.route("/register", methods=["POST"])
@validate_schema(UserRegistrationSchema)
def register():
    """
    Create a new user account.

    Request body:
        username (str), email (str), password (str), role (str, optional)

    Returns:
        201 with created user dict on success.
        400 if validation fails or username/email already taken.
    """
    try:
        user = UserService.create_user(g.validated_data)
        return success_response(user.to_dict(), "Account created successfully.", 201)
    except AppError as exc:
        return handle_app_error(exc)


# ── POST /api/auth/login ──────────────────────────────────────────────────────

@auth_bp.route("/login", methods=["POST"])
@validate_schema(UserLoginSchema)
def login():
    """
    Authenticate and create a session.

    Request body:
        username (str), password (str)

    Returns:
        200 with user dict on success.
        400 if credentials are wrong.
    """
    try:
        data = g.validated_data
        user = UserService.authenticate_user(data["username"], data["password"])

        # Store user ID in Flask session (signed cookie, not plain text)
        session.clear()           # invalidate any existing session first
        session["user_id"] = user.id
        session.permanent = True  # session survives browser close

        logger.info("User %s logged in from %s", user.id, request.remote_addr)
        return success_response(user.to_dict(), "Logged in successfully.")
    except AppError as exc:
        return handle_app_error(exc)


# ── POST /api/auth/logout ─────────────────────────────────────────────────────

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """
    Clear the current session (log out).

    Returns:
        200 with confirmation message.
    """
    user_id = g.current_user.id
    session.clear()   # remove all session data (including user_id)
    logger.info("User %s logged out", user_id)
    return success_response(None, "Logged out successfully.")


# ── GET /api/auth/me ──────────────────────────────────────────────────────────

@auth_bp.route("/me", methods=["GET"])
@login_required
def get_me():
    """
    Return the authenticated user's profile.

    Returns:
        200 with user dict.
    """
    return success_response(g.current_user.to_dict())


# ── PUT /api/auth/me ──────────────────────────────────────────────────────────

@auth_bp.route("/me", methods=["PUT"])
@login_required
@validate_schema(UserUpdateSchema)
def update_me():
    """
    Update the authenticated user's email or username.

    Request body (all optional):
        email (str), username (str)

    Returns:
        200 with updated user dict.
        400/409 on validation/conflict errors.
    """
    try:
        user = UserService.update_user(
            g.current_user.id,
            g.validated_data,
            g.current_user.id,   # actor = self
        )
        return success_response(user.to_dict(), "Profile updated.")
    except AppError as exc:
        return handle_app_error(exc)
