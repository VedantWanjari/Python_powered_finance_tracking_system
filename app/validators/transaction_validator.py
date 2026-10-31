import datetime
from decimal import Decimal
from marshmallow import Schema, fields, validates, ValidationError, post_load, validate

class TransactionCreateSchema(Schema):

    amount = fields.Decimal(required=True, places=2, as_string=False)

    transaction_type = fields.String(
        required=True,
        validate=validate.OneOf(["income", "expense"],
                                error="transaction_type must be 'income' or 'expense'"),
    )

    date = fields.Date(required=True)

    description = fields.String(
        required=True,
        validate=validate.Length(min=1, max=255),
    )

    category_id    = fields.Integer(load_default=None)
    notes          = fields.String(load_default=None, allow_none=True)
    tags           = fields.List(fields.String(), load_default=[])
    is_recurring   = fields.Boolean(load_default=False)
    recurring_frequency = fields.String(
        load_default=None,
        allow_none=True,
        validate=validate.OneOf(
            [None, "weekly", "monthly", "yearly"],
            error="recurring_frequency must be weekly, monthly, or yearly",
        ),
    )
    budget_month = fields.String(load_default=None, allow_none=True)

    @validates("amount")
    def validate_amount(self, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValidationError("Amount must be greater than zero.")
        return value

    @validates("tags")
    def validate_tags(self, value: list) -> list:
        for tag in value:
            if not isinstance(tag, str) or not tag.strip():
                raise ValidationError("Each tag must be a non-empty string.")
        return value

    @validates("description")
    def validate_description(self, value: str) -> str:
        if not value.strip():
            raise ValidationError("Description cannot be blank.")
        return value.strip()

    @post_load
    def check_recurring_consistency(self, data: dict, **kwargs) -> dict:
        if data.get("is_recurring") and not data.get("recurring_frequency"):
            raise ValidationError(
                {"recurring_frequency": ["Required when is_recurring is true."]}
            )
        return data

class TransactionUpdateSchema(Schema):

    amount = fields.Decimal(places=2, as_string=False)
    transaction_type = fields.String(
        validate=validate.OneOf(["income", "expense"]),
    )
    date            = fields.Date()
    description     = fields.String(
        validate=validate.Length(min=1, max=255)
    )
    category_id     = fields.Integer(allow_none=True)
    notes           = fields.String(allow_none=True)
    tags            = fields.List(fields.String(), allow_none=True)
    is_recurring    = fields.Boolean()
    recurring_frequency = fields.String(allow_none=True)
    budget_month    = fields.String(allow_none=True)

    @validates("amount")
    def validate_amount(self, value):
        if value <= 0:
            raise ValidationError("Amount must be greater than zero.")
        return value

    @validates("description")
    def validate_description(self, value: str) -> str:
        if not value.strip():
            raise ValidationError("Description cannot be blank.")
        return value.strip()

    @validates("tags")
    def validate_tags(self, value: list) -> list:
        if value is None:
            return value
        if any(not tag.strip() for tag in value):
            raise ValidationError("Each tag must be a non-empty string.")
        return value

    @post_load
    def check_recurring_consistency(self, data: dict, **kwargs) -> dict:
        if data.get("is_recurring") and not data.get("recurring_frequency"):
            raise ValidationError(
                {"recurring_frequency": ["Required when is_recurring is true."]}
            )
        return data
