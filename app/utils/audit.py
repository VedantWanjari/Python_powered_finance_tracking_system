"""
app/utils/audit.py
──────────────────
Shared helper for writing audit log entries.

Both TransactionService and UserService write identical audit rows; this
module centralises that logic so there is one place to maintain it and
both callers stay in sync.
"""

import logging
from app import db
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


def write_audit_log(
    user_id: int,
    action: str,
    resource_type: str,
    resource_id,
    old_values: dict,
    new_values: dict,
) -> None:
    """
    Append one row to the audit_logs table.

    This is a fire-and-forget helper: if the write fails it logs the
    exception but never raises, so the main business operation is never
    rolled back due to an audit failure.

    Args:
        user_id:       ID of the user who performed the action.
        action:        Short verb, e.g. "CREATE_TRANSACTION", "UPDATE_USER_ROLE".
        resource_type: Type name of the affected object, e.g. "Transaction".
        resource_id:   Primary key of the affected row (any type, stored as str).
        old_values:    JSON-serialisable snapshot before the change (empty for creates).
        new_values:    JSON-serialisable snapshot after the change (empty for deletes).
    """
    try:
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
        )
        log.old_values = old_values
        log.new_values = new_values
        db.session.add(log)
        db.session.commit()
    except Exception:   # noqa: BLE001
        # Audit failure must never break the main operation
        logger.exception("Failed to write audit log for action=%s resource=%s", action, resource_id)
