import csv
import io
import json
import datetime
import logging
from typing import Optional

from flask import Response

from app.services.transaction_service import TransactionService

logger = logging.getLogger(__name__)

class ExportService:

    @staticmethod
    def export_csv(user_id: int, filters: Optional[dict] = None) -> Response:
        transactions, _ = TransactionService.list_transactions(
            user_id=user_id,
            filters=filters or {},
            page=1,
            per_page=10_000,
        )

        output = io.StringIO()
        fieldnames = [
            "id", "date", "transaction_type", "amount",
            "category_name", "description", "notes", "tags",
            "is_recurring", "recurring_frequency", "created_at",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()

        for txn in transactions:
            txn["tags"] = ", ".join(txn.get("tags", []))
            writer.writerow(txn)

        filename = f"transactions_{datetime.datetime.now(datetime.UTC).strftime('%Y%m%d_%H%M%S')}.csv"
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    @staticmethod
    def export_json(user_id: int, filters: Optional[dict] = None) -> Response:
        transactions, total = TransactionService.list_transactions(
            user_id=user_id,
            filters=filters or {},
            page=1,
            per_page=10_000,
        )

        payload = {
            "exported_at":       datetime.datetime.now(datetime.UTC).replace(tzinfo=None).isoformat() + "Z",
            "total":             total,
            "transactions":      transactions,
        }

        filename = f"transactions_{datetime.datetime.now(datetime.UTC).strftime('%Y%m%d_%H%M%S')}.json"
        return Response(
            json.dumps(payload, indent=2, default=str),
            mimetype="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
