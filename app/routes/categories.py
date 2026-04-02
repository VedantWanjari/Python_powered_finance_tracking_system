"""
app/routes/categories.py
────────────────────────
Category listing endpoint for the frontend transaction form dropdown.

Returns all categories visible to the authenticated user:
  - system-wide default categories (is_default=True)
  - categories created by the current user
"""

import logging
from flask import Blueprint, g

from app.middleware.auth_middleware import login_required
from app.models.category import Category
from app.utils.response_formatter import success_response

logger = logging.getLogger(__name__)

categories_bp = Blueprint("categories", __name__)


# ── GET /api/categories/ ──────────────────────────────────────────────────────

@categories_bp.route("/", methods=["GET"])
@login_required
def list_categories():
    """
    Return all categories available to the current user.

    Includes:
      - System-wide default categories (is_default=True)
      - Categories created by the current user

    Returns:
        200 with list of category dicts.
    """
    user_id = g.current_user.id
    categories = (
        Category.query
        .filter(
            (Category.is_default == True) |  # noqa: E712
            (Category.created_by == user_id)
        )
        .order_by(Category.name)
        .all()
    )
    return success_response(
        [c.to_dict() for c in categories],
        "Categories retrieved.",
    )
