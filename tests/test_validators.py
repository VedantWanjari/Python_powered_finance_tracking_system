import datetime
import pytest
from marshmallow import ValidationError

from app.validators.transaction_validator import TransactionCreateSchema
from app.validators.user_validator import UserRegistrationSchema

class TestTransactionCreateSchema:
    schema = TransactionCreateSchema()

    def test_transaction_validator_valid_data(self):
        data = self.schema.load({
            "amount": "99.99",
            "transaction_type": "expense",
            "date": datetime.date.today().isoformat(),
            "description": "Lunch",
        })
        assert float(data["amount"]) == 99.99

    def test_transaction_validator_negative_amount(self):
        with pytest.raises(ValidationError) as exc_info:
            self.schema.load({
                "amount": "-10",
                "transaction_type": "expense",
                "date": datetime.date.today().isoformat(),
                "description": "Bad",
            })
        assert "amount" in exc_info.value.messages

    def test_transaction_validator_zero_amount(self):
        with pytest.raises(ValidationError):
            self.schema.load({
                "amount": "0",
                "transaction_type": "income",
                "date": datetime.date.today().isoformat(),
                "description": "Zero",
            })

    def test_transaction_validator_invalid_type(self):
        with pytest.raises(ValidationError) as exc_info:
            self.schema.load({
                "amount": "50",
                "transaction_type": "transfer",
                "date": datetime.date.today().isoformat(),
                "description": "Transfer",
            })
        assert "transaction_type" in exc_info.value.messages

    def test_transaction_validator_invalid_date(self):
        with pytest.raises(ValidationError):
            self.schema.load({
                "amount": "50",
                "transaction_type": "expense",
                "date": "not-a-date",
                "description": "Bad date",
            })

    def test_transaction_validator_tags_must_be_strings(self):
        with pytest.raises(ValidationError):
            self.schema.load({
                "amount": "50",
                "transaction_type": "expense",
                "date": datetime.date.today().isoformat(),
                "description": "Tagged",
                "tags": [123, 456],
            })

    def test_transaction_validator_optional_fields_have_defaults(self):
        data = self.schema.load({
            "amount": "10",
            "transaction_type": "income",
            "date": datetime.date.today().isoformat(),
            "description": "Minimal",
        })
        assert data["tags"] == []
        assert data["is_recurring"] is False

    def test_transaction_validator_recurring_without_frequency(self):
        with pytest.raises(ValidationError):
            self.schema.load({
                "amount": "10",
                "transaction_type": "expense",
                "date": datetime.date.today().isoformat(),
                "description": "Recurring no freq",
                "is_recurring": True,
            })

class TestUserRegistrationSchema:
    schema = UserRegistrationSchema()

    def test_user_validator_valid_registration(self):
        data = self.schema.load({
            "username": "ValidUser",
            "email": "valid@example.com",
            "password": "Secure@123",
        })
        assert data["username"] == "ValidUser"

    def test_user_validator_invalid_email(self):
        with pytest.raises(ValidationError) as exc_info:
            self.schema.load({
                "username": "user1",
                "email": "not-an-email",
                "password": "Secure@123",
            })
        assert "email" in exc_info.value.messages

    def test_user_validator_weak_password_too_short(self):
        with pytest.raises(ValidationError) as exc_info:
            self.schema.load({
                "username": "user2",
                "email": "u2@example.com",
                "password": "Ab@1",
            })
        assert "password" in exc_info.value.messages

    def test_user_validator_weak_password_no_uppercase(self):
        with pytest.raises(ValidationError):
            self.schema.load({
                "username": "user3",
                "email": "u3@example.com",
                "password": "nouppercase@1",
            })

    def test_user_validator_weak_password_no_special_char(self):
        with pytest.raises(ValidationError):
            self.schema.load({
                "username": "user4",
                "email": "u4@example.com",
                "password": "NoSpecial123",
            })

    def test_user_validator_username_too_short(self):
        with pytest.raises(ValidationError) as exc_info:
            self.schema.load({
                "username": "ab",
                "email": "u5@example.com",
                "password": "Valid@123",
            })
        assert "username" in exc_info.value.messages

    def test_user_validator_username_invalid_chars(self):
        with pytest.raises(ValidationError) as exc_info:
            self.schema.load({
                "username": "bad user!",
                "email": "u6@example.com",
                "password": "Valid@123",
            })
        assert "username" in exc_info.value.messages
