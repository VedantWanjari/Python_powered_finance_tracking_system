import logging
import os
from logging.handlers import RotatingFileHandler

LOG_FORMAT = "%(asctime)s  %(levelname)-8s  [%(name)s:%(lineno)d]  %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

MAX_BYTES = 5 * 1024 * 1024
BACKUP_COUNT = 3
LOG_DIR = "logs"

def setup_logger(app) -> None:
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)

    handlers = [console_handler]

    if not app.config.get("TESTING"):
        os.makedirs(LOG_DIR, exist_ok=True)

        file_handler = RotatingFileHandler(
            filename=os.path.join(LOG_DIR, "finance_app.log"),
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        handlers.append(file_handler)

    app.logger.handlers.clear()
    for handler in handlers:
        app.logger.addHandler(handler)

    app.logger.propagate = False

    app.logger.info("Logging initialised (env=%s)", app.config.get("ENV", "unknown"))
