"""
app/routes/transactions.py
───────────────────────────
Transaction CRUD, search, bulk create, and export endpoints.

All endpoints live under /api/transactions.
"""

import logging
from flask import Blueprint, request, g

from app.middleware.auth_middleware import login_required
from app.middleware.role_middleware import analyst_required
from app.middleware.error_handler import handle_app_error
from app.validators.transaction_validator import (
    TransactionCreateSchema, TransactionUpdateSchema,
)
from app.validators.decorators import validate_schema
from app.services.transaction_service import TransactionService
from app.services.export_service import ExportService
from app.services.exceptions import AppError, ValidationError
from app.utils.response_formatter import success_response, paginated_response

logger = logging.getLogger(__name__)
transactions_bp = Blueprint("transactions", __name__)


# ── GET /api/transactions ─────────────────────────────────────────────────────

@transactions_bp.route("/", methods=["GET"])
@login_required
def list_transactions():
    """
    List the authenticated user's transactions with optional filters.

    Query params:
        page, per_page, sort_by, sort_order,
        date_from, date_to, category_id, transaction_type,
        amount_min, amount_max, search, tags
    """
    # Extract pagination / sorting params (with safe defaults)
    try:
        page     = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("per_page", 20)), 100)
    except ValueError:
        return handle_app_error(ValidationError("page and per_page must be integers."))

    sort_by    = request.args.get("sort_by", "date")
    sort_order = request.args.get("sort_order", "desc")

    # Collect all possible filter keys from query string
    filters = {k: request.args.get(k) for k in [
        "date_from", "date_to", "category_id", "transaction_type",
        "amount_min", "amount_max", "search", "tags",
    ] if request.args.get(k)}

    transactions, total = TransactionService.list_transactions(
        user_id=g.current_user.id,
        filters=filters,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return paginated_response(transactions, total, page, per_page)


# ── POST /api/transactions ────────────────────────────────────────────────────

@transactions_bp.route("/", methods=["POST"])
@login_required
@validate_schema(TransactionCreateSchema)
def create_transaction():
    """
    Create a new transaction for the authenticated user.

    Request body: TransactionCreateSchema fields.
    """
    try:
        txn = TransactionService.create_transaction(g.current_user.id, g.validated_data)
        return success_response(txn.to_dict(), "Transaction created.", 201)
    except AppError as exc:
        return handle_app_error(exc)


# ── GET /api/transactions/<id> ────────────────────────────────────────────────

@transactions_bp.route("/<int:transaction_id>", methods=["GET"])
@login_required
def get_transaction(transaction_id: int):
    """Fetch a single transaction by ID (must belong to authenticated user)."""
    try:
        txn = TransactionService.get_transaction(transaction_id, g.current_user.id)
        return success_response(txn.to_dict())
    except AppError as exc:
        return handle_app_error(exc)


# ── PUT /api/transactions/<id> ────────────────────────────────────────────────

@transactions_bp.route("/<int:transaction_id>", methods=["PUT"])
@login_required
@validate_schema(TransactionUpdateSchema)
def update_transaction(transaction_id: int):
    """Update an existing transaction (must belong to authenticated user)."""
    try:
        txn = TransactionService.update_transaction(
            transaction_id, g.current_user.id, g.validated_data
        )
        return success_response(txn.to_dict(), "Transaction updated.")
    except AppError as exc:
        return handle_app_error(exc)


# ── DELETE /api/transactions/<id> ─────────────────────────────────────────────

@transactions_bp.route("/<int:transaction_id>", methods=["DELETE"])
@login_required
def delete_transaction(transaction_id: int):
    """Delete a transaction permanently (must belong to authenticated user)."""
    try:
        TransactionService.delete_transaction(transaction_id, g.current_user.id)
        return success_response(None, "Transaction deleted.")
    except AppError as exc:
        return handle_app_error(exc)


# ── POST /api/transactions/bulk ───────────────────────────────────────────────

@transactions_bp.route("/bulk", methods=["POST"])
@analyst_required
def bulk_create():
    """
    Bulk-create transactions (analyst + admin only).

    Request body:
        { "transactions": [ <TransactionCreateSchema>, ... ] }
    """
    if not request.is_json:
        return handle_app_error(ValidationError("Content-Type must be application/json."))

    data = request.get_json()
    items = data.get("transactions", [])
    if not isinstance(items, list) or not items:
        return handle_app_error(ValidationError("'transactions' must be a non-empty list."))

    schema = TransactionCreateSchema()
    validated_items = []
    errors = {}
    for idx, item in enumerate(items):
        try:
            validated_items.append(schema.load(item))
        except Exception as e:   # noqa: BLE001
            errors[idx] = str(e)

    if errors:
        return handle_app_error(ValidationError("Some transactions failed validation.", errors))

    try:
        created = TransactionService.bulk_create(g.current_user.id, validated_items)
        return success_response(
            {"created_count": len(created)},
            f"{len(created)} transactions created.",
            201,
        )
    except AppError as exc:
        return handle_app_error(exc)


# ── GET /api/transactions/export/csv ─────────────────────────────────────────

@transactions_bp.route("/export/csv", methods=["GET"])
@login_required
def export_csv():
    """Download all matching transactions as a CSV file."""
    filters = {k: request.args.get(k) for k in [
        "date_from", "date_to", "category_id", "transaction_type",
    ] if request.args.get(k)}
    return ExportService.export_csv(g.current_user.id, filters)


# ── GET /api/transactions/export/json ────────────────────────────────────────

@transactions_bp.route("/export/json", methods=["GET"])
@login_required
def export_json():
    """Download all matching transactions as a JSON file."""
    filters = {k: request.args.get(k) for k in [
        "date_from", "date_to", "category_id", "transaction_type",
    ] if request.args.get(k)}
    return ExportService.export_json(g.current_user.id, filters)


# ── GET /api/transactions/search ─────────────────────────────────────────────

@transactions_bp.route("/search", methods=["GET"])
@login_required
def search_transactions():
    """
    Full-text search on description and notes.

    Query params:
        q (required) – search term
        page, per_page
    """
    search_term = request.args.get("q", "").strip()
    if not search_term:
        return handle_app_error(ValidationError("Query parameter 'q' is required."))

    try:
        page     = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("per_page", 20)), 100)
    except ValueError:
        return handle_app_error(ValidationError("page and per_page must be integers."))

    transactions, total = TransactionService.list_transactions(
        user_id=g.current_user.id,
        filters={"search": search_term},
        page=page,
        per_page=per_page,
    )
    return paginated_response(transactions, total, page, per_page, f"Search results for '{search_term}'")
