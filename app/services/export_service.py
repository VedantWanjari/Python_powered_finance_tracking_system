"""
app/services/export_service.py
────────────────────────────────
Generate CSV and JSON exports of transaction data.
"""

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
    """Handles exporting transaction data to various formats."""

    @staticmethod
    def export_csv(user_id: int, filters: Optional[dict] = None) -> Response:
        """
        Generate a CSV file of the user's transactions.

        Args:
            user_id:  ID of the authenticated user.
            filters:  Optional filter dict (same keys as list_transactions).

        Returns:
            Flask Response with Content-Type: text/csv and download headers.
        """
        # Fetch all matching transactions (no pagination for exports)
        transactions, _ = TransactionService.list_transactions(
            user_id=user_id,
            filters=filters or {},
            page=1,
            per_page=10_000,   # large limit for export
        )

        # ── Build CSV in memory ───────────────────────────────────────────
        output = io.StringIO()   # in-memory buffer (no temp file needed)
        fieldnames = [
            "id", "date", "transaction_type", "amount",
            "category_name", "description", "notes", "tags",
            "is_recurring", "recurring_frequency", "created_at",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()

        for txn in transactions:
            # Flatten tags list to comma-separated string for CSV
            txn["tags"] = ", ".join(txn.get("tags", []))
            writer.writerow(txn)

        # ── Build response ────────────────────────────────────────────────
        filename = f"transactions_{datetime.datetime.now(datetime.UTC).strftime('%Y%m%d_%H%M%S')}.csv"
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    @staticmethod
    def export_json(user_id: int, filters: Optional[dict] = None) -> Response:
        """
        Generate a JSON export of the user's transactions.

        Returns:
            Flask Response with Content-Type: application/json.
        """
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
