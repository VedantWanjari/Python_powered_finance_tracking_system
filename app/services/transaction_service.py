"""
app/services/transaction_service.py
─────────────────────────────────────
Business logic for transaction CRUD, filtering, and bulk operations.
"""

import datetime
import logging
from typing import Optional, List, Tuple

from app import db
from app.models.transaction import Transaction
from app.services.exceptions import ResourceNotFound, Forbidden
from app.cache.analytics_cache import analytics_cache
from app.utils.audit import write_audit_log

logger = logging.getLogger(__name__)


class TransactionService:
    """Handles all transaction lifecycle operations."""

    # ── Create ────────────────────────────────────────────────────────────

    @staticmethod
    def create_transaction(user_id: int, data: dict) -> Transaction:
        """
        Create a new transaction for *user_id*.

        Args:
            user_id: ID of the authenticated user.
            data:    Validated dict from TransactionCreateSchema.

        Returns:
            The created Transaction.
        """
        txn = Transaction(
            user_id=user_id,
            amount=data["amount"],
            transaction_type=data["transaction_type"],
            category_id=data.get("category_id"),
            date=data["date"],
            description=data["description"],
            notes=data.get("notes"),
            is_recurring=data.get("is_recurring", False),
            recurring_frequency=data.get("recurring_frequency"),
            budget_month=data.get("budget_month"),
        )
        txn.tags = data.get("tags", [])   # uses the property setter (JSON encode)

        db.session.add(txn)
        db.session.commit()

        # Invalidate cached analytics for this user – data has changed
        analytics_cache.invalidate_user(user_id)

        write_audit_log(user_id, "CREATE_TRANSACTION", "Transaction", txn.id, {}, txn.to_dict())
        logger.info("Transaction %s created by user %s", txn.id, user_id)
        return txn

    # ── Read ──────────────────────────────────────────────────────────────

    @staticmethod
    def get_transaction(transaction_id: int, user_id: int) -> Transaction:
        """
        Fetch a single transaction, enforcing ownership.

        Raises:
            ResourceNotFound: If transaction doesn't exist.
            Forbidden:        If it belongs to a different user.
        """
        txn = db.session.get(Transaction, transaction_id)
        if txn is None:
            raise ResourceNotFound(f"Transaction {transaction_id} not found.")
        if txn.user_id != user_id:
            raise Forbidden("You do not have access to this transaction.")
        return txn

    @staticmethod
    def list_transactions(
        user_id: int,
        filters: Optional[dict] = None,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = "date",
        sort_order: str = "desc",
    ) -> Tuple[list, int]:
        """
        Return a paginated, filtered, sorted list of transactions.

        Filter keys (all optional):
          date_from      – ISO date string
          date_to        – ISO date string
          category_id    – integer
          transaction_type – "income" | "expense"
          amount_min     – float
          amount_max     – float
          search         – substring match on description + notes
          tags           – comma-separated tag strings

        Returns:
            Tuple of (list_of_dicts, total_count).
        """
        filters = filters or {}
        query = Transaction.query.filter_by(user_id=user_id)

        # ── Apply filters ─────────────────────────────────────────────────
        if filters.get("date_from"):
            query = query.filter(Transaction.date >= filters["date_from"])
        if filters.get("date_to"):
            query = query.filter(Transaction.date <= filters["date_to"])
        if filters.get("category_id"):
            query = query.filter(Transaction.category_id == filters["category_id"])
        if filters.get("transaction_type"):
            query = query.filter(Transaction.transaction_type == filters["transaction_type"])
        if filters.get("amount_min") is not None:
            query = query.filter(Transaction.amount >= filters["amount_min"])
        if filters.get("amount_max") is not None:
            query = query.filter(Transaction.amount <= filters["amount_max"])
        if filters.get("search"):
            # Full-text search on description and notes
            term = f"%{filters['search']}%"
            query = query.filter(
                db.or_(
                    Transaction.description.ilike(term),
                    Transaction.notes.ilike(term),
                )
            )
        if filters.get("tags"):
            # Filter by tags stored in JSON; simple substring match
            for tag in filters["tags"].split(","):
                tag = tag.strip()
                if tag:
                    query = query.filter(Transaction._tags.contains(tag))

        # ── Sorting ───────────────────────────────────────────────────────
        allowed_sort_cols = {
            "date":    Transaction.date,
            "amount":  Transaction.amount,
            "created": Transaction.created_at,
        }
        sort_col = allowed_sort_cols.get(sort_by, Transaction.date)
        if sort_order == "asc":
            query = query.order_by(sort_col.asc())
        else:
            query = query.order_by(sort_col.desc())

        # ── Paginate ──────────────────────────────────────────────────────
        paginator = query.paginate(page=page, per_page=per_page, error_out=False)
        return [t.to_dict() for t in paginator.items], paginator.total

    # ── Update ────────────────────────────────────────────────────────────

    @staticmethod
    def update_transaction(transaction_id: int, user_id: int, data: dict) -> Transaction:
        """
        Update fields on an existing transaction.

        Only non-None values in *data* are applied (partial update semantics).
        """
        txn = db.session.get(Transaction, transaction_id)
        if txn is None:
            raise ResourceNotFound(f"Transaction {transaction_id} not found.")
        if txn.user_id != user_id:
            raise Forbidden("You do not have access to this transaction.")

        old_data = txn.to_dict()   # snapshot for audit trail

        # Apply each field only when a new value was provided
        updatable = [
            "amount", "transaction_type", "category_id", "date",
            "description", "notes", "is_recurring", "recurring_frequency",
            "budget_month",
        ]
        for field in updatable:
            if data.get(field) is not None:
                setattr(txn, field, data[field])

        if data.get("tags") is not None:
            txn.tags = data["tags"]   # goes through the JSON-encoding setter

        txn.updated_at = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
        db.session.commit()

        analytics_cache.invalidate_user(user_id)  # cache is now stale
        write_audit_log(user_id, "UPDATE_TRANSACTION", "Transaction",
                        transaction_id, old_data, txn.to_dict())
        return txn

    # ── Delete ────────────────────────────────────────────────────────────

    @staticmethod
    def delete_transaction(transaction_id: int, user_id: int) -> None:
        """
        Permanently delete a transaction (hard delete).

        Ownership is verified before deletion.
        """
        txn = db.session.get(Transaction, transaction_id)
        if txn is None:
            raise ResourceNotFound(f"Transaction {transaction_id} not found.")
        if txn.user_id != user_id:
            raise Forbidden("You do not have access to this transaction.")

        old_data = txn.to_dict()
        db.session.delete(txn)
        db.session.commit()

        analytics_cache.invalidate_user(user_id)
        write_audit_log(user_id, "DELETE_TRANSACTION", "Transaction",
                        transaction_id, old_data, {})
        logger.info("Transaction %s deleted by user %s", transaction_id, user_id)

    # ── Bulk create ───────────────────────────────────────────────────────

    @staticmethod
    def bulk_create(user_id: int, transactions: List[dict]) -> List[Transaction]:
        """
        Insert multiple transactions in a single database transaction.

        Args:
            user_id:      ID of the authenticated user.
            transactions: List of validated dicts (same shape as create_transaction).

        Returns:
            List of created Transaction objects.
        """
        created = []
        for item in transactions:
            txn = Transaction(
                user_id=user_id,
                amount=item["amount"],
                transaction_type=item["transaction_type"],
                category_id=item.get("category_id"),
                date=item["date"],
                description=item["description"],
                notes=item.get("notes"),
                is_recurring=item.get("is_recurring", False),
                recurring_frequency=item.get("recurring_frequency"),
            )
            txn.tags = item.get("tags", [])
            db.session.add(txn)
            created.append(txn)

        db.session.commit()
        analytics_cache.invalidate_user(user_id)

        # Write one audit entry per transaction (mirrors single-create behaviour)
        for txn in created:
            write_audit_log(user_id, "BULK_CREATE_TRANSACTION", "Transaction",
                            txn.id, {}, txn.to_dict())

        logger.info("Bulk created %d transactions for user %s", len(created), user_id)
        return created


# ── Private helpers ───────────────────────────────────────────────────────────
# Note: _write_audit has been consolidated into app.utils.audit.write_audit_log.
