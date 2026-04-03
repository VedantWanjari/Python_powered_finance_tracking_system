"""
app/models/audit_log.py
───────────────────────
Immutable audit trail for all sensitive operations.

Every create / update / delete on Users and Transactions writes a row here.
This provides:
  • Compliance evidence ("who changed what, when")
  • Debugging timeline ("what happened before this bug?")
  • Security forensics ("did anyone tamper with records?")

Rows are never deleted or updated – the table is append-only.
"""

import datetime
import json
from app import db

_utcnow = lambda: datetime.datetime.now(datetime.UTC).replace(tzinfo=None)  # noqa: E731


class AuditLog(db.Model):
    """One row = one sensitive action performed by one user."""

    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Who performed the action (NULL = system / unauthenticated)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"),
                        nullable=True, index=True)

    # Short verb, e.g. "CREATE_TRANSACTION", "UPDATE_USER_ROLE", "LOGIN"
    action = db.Column(db.String(64), nullable=False, index=True)

    # Type of object that was changed, e.g. "Transaction", "User"
    resource_type = db.Column(db.String(64), nullable=False)

    # Primary key of the affected row (as string for flexibility)
    resource_id = db.Column(db.String(64), nullable=True)

    # JSON snapshot of the row BEFORE the change (NULL for creates)
    _old_values = db.Column("old_values", db.Text, nullable=True)

    # JSON snapshot of the row AFTER the change (NULL for deletes)
    _new_values = db.Column("new_values", db.Text, nullable=True)

    # Network / request context for security forensics
    ip_address = db.Column(db.String(45), nullable=True)   # IPv6 max = 45 chars
    user_agent = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, nullable=False,
                           default=_utcnow, index=True)

    # ── JSON helpers ──────────────────────────────────────────────────────

    @property
    def old_values(self) -> dict:
        """Deserialise old_values JSON string to dict."""
        if not self._old_values:
            return {}
        try:
            return json.loads(self._old_values)
        except (json.JSONDecodeError, TypeError):
            return {}

    @old_values.setter
    def old_values(self, value: dict) -> None:
        self._old_values = json.dumps(value) if value else None

    @property
    def new_values(self) -> dict:
        """Deserialise new_values JSON string to dict."""
        if not self._new_values:
            return {}
        try:
            return json.loads(self._new_values)
        except (json.JSONDecodeError, TypeError):
            return {}

    @new_values.setter
    def new_values(self, value: dict) -> None:
        self._new_values = json.dumps(value) if value else None

    def to_dict(self) -> dict:
        """Serialise to a JSON-safe dict for API responses."""
        return {
            "id":            self.id,
            "user_id":       self.user_id,
            "action":        self.action,
            "resource_type": self.resource_type,
            "resource_id":   self.resource_id,
            "old_values":    self.old_values,
            "new_values":    self.new_values,
            "ip_address":    self.ip_address,
            "user_agent":    self.user_agent,
            "created_at":    self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AuditLog {self.action} by user={self.user_id} at {self.created_at}>"
