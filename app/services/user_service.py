"""
app/services/user_service.py
──────────────────────────────
Business logic for user management.
All database access goes through SQLAlchemy; no raw SQL here.
"""

import datetime
import logging
from typing import Optional, Tuple

from app import db
from app.models.user import User
from app.services.exceptions import (
    ResourceNotFound, ConflictError, ValidationError, Forbidden,
)
from app.utils.audit import write_audit_log

logger = logging.getLogger(__name__)

VALID_ROLES = {"viewer", "analyst", "admin"}


class UserService:
    """Handles all user lifecycle operations."""

    # ── Create ────────────────────────────────────────────────────────────

    @staticmethod
    def create_user(data: dict) -> User:
        """
        Register a new user.

        Args:
            data: Validated dict from UserRegistrationSchema.

        Returns:
            The newly created User instance.

        Raises:
            ConflictError: If username or email already exists.
        """
        # Check uniqueness before inserting to give a friendly error
        if User.query.filter_by(username=data["username"]).first():
            raise ConflictError(f"Username '{data['username']}' is already taken.")
        if User.query.filter_by(email=data["email"]).first():
            raise ConflictError(f"Email '{data['email']}' is already registered.")

        user = User(
            username=data["username"],
            email=data["email"],
            role=data.get("role", "viewer"),
        )
        user.set_password(data["password"])   # bcrypt hash

        db.session.add(user)
        db.session.commit()

        logger.info("New user created: %s (role=%s)", user.username, user.role)
        return user

    # ── Read ──────────────────────────────────────────────────────────────

    @staticmethod
    def authenticate_user(username: str, password: str) -> User:
        """
        Verify credentials and return the matching User.

        Args:
            username: Submitted username.
            password: Submitted plaintext password.

        Returns:
            Authenticated User instance.

        Raises:
            ValidationError: If credentials are wrong or account is inactive.
        """
        user = User.query.filter_by(username=username).first()

        # Use a generic error message so attackers can't enumerate usernames
        if user is None or not user.check_password(password):
            raise ValidationError("Invalid username or password.")

        if not user.is_active:
            raise ValidationError("This account has been deactivated.")

        return user

    @staticmethod
    def get_user(user_id: int) -> User:
        """
        Fetch a user by primary key.

        Raises:
            ResourceNotFound: If no user with that ID exists.
        """
        user = db.session.get(User, user_id)
        if user is None:
            raise ResourceNotFound(f"User {user_id} not found.")
        return user

    @staticmethod
    def list_users(page: int = 1, per_page: int = 20) -> Tuple[list, int]:
        """
        Return a paginated list of all users (admin endpoint).

        Returns:
            Tuple of (list_of_user_dicts, total_count).
        """
        paginator = (
            User.query
            .order_by(User.created_at.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )
        return [u.to_dict() for u in paginator.items], paginator.total

    # ── Update ────────────────────────────────────────────────────────────

    @staticmethod
    def update_user(user_id: int, data: dict, actor_id: int) -> User:
        """
        Update a user's profile (email, username).

        Args:
            user_id:  ID of the user to update.
            data:     Dict of fields to change (only non-None values applied).
            actor_id: ID of the user making the change (for audit log).

        Returns:
            The updated User.
        """
        user = db.session.get(User, user_id)
        if user is None:
            raise ResourceNotFound(f"User {user_id} not found.")

        old_data = user.to_dict()   # snapshot before changes for audit trail

        if data.get("email"):
            # Check email uniqueness (exclude current user)
            existing = User.query.filter(
                User.email == data["email"], User.id != user_id
            ).first()
            if existing:
                raise ConflictError("Email is already in use by another account.")
            user.email = data["email"]

        if data.get("username"):
            existing = User.query.filter(
                User.username == data["username"], User.id != user_id
            ).first()
            if existing:
                raise ConflictError("Username is already taken.")
            user.username = data["username"]

        user.updated_at = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
        db.session.commit()

        # Write audit entry
        write_audit_log(actor_id, "UPDATE_USER", "User", user_id, old_data, user.to_dict())

        logger.info("User %s updated by actor %s", user_id, actor_id)
        return user

    @staticmethod
    def admin_update_user(user_id: int, data: dict, actor_id: int) -> User:
        """
        Admin-only: change a user's role or is_active flag.

        Args:
            user_id:  Target user.
            data:     Dict with optional 'role' and 'is_active' keys.
            actor_id: Admin performing the change.
        """
        user = db.session.get(User, user_id)
        if user is None:
            raise ResourceNotFound(f"User {user_id} not found.")

        # Prevent admin from demoting themselves accidentally
        if user_id == actor_id and "role" in data and data["role"] != "admin":
            raise Forbidden("Admins cannot change their own role.")

        old_data = user.to_dict()

        if data.get("role") is not None:
            user.role = data["role"]
        if data.get("is_active") is not None:
            user.is_active = data["is_active"]

        user.updated_at = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
        db.session.commit()

        write_audit_log(actor_id, "ADMIN_UPDATE_USER", "User", user_id, old_data, user.to_dict())
        return user

    @staticmethod
    def deactivate_user(user_id: int, actor_id: int) -> None:
        """
        Soft-delete: set is_active=False instead of destroying the row.
        This preserves audit history and transaction ownership.
        """
        user = db.session.get(User, user_id)
        if user is None:
            raise ResourceNotFound(f"User {user_id} not found.")
        if user_id == actor_id:
            raise Forbidden("You cannot deactivate your own account.")

        user.is_active = False
        db.session.commit()
        write_audit_log(actor_id, "DEACTIVATE_USER", "User", user_id, {}, {})
        logger.info("User %s deactivated by admin %s", user_id, actor_id)


# ── Private helpers ───────────────────────────────────────────────────────────
# Note: _write_audit has been consolidated into app.utils.audit.write_audit_log.
