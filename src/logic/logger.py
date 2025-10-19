"""
Logging configuration for the application.
Logs to both console and file (logs/app.log).
"""
import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(log_level: str = "INFO", log_file: str = "logs/app.log"):
    """
    Configure application logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Path to log file
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)

    # File handler
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        # If file logging fails, continue with console only
        print(f"Warning: Could not set up file logging: {e}")

    # Add console handler
    logger.addHandler(console_handler)

    logger.info("Logging initialized")
    return logger


def setup_worker_logging(log_file: str = "logs/worker.log"):
    """
    Configure logging for Streamlit worker subprocess.

    Creates a separate log file to capture worker process errors that
    would otherwise be lost when running in separate process.

    Args:
        log_file: Path to worker log file

    Returns:
        Logger instance configured for worker process
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Create worker-specific logger
    worker_logger = logging.getLogger('streamlit_worker')
    worker_logger.setLevel(logging.DEBUG)
    worker_logger.handlers.clear()

    # File handler for worker errors
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [WORKER] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        worker_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not set up worker logging: {e}")

    return worker_logger
