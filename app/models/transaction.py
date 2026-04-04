import datetime
import json
from typing import List
from app import db

_utcnow = lambda: datetime.datetime.now(datetime.UTC).replace(tzinfo=None)

class Transaction(db.Model):

    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"),
                        nullable=False, index=True)

    amount = db.Column(db.Numeric(10, 2), nullable=False)

    transaction_type = db.Column(db.String(10), nullable=False, index=True)

    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"),
                             nullable=True, index=True)

    date = db.Column(db.Date, nullable=False, index=True)

    description = db.Column(db.String(255), nullable=False)

    notes = db.Column(db.Text, nullable=True)

    _tags = db.Column("tags", db.Text, nullable=True, default="[]")

    is_recurring = db.Column(db.Boolean, nullable=False, default=False)
    recurring_frequency = db.Column(db.String(20), nullable=True)

    budget_month = db.Column(db.String(7), nullable=True, index=True)

    created_at = db.Column(db.DateTime, nullable=False,
                           default=_utcnow)
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=_utcnow,
                           onupdate=_utcnow)

    __table_args__ = (
        db.Index("ix_txn_user_date", "user_id", "date"),
        db.Index("ix_txn_user_type", "user_id", "transaction_type"),
        db.Index("ix_txn_user_category", "user_id", "category_id"),
    )

    @property
    def tags(self) -> List[str]:
        if not self._tags:
            return []
        try:
            return json.loads(self._tags)
        except (json.JSONDecodeError, TypeError):
            return []

    @tags.setter
    def tags(self, value: List[str]) -> None:
        self._tags = json.dumps(value) if value else "[]"

    def to_dict(self) -> dict:
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

    def __repr__(self) -> str:
        return (f"<Transaction {self.id} "
                f"{self.transaction_type} {self.amount} on {self.date}>")
