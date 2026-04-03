"""
app/models/user.py
──────────────────
SQLAlchemy model for the `users` table.

Roles (least → most privileged):
  viewer   – read-only access to their own transactions
  analyst  – viewer + analytics endpoints + bulk import
  admin    – full access including user management
"""

import datetime                             # for default timestamps and UTC sentinel
import bcrypt                               # password hashing (salted)
from app import db                          # shared SQLAlchemy instance

# Timezone-aware UTC now — used as column defaults to avoid the deprecated
# datetime.utcnow() function (deprecated in Python 3.12).
_utcnow = lambda: datetime.datetime.now(datetime.UTC).replace(tzinfo=None)  # noqa: E731


class User(db.Model):
    """Represents a registered user of the finance system."""

    __tablename__ = "users"

    # ── Primary key ───────────────────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # ── Credentials ───────────────────────────────────────────────────────
    # unique=True enforces no duplicate usernames at the DB level
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    # Store only the bcrypt hash, never the plaintext password
    password_hash = db.Column(db.String(255), nullable=False)

    # ── Access control ────────────────────────────────────────────────────
    # Allowed values enforced at the application layer (see validators)
    role = db.Column(db.String(20), nullable=False, default="viewer")

    # Soft-deactivation: set is_active=False instead of deleting rows
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # ── Timestamps ────────────────────────────────────────────────────────
    created_at = db.Column(db.DateTime, nullable=False,
                           default=_utcnow)
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=_utcnow,
                           onupdate=_utcnow)

    # ── Relationships ─────────────────────────────────────────────────────
    # lazy="dynamic" returns a query object so callers can apply filters
    transactions = db.relationship("Transaction", backref="owner",
                                   lazy="dynamic",
                                   foreign_keys="Transaction.user_id")
    audit_logs = db.relationship("AuditLog", backref="actor",
                                 lazy="dynamic",
                                 foreign_keys="AuditLog.user_id")

    # ── Password helpers ──────────────────────────────────────────────────

    def set_password(self, plaintext: str) -> None:
        """
        Hash *plaintext* with bcrypt and store result.

        bcrypt.gensalt() generates a fresh random salt every call,
        so two users with the same password get different hashes.

        Args:
            plaintext: The raw password string supplied by the user.
        """
        hashed = bcrypt.hashpw(plaintext.encode("utf-8"), bcrypt.gensalt())
        # Decode bytes → str for storage in a VARCHAR column
        self.password_hash = hashed.decode("utf-8")

    def check_password(self, plaintext: str) -> bool:
        """
        Return True if *plaintext* matches the stored bcrypt hash.

        Args:
            plaintext: Password attempt from the login request.

        Returns:
            True if credentials match, False otherwise.
        """
        return bcrypt.checkpw(
            plaintext.encode("utf-8"),
            self.password_hash.encode("utf-8"),
        )

    # ── Serialisation ─────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Return a JSON-safe dict (never includes the password hash)."""
        return {
            "id":         self.id,
            "username":   self.username,
            "email":      self.email,
            "role":       self.role,
            "is_active":  self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<User {self.username} ({self.role})>"
