import logging
import os

log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_name, logging.INFO)

logging.basicConfig(
    level=log_level,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("flavour_fleet")
