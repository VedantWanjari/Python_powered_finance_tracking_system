"""
app/utils/logger.py
───────────────────
Centralised logging configuration.

Creates two handlers:
  1. StreamHandler  – writes to stdout (visible in `flask run` terminal)
  2. FileHandler    – writes to logs/finance_app.log (persistent)

Both handlers share the same structured format so log aggregators
(Splunk, CloudWatch, etc.) can parse them consistently.
"""

import logging
import os
from logging.handlers import RotatingFileHandler   # auto-rotate at max size


# Log format – includes timestamp, level, module, and message
LOG_FORMAT = "%(asctime)s  %(levelname)-8s  [%(name)s:%(lineno)d]  %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Maximum log file size before rotation (5 MB)
MAX_BYTES = 5 * 1024 * 1024
# Keep the 3 most recent rotated files alongside the current one
BACKUP_COUNT = 3
# Directory where log files are stored
LOG_DIR = "logs"


def setup_logger(app) -> None:
    """
    Attach console and file handlers to *app*'s logger.

    Args:
        app: The Flask application instance.
    """
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # ── Console handler ───────────────────────────────────────────────────
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    # Show DEBUG messages only when Flask is in debug mode
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)

    # ── File handler (only in non-testing environments) ───────────────────
    handlers = [console_handler]

    if not app.config.get("TESTING"):
        # Create logs/ directory if it doesn't exist
        os.makedirs(LOG_DIR, exist_ok=True)

        file_handler = RotatingFileHandler(
            filename=os.path.join(LOG_DIR, "finance_app.log"),
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)   # always INFO+ to file
        handlers.append(file_handler)

    # ── Attach handlers to Flask's app.logger ─────────────────────────────
    # Remove default handlers first to avoid duplicate log lines
    app.logger.handlers.clear()
    for handler in handlers:
        app.logger.addHandler(handler)

    # Prevent propagation to the root logger (avoids double output)
    app.logger.propagate = False

    app.logger.info("Logging initialised (env=%s)", app.config.get("ENV", "unknown"))
