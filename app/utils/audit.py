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
    except Exception:
        logger.exception("Failed to write audit log for action=%s resource=%s", action, resource_id)
