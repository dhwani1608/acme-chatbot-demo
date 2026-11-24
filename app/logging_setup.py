import logging
from logging.handlers import TimedRotatingFileHandler

from .config import LOG_RETENTION_DAYS
from .privacy import RedactingFilter


def configure_logging() -> None:
    # Daily rotation, 180 files kept = 180 days (CERT-In rolling window).
    handler = TimedRotatingFileHandler("logs/app.log", when="midnight", backupCount=180, utc=True)
    handler.addFilter(RedactingFilter())
    console = logging.StreamHandler()
    console.addFilter(RedactingFilter())
    logging.basicConfig(level=logging.INFO, handlers=[handler, console])
    logging.getLogger("demo").info("log retention days: %s", LOG_RETENTION_DAYS)
