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

    @staticmethod
    def create_user(data: dict) -> User:
        if User.query.filter_by(username=data["username"]).first():
            raise ConflictError(f"Username '{data['username']}' is already taken.")
        if User.query.filter_by(email=data["email"]).first():
            raise ConflictError(f"Email '{data['email']}' is already registered.")

        user = User(
            username=data["username"],
            email=data["email"],
            role=data.get("role", "viewer"),
        )
        user.set_password(data["password"])

        db.session.add(user)
        db.session.commit()

        logger.info("New user created: %s (role=%s)", user.username, user.role)
        return user

    @staticmethod
    def authenticate_user(username: str, password: str) -> User:
        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            raise ValidationError("Invalid username or password.")

        if not user.is_active:
            raise ValidationError("This account has been deactivated.")

        return user

    @staticmethod
    def get_user(user_id: int) -> User:
        user = db.session.get(User, user_id)
        if user is None:
            raise ResourceNotFound(f"User {user_id} not found.")
        return user

    @staticmethod
    def list_users(page: int = 1, per_page: int = 20) -> Tuple[list, int]:
        paginator = (
            User.query
            .order_by(User.created_at.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
        )
        return [u.to_dict() for u in paginator.items], paginator.total

    @staticmethod
    def update_user(user_id: int, data: dict, actor_id: int) -> User:
        user = db.session.get(User, user_id)
        if user is None:
            raise ResourceNotFound(f"User {user_id} not found.")

        old_data = user.to_dict()

        if data.get("email"):
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

        write_audit_log(actor_id, "UPDATE_USER", "User", user_id, old_data, user.to_dict())

        logger.info("User %s updated by actor %s", user_id, actor_id)
        return user

    @staticmethod
    def admin_update_user(user_id: int, data: dict, actor_id: int) -> User:
        user = db.session.get(User, user_id)
        if user is None:
            raise ResourceNotFound(f"User {user_id} not found.")

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
        user = db.session.get(User, user_id)
        if user is None:
            raise ResourceNotFound(f"User {user_id} not found.")
        if user_id == actor_id:
            raise Forbidden("You cannot deactivate your own account.")

        user.is_active = False
        db.session.commit()
        write_audit_log(actor_id, "DEACTIVATE_USER", "User", user_id, {}, {})
        logger.info("User %s deactivated by admin %s", user_id, actor_id)
