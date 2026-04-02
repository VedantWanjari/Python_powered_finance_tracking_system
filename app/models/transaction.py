"""
app/models/transaction.py
─────────────────────────
Core financial transaction record.

Fields follow double-entry bookkeeping conventions:
  • transaction_type = "income"  → money coming in
  • transaction_type = "expense" → money going out

Tags are stored as a JSON string so they're portable across MySQL and
SQLite (which has no native JSON column type in older versions).
"""

import datetime
import json
from typing import List
from app import db


class Transaction(db.Model):
    """A single financial event (income or expense)."""

    __tablename__ = "transactions"

    # ── Core fields ───────────────────────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Foreign key to the user who owns this transaction
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"),
                        nullable=False, index=True)

    # DECIMAL(10,2) = up to 99,999,999.99 – enough for personal finance
    amount = db.Column(db.Numeric(10, 2), nullable=False)

    # Only two valid values; enforced by Marshmallow validator
    transaction_type = db.Column(db.String(10), nullable=False, index=True)

    # Optional category – nullable so uncategorised transactions are allowed
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"),
                             nullable=True, index=True)

    # Date of the financial event (not necessarily when it was entered)
    date = db.Column(db.Date, nullable=False, index=True)

    # Short required label (e.g. "Grocery run", "Monthly rent")
    description = db.Column(db.String(255), nullable=False)

    # Optional longer notes (supports full-text search)
    notes = db.Column(db.Text, nullable=True)

    # JSON-encoded list of string tags, e.g. '["travel","work"]'
    # Stored as Text for SQLite compat; parsed to list via property below
    _tags = db.Column("tags", db.Text, nullable=True, default="[]")

    # ── Recurring transaction support ─────────────────────────────────────
    is_recurring = db.Column(db.Boolean, nullable=False, default=False)
    # "weekly" / "monthly" / "yearly" – NULL when is_recurring=False
    recurring_frequency = db.Column(db.String(20), nullable=True)

    # "YYYY-MM" string used for budget tracking (e.g. "2024-03")
    budget_month = db.Column(db.String(7), nullable=True, index=True)

    # ── Timestamps ────────────────────────────────────────────────────────
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.datetime.utcnow,
                           onupdate=datetime.datetime.utcnow)

    # ── Composite indexes for common filter combinations ──────────────────
    # Speeds up "show all expenses in March 2024" type queries
    __table_args__ = (
        db.Index("ix_txn_user_date", "user_id", "date"),
        db.Index("ix_txn_user_type", "user_id", "transaction_type"),
        db.Index("ix_txn_user_category", "user_id", "category_id"),
    )

    # ── Tags property (serialize/deserialize JSON) ────────────────────────

    @property
    def tags(self) -> List[str]:
        """Return tags as a Python list (parsed from JSON string)."""
        if not self._tags:
            return []
        try:
            return json.loads(self._tags)
        except (json.JSONDecodeError, TypeError):
            return []

    @tags.setter
    def tags(self, value: List[str]) -> None:
        """Store tags as JSON string."""
        self._tags = json.dumps(value) if value else "[]"

    # ── Serialisation ─────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Return a JSON-safe dict including computed/related fields."""
        return {
            "id":                  self.id,
            "user_id":             self.user_id,
            "amount":              float(self.amount) if self.amount is not None else None,
            "transaction_type":    self.transaction_type,
            "category_id":         self.category_id,
            "category_name":       self.category_ref.name if self.category_ref else None,
            "date":                self.date.isoformat() if self.date else None,
            "description":         self.description,
            "notes":               self.notes,
            "tags":                self.tags,
            "is_recurring":        self.is_recurring,
            "recurring_frequency": self.recurring_frequency,
            "budget_month":        self.budget_month,
            "created_at":          self.created_at.isoformat() if self.created_at else None,
            "updated_at":          self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:  # pragma: no cover
        return (f"<Transaction {self.id} "
                f"{self.transaction_type} {self.amount} on {self.date}>")
