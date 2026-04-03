"""tests/test_integration.py – end-to-end integration tests."""

import csv
import datetime
import io
import pytest
from tests.conftest import login


class TestFullTransactionLifecycle:
    """Create → read → update → delete a transaction."""

    def test_full_transaction_lifecycle(self, client, sample_user, sample_category):
        login(client, "testuser", "Test@1234")
        today = datetime.date.today().isoformat()

        # CREATE
        resp = client.post("/api/transactions/", json={
            "amount": 250.00,
            "transaction_type": "expense",
            "date": today,
            "description": "Original description",
            "category_id": sample_category.id,
        })
        assert resp.status_code == 201
        txn_id = resp.get_json()["data"]["id"]

        # READ
        resp = client.get(f"/api/transactions/{txn_id}")
        assert resp.status_code == 200
        assert resp.get_json()["data"]["amount"] == 250.0

        # UPDATE
        resp = client.put(f"/api/transactions/{txn_id}", json={"description": "Updated description"})
        assert resp.status_code == 200
        assert resp.get_json()["data"]["description"] == "Updated description"

        # DELETE
        resp = client.delete(f"/api/transactions/{txn_id}")
        assert resp.status_code == 200

        # Verify gone
        resp = client.get(f"/api/transactions/{txn_id}")
        assert resp.status_code == 404


class TestAnalyticsUpdatesAfterTransaction:
    """Verify analytics reflect newly created transactions."""

    def test_analytics_updates_after_transaction(self, client, sample_user):
        login(client, "testuser", "Test@1234")
        today = datetime.date.today().isoformat()

        # Get baseline balance
        before = client.get("/api/analytics/dashboard").get_json()["data"]["net_balance"]

        # Add an income transaction
        client.post("/api/transactions/", json={
            "amount": 1000,
            "transaction_type": "income",
            "date": today,
            "description": "Bonus",
        })

        # Analytics should now reflect higher balance (cache was invalidated)
        after = client.get("/api/analytics/dashboard").get_json()["data"]["net_balance"]
        assert after == before + 1000.0


class TestRoleBasedAccessEnforcement:
    def test_viewer_cannot_access_bulk_create(self, client, sample_user):
        login(client, "testuser", "Test@1234")
        resp = client.post("/api/transactions/bulk", json={"transactions": []})
        assert resp.status_code == 403

    def test_viewer_cannot_access_trends(self, client, sample_user):
        login(client, "testuser", "Test@1234")
        resp = client.get("/api/analytics/trends")
        assert resp.status_code == 403

    def test_analyst_can_access_trends(self, client, sample_analyst):
        login(client, "analyst", "Analyst@1234")
        resp = client.get("/api/analytics/trends")
        assert resp.status_code == 200

    def test_viewer_cannot_access_users_list(self, client, sample_user):
        login(client, "testuser", "Test@1234")
        resp = client.get("/api/users/")
        assert resp.status_code == 403

    def test_admin_can_access_users_list(self, client, sample_admin):
        login(client, "adminuser", "Admin@1234")
        resp = client.get("/api/users/")
        assert resp.status_code == 200


class TestExportCsvProducesValidFile:
    def test_export_csv_produces_valid_file(self, client, sample_user, sample_transactions):
        login(client, "testuser", "Test@1234")
        resp = client.get("/api/transactions/export/csv")
        assert resp.status_code == 200
        assert "text/csv" in resp.content_type

        # Parse the CSV and verify headers exist
        content = resp.data.decode("utf-8")
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        assert len(rows) > 0
        assert "amount" in rows[0]
        assert "description" in rows[0]


class TestPaginationWorksCorrectly:
    def test_pagination_works_correctly(self, client, sample_user, sample_transactions):
        login(client, "testuser", "Test@1234")

        # 10 transactions seeded; request page 1 with 3 per page
        resp = client.get("/api/transactions/?page=1&per_page=3")
        assert resp.status_code == 200
        body = resp.get_json()
        assert len(body["data"]) == 3
        assert body["pagination"]["total"] == 10
        assert body["pagination"]["total_pages"] == 4   # ceil(10/3)
        assert body["pagination"]["has_next"] is True
        assert body["pagination"]["has_prev"] is False


class TestConcurrentUserIsolation:
    """User A's transactions must not be visible to User B."""

    def test_concurrent_user_isolation(self, client, sample_user, sample_admin, sample_transactions):
        # Admin logs in – sample_transactions belong to sample_user, not admin
        login(client, "adminuser", "Admin@1234")
        resp = client.get("/api/transactions/")
        assert resp.status_code == 200
        items = resp.get_json()["data"]
        # Admin has no transactions of their own
        assert len(items) == 0
