"""
app/services/analytics_service.py
────────────────────────────────────
Analytics computations with in-memory TTL caching.

All public methods check the cache first; on a miss they query the DB,
store the result, and return it.  Any write operation (create/update/delete
transaction) calls analytics_cache.invalidate_user() to keep data fresh.
"""

import logging
import calendar
import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import func

from app import db
from app.models.transaction import Transaction
from app.models.category import Category
from app.cache.analytics_cache import analytics_cache

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Compute and cache financial analytics for a user."""

    # ── Dashboard ─────────────────────────────────────────────────────────

    @staticmethod
    def get_dashboard(user_id: int) -> dict:
        """
        Return high-level financial summary for the dashboard.

        Includes: total income, total expenses, net balance, transaction count,
        and the 5 most recent transactions.
        """
        cache_key = f"{user_id}:dashboard"
        cached = analytics_cache.get(cache_key)
        if cached:
            return cached

        # ── Aggregate totals ──────────────────────────────────────────────
        totals = (
            db.session.query(
                Transaction.transaction_type,
                func.sum(Transaction.amount).label("total"),
                func.count(Transaction.id).label("count"),
            )
            .filter(Transaction.user_id == user_id)
            .group_by(Transaction.transaction_type)
            .all()
        )

        income = Decimal("0")
        expenses = Decimal("0")
        total_count = 0
        for row in totals:
            if row.transaction_type == "income":
                income = row.total or Decimal("0")
            else:
                expenses = row.total or Decimal("0")
            total_count += row.count

        # ── Recent transactions ───────────────────────────────────────────
        recent = (
            Transaction.query
            .filter_by(user_id=user_id)
            .order_by(Transaction.date.desc(), Transaction.created_at.desc())
            .limit(5)
            .all()
        )

        result = {
            "total_income":      float(income),
            "total_expenses":    float(expenses),
            "net_balance":       float(income - expenses),
            "transaction_count": total_count,
            "recent_transactions": [t.to_dict() for t in recent],
        }

        analytics_cache.set(cache_key, result)
        return result

    # ── Trend analysis ────────────────────────────────────────────────────

    @staticmethod
    def get_trend_analysis(user_id: int, months: int = 6) -> list:
        """
        Return month-by-month income/expense totals for the last *months* months.

        Args:
            user_id: The user to analyse.
            months:  How many months of history to return (default 6).

        Returns:
            List of dicts sorted oldest → newest:
            [{"month": "2024-01", "income": 3000.0, "expenses": 1200.0, "net": 1800.0}, ...]
        """
        cache_key = f"{user_id}:trends:{months}"
        cached = analytics_cache.get(cache_key)
        if cached:
            return cached

        # Build the list of (year, month) tuples to cover
        today = datetime.date.today()
        periods = []
        for i in range(months - 1, -1, -1):   # oldest first
            # Subtract months properly (handles year boundaries)
            month_offset = today.month - i - 1
            year = today.year + month_offset // 12
            month = month_offset % 12 + 1
            periods.append((year, month))

        result = []
        for year, month in periods:
            # First and last day of the month
            first_day = datetime.date(year, month, 1)
            last_day  = datetime.date(year, month, calendar.monthrange(year, month)[1])

            rows = (
                db.session.query(
                    Transaction.transaction_type,
                    func.sum(Transaction.amount).label("total"),
                )
                .filter(
                    Transaction.user_id == user_id,
                    Transaction.date >= first_day,
                    Transaction.date <= last_day,
                )
                .group_by(Transaction.transaction_type)
                .all()
            )

            income = expenses = Decimal("0")
            for row in rows:
                if row.transaction_type == "income":
                    income = row.total or Decimal("0")
                else:
                    expenses = row.total or Decimal("0")

            result.append({
                "month":    f"{year:04d}-{month:02d}",
                "income":   float(income),
                "expenses": float(expenses),
                "net":      float(income - expenses),
            })

        analytics_cache.set(cache_key, result)
        return result

    # ── Category breakdown ────────────────────────────────────────────────

    @staticmethod
    def get_category_breakdown(
        user_id: int,
        start_date: Optional[datetime.date] = None,
        end_date: Optional[datetime.date] = None,
    ) -> list:
        """
        Return spending (expenses only) broken down by category.

        Args:
            user_id:    The user to analyse.
            start_date: Inclusive lower bound on transaction date.
            end_date:   Inclusive upper bound on transaction date.

        Returns:
            List of dicts sorted by total descending:
            [{"category_id": 2, "category_name": "Food", "total": 450.0, "percentage": 30.0}, ...]
        """
        cache_key = f"{user_id}:categories:{start_date}:{end_date}"
        cached = analytics_cache.get(cache_key)
        if cached:
            return cached

        query = (
            db.session.query(
                Transaction.category_id,
                func.sum(Transaction.amount).label("total"),
                func.count(Transaction.id).label("count"),
            )
            .filter(
                Transaction.user_id == user_id,
                Transaction.transaction_type == "expense",
            )
        )
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)

        rows = query.group_by(Transaction.category_id).all()

        # Calculate overall total for percentage computation
        grand_total = sum(r.total or Decimal("0") for r in rows) or Decimal("1")

        result = []
        for row in rows:
            # Fetch category name (may be NULL for uncategorised)
            cat = db.session.get(Category, row.category_id) if row.category_id else None
            total = float(row.total or 0)
            result.append({
                "category_id":   row.category_id,
                "category_name": cat.name if cat else "Uncategorised",
                "total":         total,
                "count":         row.count,
                "percentage":    round(float(row.total or 0) / float(grand_total) * 100, 1),
            })

        # Sort by total descending so top spenders appear first
        result.sort(key=lambda x: x["total"], reverse=True)
        analytics_cache.set(cache_key, result)
        return result

    # ── Monthly summary ───────────────────────────────────────────────────

    @staticmethod
    def get_monthly_summary(user_id: int, year: int, month: int) -> dict:
        """
        Return a detailed breakdown for a specific calendar month.

        Returns totals, daily averages, category breakdown, and transaction list.
        """
        cache_key = f"{user_id}:monthly:{year}:{month}"
        cached = analytics_cache.get(cache_key)
        if cached:
            return cached

        first_day = datetime.date(year, month, 1)
        last_day  = datetime.date(year, month, calendar.monthrange(year, month)[1])

        transactions = (
            Transaction.query
            .filter(
                Transaction.user_id == user_id,
                Transaction.date >= first_day,
                Transaction.date <= last_day,
            )
            .order_by(Transaction.date.asc())
            .all()
        )

        income   = sum(float(t.amount) for t in transactions if t.transaction_type == "income")
        expenses = sum(float(t.amount) for t in transactions if t.transaction_type == "expense")
        days_in_month = calendar.monthrange(year, month)[1]

        result = {
            "year":             year,
            "month":            month,
            "total_income":     income,
            "total_expenses":   expenses,
            "net":              income - expenses,
            "transaction_count": len(transactions),
            "avg_daily_expense": round(expenses / days_in_month, 2),
            "transactions":     [t.to_dict() for t in transactions],
        }

        analytics_cache.set(cache_key, result)
        return result

    # ── Budget status ──────────────────────────────────────────────────────

    @staticmethod
    def get_budget_status(user_id: int, budget_month: str) -> dict:
        """
        Compare actual spending against budget_month tag on transactions.

        Args:
            user_id:      The user to analyse.
            budget_month: "YYYY-MM" string (e.g. "2024-03").

        Returns:
            Dict with actual spending grouped by category for the month.
        """
        cache_key = f"{user_id}:budget:{budget_month}"
        cached = analytics_cache.get(cache_key)
        if cached:
            return cached

        rows = (
            db.session.query(
                Transaction.category_id,
                func.sum(Transaction.amount).label("total"),
            )
            .filter(
                Transaction.user_id == user_id,
                Transaction.budget_month == budget_month,
                Transaction.transaction_type == "expense",
            )
            .group_by(Transaction.category_id)
            .all()
        )

        spending = []
        total_spent = Decimal("0")
        for row in rows:
            cat = db.session.get(Category, row.category_id) if row.category_id else None
            amt = float(row.total or 0)
            total_spent += Decimal(str(amt))
            spending.append({
                "category_id":   row.category_id,
                "category_name": cat.name if cat else "Uncategorised",
                "actual":        amt,
            })

        result = {
            "budget_month":  budget_month,
            "total_spent":   float(total_spent),
            "by_category":   spending,
        }
        analytics_cache.set(cache_key, result)
        return result
