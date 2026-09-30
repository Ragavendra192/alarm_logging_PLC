import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


def setup_logger():
    """
    Configure application logging.

    Logs are written to:
        logs/collector.log

    A new log file is created every day.
    """

    # Create logs directory in application root
    if getattr(sys, "frozen", False):
        log_directory = str(Path(sys.executable).resolve().parent / "logs")
    else:
        log_directory = str(Path(__file__).resolve().parent.parent / "logs")
    os.makedirs(log_directory, exist_ok=True)


    logger = logging.getLogger("PLCDataCollector")
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers if setup_logger() is called multiple times
    if logger.handlers:
        return logger

    # Log format
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # -----------------------------
    # Console Handler
    # -----------------------------
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # -----------------------------
    # File Handler
    # -----------------------------
    log_file = os.path.join(log_directory, "collector.log")

    file_handler = TimedRotatingFileHandler(
        log_file,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )

    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger