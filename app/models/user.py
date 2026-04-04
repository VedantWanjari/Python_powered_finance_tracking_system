import datetime
import bcrypt
from app import db

_utcnow = lambda: datetime.datetime.now(datetime.UTC).replace(tzinfo=None)

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), nullable=False, default="viewer")

    is_active = db.Column(db.Boolean, nullable=False, default=True)

    created_at = db.Column(db.DateTime, nullable=False,
                           default=_utcnow)
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=_utcnow,
                           onupdate=_utcnow)

    transactions = db.relationship("Transaction", backref="owner",
                                   lazy="dynamic",
                                   foreign_keys="Transaction.user_id")
    audit_logs = db.relationship("AuditLog", backref="actor",
                                 lazy="dynamic",
                                 foreign_keys="AuditLog.user_id")

    def set_password(self, plaintext: str) -> None:
        hashed = bcrypt.hashpw(plaintext.encode("utf-8"), bcrypt.gensalt())
        self.password_hash = hashed.decode("utf-8")

    def check_password(self, plaintext: str) -> bool:
        return bcrypt.checkpw(
            plaintext.encode("utf-8"),
            self.password_hash.encode("utf-8"),
        )

    def to_dict(self) -> dict:
        return {
            "id":         self.id,
            "username":   self.username,
            "email":      self.email,
            "role":       self.role,
            "is_active":  self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.role})>"
