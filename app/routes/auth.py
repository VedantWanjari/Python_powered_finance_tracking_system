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

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
@validate_schema(UserRegistrationSchema)
def register():
    """
    Register a new user account.
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              example: vedant
            email:
              type: string
              example: vedant@example.com
            password:
              type: string
              example: "Secure@123"
              description: "Min 8 chars, 1 uppercase, 1 digit, 1 special character"
    responses:
      201:
        description: Account created successfully
        schema:
          $ref: '#/definitions/UserResponse'
      400:
        description: Validation error
      409:
        description: Username or email already exists
    """
    try:
        user = UserService.create_user(g.validated_data)
        return success_response(user.to_dict(), "Account created successfully.", 201)
    except AppError as exc:
        return handle_app_error(exc)

@auth_bp.route("/login", methods=["POST"])
@validate_schema(UserLoginSchema)
def login():
    """
    Authenticate and receive a session cookie.
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: demo
            password:
              type: string
              example: "Demo@1234"
    responses:
      200:
        description: Logged in successfully — session cookie is set automatically
        schema:
          $ref: '#/definitions/UserResponse'
      401:
        description: Invalid credentials
    """
    try:
        data = g.validated_data
        user = UserService.authenticate_user(data["username"], data["password"])

        session.clear()
        session["user_id"] = user.id
        session.permanent = True

        logger.info("User %s logged in from %s", user.id, request.remote_addr)
        return success_response(user.to_dict(), "Logged in successfully.")
    except AppError as exc:
        return handle_app_error(exc)

@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """
    Clear the current session.
    ---
    tags:
      - Auth
    security:
      - cookieAuth: []
    responses:
      200:
        description: Logged out successfully
      401:
        description: Not authenticated
    """
    user_id = g.current_user.id
    session.clear()
    logger.info("User %s logged out", user_id)
    return success_response(None, "Logged out successfully.")

@auth_bp.route("/me", methods=["GET"])
@login_required
def get_me():
    """
    Return the current user's profile.
    ---
    tags:
      - Auth
    security:
      - cookieAuth: []
    responses:
      200:
        description: Current user profile
        schema:
          $ref: '#/definitions/UserResponse'
      401:
        description: Not authenticated
    """
    return success_response(g.current_user.to_dict())

@auth_bp.route("/me", methods=["PUT"])
@login_required
@validate_schema(UserUpdateSchema)
def update_me():
    """
    Update the current user's email or username.
    ---
    tags:
      - Auth
    security:
      - cookieAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              example: newemail@example.com
            username:
              type: string
              example: alice_new
    responses:
      200:
        description: Profile updated
        schema:
          $ref: '#/definitions/UserResponse'
      400:
        description: Validation error
      401:
        description: Not authenticated
      409:
        description: Username or email already taken
    """
    try:
        user = UserService.update_user(
            g.current_user.id,
            g.validated_data,
            g.current_user.id,
        )
        return success_response(user.to_dict(), "Profile updated.")
    except AppError as exc:
        return handle_app_error(exc)
