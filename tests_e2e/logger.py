import logging
import sys
from pathlib import Path
from typing import Optional

from rich.logging import RichHandler

from config import get_config


def get_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """
    Get or create a logger with the specified name and configuration.

    Args:
        name: Logger name (typically __name__ of the calling module)
        log_file: Optional file path for logging output. If None, logs only to console.

    Returns:
        Configured logger instance
    """
    # Get configuration
    config = get_config()

    # Create logger
    logger = logging.getLogger(name)

    # Return existing logger if already configured
    if logger.handlers:
        return logger

    # Set log level from configuration
    logger.setLevel(config.log_level)

    # Create formatters
    console_format = "%(message)s"
    file_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Console handler with rich formatting
    console_handler = RichHandler(
        rich_tracebacks=True,
        show_time=False,
        show_path=False
    )
    console_handler.setFormatter(logging.Formatter(console_format))
    logger.addHandler(console_handler)

    # File handler if log file specified
    if log_file:
        # Create logs directory if needed
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(file_format))
        logger.addHandler(file_handler)

    # Don't propagate to root logger
    logger.propagate = False

    return logger


def setup_global_logging(log_file: Optional[str] = None) -> None:
    """
    Set up global logging configuration.

    Args:
        log_file: Optional file path for logging output
    """
    # Set up root logger
    root_logger = get_logger("root", log_file)

    # Capture warnings
    logging.captureWarnings(True)

    # Handle uncaught exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Handle keyboard interrupt normally
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        root_logger.error(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = handle_exception


if __name__ == "__main__":
    # Example usage
    logger = get_logger(__name__, "logs/test.log")
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    try:
        raise ValueError("Test exception")
    except Exception:
        logger.exception("Caught an exception")
