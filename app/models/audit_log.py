import datetime
import json
from app import db

_utcnow = lambda: datetime.datetime.now(datetime.UTC).replace(tzinfo=None)

class AuditLog(db.Model):

    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"),
                        nullable=True, index=True)

    action = db.Column(db.String(64), nullable=False, index=True)

    resource_type = db.Column(db.String(64), nullable=False)

    resource_id = db.Column(db.String(64), nullable=True)

    _old_values = db.Column("old_values", db.Text, nullable=True)

    _new_values = db.Column("new_values", db.Text, nullable=True)

    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, nullable=False,
                           default=_utcnow, index=True)

    @property
    def old_values(self) -> dict:
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

    def __repr__(self) -> str:
        return f"<AuditLog {self.action} by user={self.user_id} at {self.created_at}>"
