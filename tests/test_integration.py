import csv
import datetime
import io
import pytest
from tests.conftest import login

class TestFullTransactionLifecycle:

    def test_full_transaction_lifecycle(self, client, sample_user, sample_category):
        login(client, "testuser", "Test@1234")
        today = datetime.date.today().isoformat()

        resp = client.post("/api/transactions/", json={
            "amount": 250.00,
            "transaction_type": "expense",
            "date": today,
            "description": "Original description",
            "category_id": sample_category.id,
        })
        assert resp.status_code == 201
        txn_id = resp.get_json()["data"]["id"]

        resp = client.get(f"/api/transactions/{txn_id}")
        assert resp.status_code == 200
        assert resp.get_json()["data"]["amount"] == 250.0

        resp = client.put(f"/api/transactions/{txn_id}", json={"description": "Updated description"})
        assert resp.status_code == 200
        assert resp.get_json()["data"]["description"] == "Updated description"

        resp = client.delete(f"/api/transactions/{txn_id}")
        assert resp.status_code == 200

        resp = client.get(f"/api/transactions/{txn_id}")
        assert resp.status_code == 404

class TestAnalyticsUpdatesAfterTransaction:

    def test_analytics_updates_after_transaction(self, client, sample_user):
        login(client, "testuser", "Test@1234")
        today = datetime.date.today().isoformat()

        before = client.get("/api/analytics/dashboard").get_json()["data"]["net_balance"]

        client.post("/api/transactions/", json={
            "amount": 1000,
            "transaction_type": "income",
            "date": today,
            "description": "Bonus",
        })

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

        content = resp.data.decode("utf-8")
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        assert len(rows) > 0
        assert "amount" in rows[0]
        assert "description" in rows[0]

class TestPaginationWorksCorrectly:
    def test_pagination_works_correctly(self, client, sample_user, sample_transactions):
        login(client, "testuser", "Test@1234")

        resp = client.get("/api/transactions/?page=1&per_page=3")
        assert resp.status_code == 200
        body = resp.get_json()
        assert len(body["data"]) == 3
        assert body["pagination"]["total"] == 10
        assert body["pagination"]["total_pages"] == 4
        assert body["pagination"]["has_next"] is True
        assert body["pagination"]["has_prev"] is False

class TestConcurrentUserIsolation:

    def test_concurrent_user_isolation(self, client, sample_user, sample_admin, sample_transactions):
        login(client, "adminuser", "Admin@1234")
        resp = client.get("/api/transactions/")
        assert resp.status_code == 200
        items = resp.get_json()["data"]
        assert len(items) == 0
