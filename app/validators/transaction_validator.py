"""
app/validators/transaction_validator.py
────────────────────────────────────────
Marshmallow schemas for transaction input validation.

Two schemas:
  TransactionCreateSchema – validates POST /api/transactions body
  TransactionUpdateSchema – validates PUT  /api/transactions/<id> body
                            (all fields optional for partial updates)
"""

import datetime
from decimal import Decimal
from marshmallow import Schema, fields, validates, ValidationError, post_load, validate


class TransactionCreateSchema(Schema):
    """Validates the body of a create-transaction request."""

    # Required fields ─────────────────────────────────────────────────────
    # Decimal with 2 places; must be positive (validated below)
    amount = fields.Decimal(required=True, places=2, as_string=False)

    # Only "income" or "expense" are valid
    transaction_type = fields.String(
        required=True,
        validate=validate.OneOf(["income", "expense"],
                                error="transaction_type must be 'income' or 'expense'"),
    )

    # Accepts ISO-8601 date strings (YYYY-MM-DD); Marshmallow parses to date
    date = fields.Date(required=True)

    # Short label; strip whitespace before saving
    description = fields.String(
        required=True,
        validate=validate.Length(min=1, max=255),
    )

    # Optional fields ─────────────────────────────────────────────────────
    category_id    = fields.Integer(load_default=None)
    notes          = fields.String(load_default=None, allow_none=True)
    tags           = fields.List(fields.String(), load_default=[])
    is_recurring   = fields.Boolean(load_default=False)
    # "weekly" / "monthly" / "yearly" – only relevant when is_recurring=True
    recurring_frequency = fields.String(
        load_default=None,
        allow_none=True,
        validate=validate.OneOf(
            [None, "weekly", "monthly", "yearly"],
            error="recurring_frequency must be weekly, monthly, or yearly",
        ),
    )
    budget_month = fields.String(load_default=None, allow_none=True)

    # ── Field-level validators ────────────────────────────────────────────

    @validates("amount")
    def validate_amount(self, value: Decimal) -> Decimal:
        """Amount must be a positive number."""
        if value <= 0:
            raise ValidationError("Amount must be greater than zero.")
        return value

    @validates("tags")
    def validate_tags(self, value: list) -> list:
        """Every tag must be a non-empty string."""
        for tag in value:
            if not isinstance(tag, str) or not tag.strip():
                raise ValidationError("Each tag must be a non-empty string.")
        return value

    @validates("description")
    def validate_description(self, value: str) -> str:
        """Reject whitespace-only descriptions."""
        if not value.strip():
            raise ValidationError("Description cannot be blank.")
        return value.strip()

    @post_load
    def check_recurring_consistency(self, data: dict, **kwargs) -> dict:
        """
        Cross-field validation: if is_recurring=True, frequency must be set.
        @post_load runs after all individual field validations pass.
        """
        if data.get("is_recurring") and not data.get("recurring_frequency"):
            raise ValidationError(
                {"recurring_frequency": ["Required when is_recurring is true."]}
            )
        return data


class TransactionUpdateSchema(Schema):
    """
    Validates a PATCH/PUT transaction request.
    All fields are optional – only provided fields are updated.
    Validators are identical to CreateSchema.
    """

    amount = fields.Decimal(places=2, as_string=False, load_default=None)
    transaction_type = fields.String(
        load_default=None,
        validate=validate.OneOf(["income", "expense"]),
    )
    date            = fields.Date(load_default=None)
    description     = fields.String(
        load_default=None, validate=validate.Length(min=1, max=255)
    )
    category_id     = fields.Integer(load_default=None)
    notes           = fields.String(load_default=None, allow_none=True)
    tags            = fields.List(fields.String(), load_default=None)
    is_recurring    = fields.Boolean(load_default=None)
    recurring_frequency = fields.String(load_default=None, allow_none=True)
    budget_month    = fields.String(load_default=None, allow_none=True)

    @validates("amount")
    def validate_amount(self, value):
        if value is not None and value <= 0:
            raise ValidationError("Amount must be greater than zero.")
        return value
