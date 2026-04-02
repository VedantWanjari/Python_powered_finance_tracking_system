"""tests/test_transactions.py – transaction CRUD endpoint tests."""

import datetime
import pytest
from tests.conftest import login


VALID_TXN = {
    "amount": 150.00,
    "transaction_type": "expense",
    "date": datetime.date.today().isoformat(),
    "description": "Test expense",
}


class TestCreateTransaction:
    def test_create_transaction_success(self, client, sample_user, sample_category):
        login(client, "testuser", "Test@1234")
        resp = client.post("/api/transactions/", json={**VALID_TXN, "category_id": sample_category.id})
        assert resp.status_code == 201
        assert resp.get_json()["data"]["description"] == "Test expense"

    def test_create_transaction_invalid_amount(self, client, sample_user):
        login(client, "testuser", "Test@1234")
        resp = client.post("/api/transactions/", json={**VALID_TXN, "amount": -50})
        assert resp.status_code == 400

    def test_create_transaction_missing_required_fields(self, client, sample_user):
        login(client, "testuser", "Test@1234")
        resp = client.post("/api/transactions/", json={"amount": 100})
        assert resp.status_code == 400

    def test_create_transaction_unauthenticated(self, client):
        resp = client.post("/api/transactions/", json=VALID_TXN)
        assert resp.status_code == 401


class TestListTransactions:
    def test_list_transactions_pagination(self, client, sample_user, sample_transactions):
        login(client, "testuser", "Test@1234")
        resp = client.get("/api/transactions/?page=1&per_page=5")
        assert resp.status_code == 200
        body = resp.get_json()
        assert "pagination" in body
        assert body["pagination"]["per_page"] == 5

    def test_list_transactions_filter_by_type(self, client, sample_user, sample_transactions):
        login(client, "testuser", "Test@1234")
        resp = client.get("/api/transactions/?transaction_type=income")
        assert resp.status_code == 200
        items = resp.get_json()["data"]
        assert all(t["transaction_type"] == "income" for t in items)

    def test_list_transactions_filter_by_date_range(self, client, sample_user, sample_transactions):
        login(client, "testuser", "Test@1234")
        today = datetime.date.today().isoformat()
        resp = client.get(f"/api/transactions/?date_from={today}&date_to={today}")
        assert resp.status_code == 200

    def test_list_transactions_filter_by_category(self, client, sample_user, sample_transactions, sample_category):
        login(client, "testuser", "Test@1234")
        resp = client.get(f"/api/transactions/?category_id={sample_category.id}")
        assert resp.status_code == 200
        items = resp.get_json()["data"]
        assert all(t["category_id"] == sample_category.id for t in items)


class TestGetTransaction:
    def test_get_transaction_success(self, client, sample_user, sample_transactions, app):
        login(client, "testuser", "Test@1234")
        txn_id = sample_transactions[0]["id"]
        resp = client.get(f"/api/transactions/{txn_id}")
        assert resp.status_code == 200

    def test_get_transaction_not_found(self, client, sample_user):
        login(client, "testuser", "Test@1234")
        resp = client.get("/api/transactions/99999")
        assert resp.status_code == 404

    def test_get_transaction_other_user(self, client, sample_admin, sample_transactions, app):
        """Admin logged in cannot access testuser's transactions via ownership check."""
        login(client, "adminuser", "Admin@1234")
        txn_id = sample_transactions[0]["id"]
        resp = client.get(f"/api/transactions/{txn_id}")
        assert resp.status_code == 403


class TestUpdateTransaction:
    def test_update_transaction_success(self, client, sample_user, sample_transactions):
        login(client, "testuser", "Test@1234")
        txn_id = sample_transactions[0]["id"]
        resp = client.put(f"/api/transactions/{txn_id}", json={"description": "Updated"})
        assert resp.status_code == 200
        assert resp.get_json()["data"]["description"] == "Updated"


class TestDeleteTransaction:
    def test_delete_transaction_success(self, client, sample_user, sample_transactions):
        login(client, "testuser", "Test@1234")
        txn_id = sample_transactions[0]["id"]
        resp = client.delete(f"/api/transactions/{txn_id}")
        assert resp.status_code == 200
        # Verify it's gone
        resp2 = client.get(f"/api/transactions/{txn_id}")
        assert resp2.status_code == 404

    def test_delete_transaction_other_user(self, client, sample_admin, sample_transactions):
        login(client, "adminuser", "Admin@1234")
        txn_id = sample_transactions[0]["id"]
        resp = client.delete(f"/api/transactions/{txn_id}")
        assert resp.status_code == 403
