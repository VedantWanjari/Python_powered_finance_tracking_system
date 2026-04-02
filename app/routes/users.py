"""
app/routes/users.py
──────────────────────
Admin-only user management endpoints.

All endpoints live under /api/users.
"""

import logging
from flask import Blueprint, request, g

from app.middleware.role_middleware import admin_required
from app.middleware.error_handler import handle_app_error
from app.validators.user_validator import AdminUserUpdateSchema
from app.validators.decorators import validate_schema
from app.services.user_service import UserService
from app.services.exceptions import AppError
from app.models.audit_log import AuditLog
from app.utils.response_formatter import success_response, paginated_response

logger = logging.getLogger(__name__)
users_bp = Blueprint("users", __name__)


# ── GET /api/users ────────────────────────────────────────────────────────────

@users_bp.route("/", methods=["GET"])
@admin_required
def list_users():
    """Return a paginated list of all users (admin only)."""
    try:
        page     = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("per_page", 20)), 100)
    except ValueError:
        page, per_page = 1, 20

    users, total = UserService.list_users(page=page, per_page=per_page)
    return paginated_response(users, total, page, per_page, "Users retrieved.")


# ── GET /api/users/<id> ───────────────────────────────────────────────────────

@users_bp.route("/<int:user_id>", methods=["GET"])
@admin_required
def get_user(user_id: int):
    """Fetch a specific user by ID (admin only)."""
    try:
        user = UserService.get_user(user_id)
        return success_response(user.to_dict())
    except AppError as exc:
        return handle_app_error(exc)


# ── PUT /api/users/<id> ───────────────────────────────────────────────────────

@users_bp.route("/<int:user_id>", methods=["PUT"])
@admin_required
@validate_schema(AdminUserUpdateSchema)
def update_user(user_id: int):
    """Update a user's role or active status (admin only)."""
    try:
        user = UserService.admin_update_user(
            user_id, g.validated_data, g.current_user.id
        )
        return success_response(user.to_dict(), "User updated.")
    except AppError as exc:
        return handle_app_error(exc)


# ── DELETE /api/users/<id> ────────────────────────────────────────────────────

@users_bp.route("/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id: int):
    """Deactivate (soft-delete) a user (admin only)."""
    try:
        UserService.deactivate_user(user_id, g.current_user.id)
        return success_response(None, "User deactivated.")
    except AppError as exc:
        return handle_app_error(exc)


# ── GET /api/users/<id>/audit-log ────────────────────────────────────────────

@users_bp.route("/<int:user_id>/audit-log", methods=["GET"])
@admin_required
def user_audit_log(user_id: int):
    """Return the audit trail for a specific user (admin only)."""
    try:
        page     = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("per_page", 20)), 100)
    except ValueError:
        page, per_page = 1, 20

    paginator = (
        AuditLog.query
        .filter_by(user_id=user_id)
        .order_by(AuditLog.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    logs = [log.to_dict() for log in paginator.items]
    return paginated_response(logs, paginator.total, page, per_page, "Audit log retrieved.")
