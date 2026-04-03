"""
app/models/category.py
──────────────────────
Spending / income category (e.g. "Food", "Salary", "Utilities").

Default categories are seeded at DB initialisation time (setup_db.py).
Users with admin role can create custom categories.
"""

import datetime
from app import db

_utcnow = lambda: datetime.datetime.now(datetime.UTC).replace(tzinfo=None)  # noqa: E731


class Category(db.Model):
    """Groups transactions for reporting and analytics."""

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Human-readable name shown in the UI / API responses
    name = db.Column(db.String(64), nullable=False, index=True)

    # Optional longer description
    description = db.Column(db.String(255), nullable=True)

    # Hex colour code for UI charts (e.g. "#FF5733")
    color = db.Column(db.String(7), nullable=True, default="#6C757D")

    # Emoji or icon name for mobile apps / dashboards
    icon = db.Column(db.String(32), nullable=True, default="📂")

    # NULL means it's a system-wide default; non-NULL means user-created
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    # True  = available to all users (seeded defaults)
    # False = visible only to the creator
    is_default = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime, nullable=False,
                           default=_utcnow)

    # ── Relationship back to transactions ─────────────────────────────────
    transactions = db.relationship("Transaction", backref="category_ref",
                                   lazy="dynamic")

    def to_dict(self) -> dict:
        """Serialise to a JSON-safe dict."""
        return {
            "id":          self.id,
            "name":        self.name,
            "description": self.description,
            "color":       self.color,
            "icon":        self.icon,
            "is_default":  self.is_default,
            "created_at":  self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Category {self.name}>"
