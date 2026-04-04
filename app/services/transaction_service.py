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

    @staticmethod
    def create_transaction(user_id: int, data: dict) -> Transaction:
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
        txn.tags = data.get("tags", [])

        db.session.add(txn)
        db.session.commit()

        analytics_cache.invalidate_user(user_id)

        write_audit_log(user_id, "CREATE_TRANSACTION", "Transaction", txn.id, {}, txn.to_dict())
        logger.info("Transaction %s created by user %s", txn.id, user_id)
        return txn

    @staticmethod
    def get_transaction(transaction_id: int, user_id: int) -> Transaction:
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
        filters = filters or {}
        query = Transaction.query.filter_by(user_id=user_id)

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
            term = f"%{filters['search']}%"
            query = query.filter(
                db.or_(
                    Transaction.description.ilike(term),
                    Transaction.notes.ilike(term),
                )
            )
        if filters.get("tags"):
            for tag in filters["tags"].split(","):
                tag = tag.strip()
                if tag:
                    query = query.filter(Transaction._tags.contains(tag))

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

        paginator = query.paginate(page=page, per_page=per_page, error_out=False)
        return [t.to_dict() for t in paginator.items], paginator.total

    @staticmethod
    def update_transaction(transaction_id: int, user_id: int, data: dict) -> Transaction:
        txn = db.session.get(Transaction, transaction_id)
        if txn is None:
            raise ResourceNotFound(f"Transaction {transaction_id} not found.")
        if txn.user_id != user_id:
            raise Forbidden("You do not have access to this transaction.")

        old_data = txn.to_dict()

        updatable = [
            "amount", "transaction_type", "category_id", "date",
            "description", "notes", "is_recurring", "recurring_frequency",
            "budget_month",
        ]
        for field in updatable:
            if data.get(field) is not None:
                setattr(txn, field, data[field])

        if data.get("tags") is not None:
            txn.tags = data["tags"]

        txn.updated_at = datetime.datetime.now(datetime.UTC).replace(tzinfo=None)
        db.session.commit()

        analytics_cache.invalidate_user(user_id)
        write_audit_log(user_id, "UPDATE_TRANSACTION", "Transaction",
                        transaction_id, old_data, txn.to_dict())
        return txn

    @staticmethod
    def delete_transaction(transaction_id: int, user_id: int) -> None:
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

    @staticmethod
    def bulk_create(user_id: int, transactions: List[dict]) -> List[Transaction]:
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

        for txn in created:
            write_audit_log(user_id, "BULK_CREATE_TRANSACTION", "Transaction",
                            txn.id, {}, txn.to_dict())

        logger.info("Bulk created %d transactions for user %s", len(created), user_id)
        return created
