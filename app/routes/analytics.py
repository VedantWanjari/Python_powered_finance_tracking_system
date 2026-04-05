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

@analytics_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    """
    High-level financial summary (KPIs). Cached for 5 minutes.
    ---
    tags:
      - Analytics
    security:
      - cookieAuth: []
    responses:
      200:
        description: Dashboard KPI data
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                total_income:
                  type: number
                  example: 5000.00
                total_expenses:
                  type: number
                  example: 1200.00
                net_balance:
                  type: number
                  example: 3800.00
                transaction_count:
                  type: integer
                  example: 15
      401:
        description: Not authenticated
    """
    try:
        data = AnalyticsService.get_dashboard(g.current_user.id)
        return success_response(data, "Dashboard data retrieved.")
    except AppError as exc:
        return handle_app_error(exc)

@analytics_bp.route("/trends", methods=["GET"])
@analyst_required
def trends():
    """
    Month-over-month income/expense trends. Requires analyst or admin role.
    ---
    tags:
      - Analytics
    security:
      - cookieAuth: []
    parameters:
      - in: query
        name: months
        type: integer
        default: 6
        description: Number of past months to include (1–24)
    responses:
      200:
        description: Trend data per month
      400:
        description: Invalid months value
      401:
        description: Not authenticated
      403:
        description: Analyst or admin role required
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

@analytics_bp.route("/categories", methods=["GET"])
@login_required
def category_breakdown():
    """
    Expense breakdown by category with optional date range filter.
    ---
    tags:
      - Analytics
    security:
      - cookieAuth: []
    parameters:
      - in: query
        name: start_date
        type: string
        example: "2024-01-01"
      - in: query
        name: end_date
        type: string
        example: "2024-03-31"
    responses:
      200:
        description: Category breakdown data
      400:
        description: Invalid date format
      401:
        description: Not authenticated
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

@analytics_bp.route("/monthly/<int:year>/<int:month>", methods=["GET"])
@login_required
def monthly_summary(year: int, month: int):
    """
    Monthly income/expense summary for a specific year and month.
    ---
    tags:
      - Analytics
    security:
      - cookieAuth: []
    parameters:
      - in: path
        name: year
        type: integer
        required: true
        example: 2024
      - in: path
        name: month
        type: integer
        required: true
        example: 3
    responses:
      200:
        description: Monthly summary data
      400:
        description: Invalid month value
      401:
        description: Not authenticated
    """
    if not (1 <= month <= 12):
        return handle_app_error(ValidationError("month must be between 1 and 12."))

    try:
        data = AnalyticsService.get_monthly_summary(g.current_user.id, year, month)
        return success_response(data, f"Monthly summary for {year}-{month:02d}.")
    except AppError as exc:
        return handle_app_error(exc)

@analytics_bp.route("/budget", methods=["GET"])
@login_required
def budget_status():
    """
    Budget vs actual spending for a given month.
    ---
    tags:
      - Analytics
    security:
      - cookieAuth: []
    parameters:
      - in: query
        name: month
        type: string
        required: true
        example: "2024-03"
        description: Month in YYYY-MM format
    responses:
      200:
        description: Budget status data
      400:
        description: Missing or invalid month parameter
      401:
        description: Not authenticated
    """
    budget_month = request.args.get("month", "").strip()
    if not budget_month:
        return handle_app_error(ValidationError("Query param 'month' (YYYY-MM) is required."))

    try:
        data = AnalyticsService.get_budget_status(g.current_user.id, budget_month)
        return success_response(data, f"Budget status for {budget_month}.")
    except AppError as exc:
        return handle_app_error(exc)

@analytics_bp.route("/report", methods=["GET"])
@analyst_required
def report():
    """
    Comprehensive report combining dashboard, trends and category breakdown. Requires analyst or admin role.
    ---
    tags:
      - Analytics
    security:
      - cookieAuth: []
    parameters:
      - in: query
        name: months
        type: integer
        default: 6
        description: Number of past months to include in trend data
    responses:
      200:
        description: Full report data
      401:
        description: Not authenticated
      403:
        description: Analyst or admin role required
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
