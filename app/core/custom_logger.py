import os
from datetime import timedelta
from loguru import logger


LOG_DIR = "/app/logs"
try:
    os.makedirs(LOG_DIR, exist_ok=True)
    logger.info(f"Logs directory setuped: {os.path.abspath(LOG_DIR)}")
except Exception as e:
    logger.error(f"Error in logs directory creation: {e}")

logger.remove()

logger.add(
    sink=lambda msg: print(msg, end=""),
    level="INFO",
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)

logger.add(
    sink=f"{LOG_DIR}/logs.log",
    level="DEBUG",
    filter=lambda record: record["level"].name in {"WARNING", "ERROR", "SUCCESS"},
    rotation=timedelta(days=1),
    retention=timedelta(days=7),
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)