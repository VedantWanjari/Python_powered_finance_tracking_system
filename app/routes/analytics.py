"""
app/routes/analytics.py
────────────────────────
Analytics and reporting endpoints.

All endpoints live under /api/analytics.
"""

import datetime
import logging
from flask import Blueprint, request, g

from app.middleware.auth_middleware import login_required
from app.middleware.role_middleware import analyst_required
from app.middleware.error_handler import handle_app_error
from app.services.analytics_service import AnalyticsService
from app.services.exceptions import AppError, ValidationError
from app.utils.response_formatter import success_response

logger = logging.getLogger(__name__)
analytics_bp = Blueprint("analytics", __name__)


# ── GET /api/analytics/dashboard ─────────────────────────────────────────────

@analytics_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    """
    Return high-level financial summary: balance, income, expenses, recent transactions.
    Response is cached for 5 minutes.
    """
    try:
        data = AnalyticsService.get_dashboard(g.current_user.id)
        return success_response(data, "Dashboard data retrieved.")
    except AppError as exc:
        return handle_app_error(exc)


# ── GET /api/analytics/trends ────────────────────────────────────────────────

@analytics_bp.route("/trends", methods=["GET"])
@analyst_required
def trends():
    """
    Month-over-month income/expense trend (analyst + admin only).

    Query params:
        months (int, default 6) – how many months of history to include
    """
    try:
        months = int(request.args.get("months", 6))
        if months < 1 or months > 24:
            raise ValidationError("months must be between 1 and 24.")
    except (TypeError, ValueError):
        return handle_app_error(ValidationError("months must be an integer."))

    try:
        data = AnalyticsService.get_trend_analysis(g.current_user.id, months)
        return success_response(data, f"Trend data for last {months} months.")
    except AppError as exc:
        return handle_app_error(exc)


# ── GET /api/analytics/categories ────────────────────────────────────────────

@analytics_bp.route("/categories", methods=["GET"])
@login_required
def category_breakdown():
    """
    Return spending breakdown by category with percentages.

    Query params (optional):
        start_date (YYYY-MM-DD), end_date (YYYY-MM-DD)
    """
    try:
        start_date = (
            datetime.date.fromisoformat(request.args["start_date"])
            if "start_date" in request.args else None
        )
        end_date = (
            datetime.date.fromisoformat(request.args["end_date"])
            if "end_date" in request.args else None
        )
    except ValueError:
        return handle_app_error(ValidationError("Dates must be in YYYY-MM-DD format."))

    try:
        data = AnalyticsService.get_category_breakdown(
            g.current_user.id, start_date, end_date
        )
        return success_response(data, "Category breakdown retrieved.")
    except AppError as exc:
        return handle_app_error(exc)


# ── GET /api/analytics/monthly/<year>/<month> ─────────────────────────────────

@analytics_bp.route("/monthly/<int:year>/<int:month>", methods=["GET"])
@login_required
def monthly_summary(year: int, month: int):
    """
    Return a detailed summary for a specific calendar month.

    URL params:
        year  – 4-digit year
        month – 1-12
    """
    if not (1 <= month <= 12):
        return handle_app_error(ValidationError("month must be between 1 and 12."))

    try:
        data = AnalyticsService.get_monthly_summary(g.current_user.id, year, month)
        return success_response(data, f"Monthly summary for {year}-{month:02d}.")
    except AppError as exc:
        return handle_app_error(exc)


# ── GET /api/analytics/budget ─────────────────────────────────────────────────

@analytics_bp.route("/budget", methods=["GET"])
@login_required
def budget_status():
    """
    Return actual spending for a budget month.

    Query params:
        month (required) – "YYYY-MM" string
    """
    budget_month = request.args.get("month", "").strip()
    if not budget_month:
        return handle_app_error(ValidationError("Query param 'month' (YYYY-MM) is required."))

    try:
        data = AnalyticsService.get_budget_status(g.current_user.id, budget_month)
        return success_response(data, f"Budget status for {budget_month}.")
    except AppError as exc:
        return handle_app_error(exc)


# ── GET /api/analytics/report ─────────────────────────────────────────────────

@analytics_bp.route("/report", methods=["GET"])
@analyst_required
def report():
    """
    Comprehensive financial report combining dashboard + trends + category breakdown.
    Analyst + admin only.
    """
    try:
        months = int(request.args.get("months", 6))
    except (TypeError, ValueError):
        months = 6

    try:
        dashboard_data = AnalyticsService.get_dashboard(g.current_user.id)
        trend_data     = AnalyticsService.get_trend_analysis(g.current_user.id, months)
        category_data  = AnalyticsService.get_category_breakdown(g.current_user.id)

        report_data = {
            "generated_at": datetime.datetime.now(datetime.UTC).replace(tzinfo=None).isoformat() + "Z",
            "summary":      dashboard_data,
            "trends":       trend_data,
            "categories":   category_data,
        }
        return success_response(report_data, "Report generated.")
    except AppError as exc:
        return handle_app_error(exc)
