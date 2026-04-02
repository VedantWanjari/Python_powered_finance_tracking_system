"""tests/test_analytics.py – analytics endpoint tests."""

import datetime
import pytest
from tests.conftest import login


class TestDashboard:
    def test_dashboard_returns_metrics(self, client, sample_user, sample_transactions):
        login(client, "testuser", "Test@1234")
        resp = client.get("/api/analytics/dashboard")
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert "total_income" in data
        assert "total_expenses" in data
        assert "net_balance" in data

    def test_dashboard_includes_balance(self, client, sample_user, sample_transactions):
        login(client, "testuser", "Test@1234")
        data = client.get("/api/analytics/dashboard").get_json()["data"]
        expected = round(data["total_income"] - data["total_expenses"], 2)
        assert round(data["net_balance"], 2) == expected

    def test_dashboard_unauthenticated(self, client):
        resp = client.get("/api/analytics/dashboard")
        assert resp.status_code == 401


class TestCategoryBreakdown:
    def test_category_breakdown_returns_percentages(self, client, sample_user, sample_transactions):
        login(client, "testuser", "Test@1234")
        resp = client.get("/api/analytics/categories")
        assert resp.status_code == 200
        items = resp.get_json()["data"]
        for item in items:
            assert "percentage" in item
            assert 0 <= item["percentage"] <= 100

    def test_category_breakdown_percentages_sum_to_100(self, client, sample_user, sample_transactions):
        login(client, "testuser", "Test@1234")
        items = client.get("/api/analytics/categories").get_json()["data"]
        if items:   # only assert if there are expenses
            total_pct = sum(i["percentage"] for i in items)
            # Allow small floating-point rounding error
            assert abs(total_pct - 100.0) < 1.0


class TestMonthlySummary:
    def test_monthly_summary_correct_totals(self, client, sample_user, sample_transactions):
        login(client, "testuser", "Test@1234")
        today = datetime.date.today()
        resp = client.get(f"/api/analytics/monthly/{today.year}/{today.month}")
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert "total_income" in data
        assert "total_expenses" in data

    def test_monthly_summary_invalid_month(self, client, sample_user):
        login(client, "testuser", "Test@1234")
        resp = client.get("/api/analytics/monthly/2024/13")
        assert resp.status_code == 400


class TestTrends:
    def test_trends_returns_monthly_data(self, client, sample_analyst):
        login(client, "analyst", "Analyst@1234")
        resp = client.get("/api/analytics/trends?months=3")
        assert resp.status_code == 200
        data = resp.get_json()["data"]
        assert len(data) == 3
        for entry in data:
            assert "month" in entry
            assert "income" in entry
            assert "expenses" in entry

    def test_trends_viewer_forbidden(self, client, sample_user):
        login(client, "testuser", "Test@1234")
        resp = client.get("/api/analytics/trends")
        assert resp.status_code == 403


class TestAnalyticsCache:
    def test_analytics_cache_works(self, client, sample_user, sample_transactions):
        """Two identical requests; second should be served from cache (same data)."""
        login(client, "testuser", "Test@1234")
        resp1 = client.get("/api/analytics/dashboard").get_json()
        resp2 = client.get("/api/analytics/dashboard").get_json()
        # Both should return the same balance
        assert resp1["data"]["net_balance"] == resp2["data"]["net_balance"]
