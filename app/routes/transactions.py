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

@transactions_bp.route("/", methods=["GET"])
@login_required
def list_transactions():
    """
    List transactions with optional filters and pagination.
    ---
    tags:
      - Transactions
    security:
      - cookieAuth: []
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: per_page
        type: integer
        default: 20
      - in: query
        name: sort_by
        type: string
        enum: [date, amount, created]
        default: date
      - in: query
        name: sort_order
        type: string
        enum: [asc, desc]
        default: desc
      - in: query
        name: date_from
        type: string
        example: "2024-01-01"
      - in: query
        name: date_to
        type: string
        example: "2024-12-31"
      - in: query
        name: transaction_type
        type: string
        enum: [income, expense]
      - in: query
        name: category_id
        type: integer
      - in: query
        name: amount_min
        type: number
      - in: query
        name: amount_max
        type: number
      - in: query
        name: search
        type: string
      - in: query
        name: tags
        type: string
        description: Comma-separated tag names
    responses:
      200:
        description: Paginated list of transactions
      401:
        description: Not authenticated
    """
    try:
        page     = int(request.args.get("page", 1))
        per_page = min(int(request.args.get("per_page", 20)), 100)
    except ValueError:
        return handle_app_error(ValidationError("page and per_page must be integers."))

    sort_by    = request.args.get("sort_by", "date")
    sort_order = request.args.get("sort_order", "desc")

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

@transactions_bp.route("/", methods=["POST"])
@login_required
@validate_schema(TransactionCreateSchema)
def create_transaction():
    """
    Create a new transaction.
    ---
    tags:
      - Transactions
    security:
      - cookieAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - amount
            - transaction_type
            - date
          properties:
            amount:
              type: number
              example: 150.00
            transaction_type:
              type: string
              enum: [income, expense]
              example: expense
            date:
              type: string
              example: "2024-03-15"
            description:
              type: string
              example: Grocery run
            category_id:
              type: integer
              example: 1
            notes:
              type: string
              example: Weekly shop
            tags:
              type: array
              items:
                type: string
              example: ["food", "weekly"]
            is_recurring:
              type: boolean
              example: false
    responses:
      201:
        description: Transaction created
      400:
        description: Validation error
      401:
        description: Not authenticated
    """
    try:
        txn = TransactionService.create_transaction(g.current_user.id, g.validated_data)
        return success_response(txn.to_dict(), "Transaction created.", 201)
    except AppError as exc:
        return handle_app_error(exc)

@transactions_bp.route("/<int:transaction_id>", methods=["GET"])
@login_required
def get_transaction(transaction_id: int):
    """
    Get a single transaction by ID.
    ---
    tags:
      - Transactions
    security:
      - cookieAuth: []
    parameters:
      - in: path
        name: transaction_id
        type: integer
        required: true
    responses:
      200:
        description: Transaction object
      401:
        description: Not authenticated
      403:
        description: Access denied (not the owner)
      404:
        description: Transaction not found
    """
    try:
        txn = TransactionService.get_transaction(transaction_id, g.current_user.id)
        return success_response(txn.to_dict())
    except AppError as exc:
        return handle_app_error(exc)

@transactions_bp.route("/<int:transaction_id>", methods=["PUT"])
@login_required
@validate_schema(TransactionUpdateSchema)
def update_transaction(transaction_id: int):
    """
    Update a transaction. All fields are optional.
    ---
    tags:
      - Transactions
    security:
      - cookieAuth: []
    parameters:
      - in: path
        name: transaction_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            amount:
              type: number
              example: 200.00
            description:
              type: string
              example: Updated grocery run
            category_id:
              type: integer
              example: 2
    responses:
      200:
        description: Transaction updated
      400:
        description: Validation error
      401:
        description: Not authenticated
      404:
        description: Transaction not found
    """
    try:
        txn = TransactionService.update_transaction(
            transaction_id, g.current_user.id, g.validated_data
        )
        return success_response(txn.to_dict(), "Transaction updated.")
    except AppError as exc:
        return handle_app_error(exc)

@transactions_bp.route("/<int:transaction_id>", methods=["DELETE"])
@login_required
def delete_transaction(transaction_id: int):
    """
    Permanently delete a transaction.
    ---
    tags:
      - Transactions
    security:
      - cookieAuth: []
    parameters:
      - in: path
        name: transaction_id
        type: integer
        required: true
    responses:
      200:
        description: Transaction deleted
      401:
        description: Not authenticated
      404:
        description: Transaction not found
    """
    try:
        TransactionService.delete_transaction(transaction_id, g.current_user.id)
        return success_response(None, "Transaction deleted.")
    except AppError as exc:
        return handle_app_error(exc)

@transactions_bp.route("/bulk", methods=["POST"])
@analyst_required
def bulk_create():
    """
    Bulk create multiple transactions at once. Requires analyst or admin role.
    ---
    tags:
      - Transactions
    security:
      - cookieAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - transactions
          properties:
            transactions:
              type: array
              items:
                type: object
                required:
                  - amount
                  - transaction_type
                  - date
                properties:
                  amount:
                    type: number
                    example: 200
                  transaction_type:
                    type: string
                    enum: [income, expense]
                  date:
                    type: string
                    example: "2024-03-01"
                  description:
                    type: string
                    example: Coffee
    responses:
      201:
        description: Transactions created
      400:
        description: Validation error in one or more items
      401:
        description: Not authenticated
      403:
        description: Analyst or admin role required
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
        except Exception as e:
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

@transactions_bp.route("/export/csv", methods=["GET"])
@login_required
def export_csv():
    """
    Download transactions as a CSV file.
    ---
    tags:
      - Transactions
    security:
      - cookieAuth: []
    produces:
      - text/csv
    parameters:
      - in: query
        name: date_from
        type: string
        example: "2024-01-01"
      - in: query
        name: date_to
        type: string
        example: "2024-12-31"
      - in: query
        name: transaction_type
        type: string
        enum: [income, expense]
      - in: query
        name: category_id
        type: integer
    responses:
      200:
        description: CSV file download
      401:
        description: Not authenticated
    """
    filters = {k: request.args.get(k) for k in [
        "date_from", "date_to", "category_id", "transaction_type",
    ] if request.args.get(k)}
    return ExportService.export_csv(g.current_user.id, filters)

@transactions_bp.route("/export/json", methods=["GET"])
@login_required
def export_json():
    """
    Download transactions as a JSON file.
    ---
    tags:
      - Transactions
    security:
      - cookieAuth: []
    parameters:
      - in: query
        name: date_from
        type: string
        example: "2024-01-01"
      - in: query
        name: date_to
        type: string
        example: "2024-12-31"
      - in: query
        name: transaction_type
        type: string
        enum: [income, expense]
      - in: query
        name: category_id
        type: integer
    responses:
      200:
        description: JSON file download
      401:
        description: Not authenticated
    """
    filters = {k: request.args.get(k) for k in [
        "date_from", "date_to", "category_id", "transaction_type",
    ] if request.args.get(k)}
    return ExportService.export_json(g.current_user.id, filters)

@transactions_bp.route("/search", methods=["GET"])
@login_required
def search_transactions():
    """
    Full-text search on transaction description and notes.
    ---
    tags:
      - Transactions
    security:
      - cookieAuth: []
    parameters:
      - in: query
        name: q
        type: string
        required: true
        example: grocery
      - in: query
        name: page
        type: integer
        default: 1
      - in: query
        name: per_page
        type: integer
        default: 20
    responses:
      200:
        description: Paginated search results
      400:
        description: Missing query parameter
      401:
        description: Not authenticated
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
