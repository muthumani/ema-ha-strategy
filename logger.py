import logging
import sys
import json
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Union
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme

class StructuredLogFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            'timestamp': self.formatTime(record, self.datefmt),
            'level': record.levelname,
            'name': record.name,
            'message': record.getMessage(),
        }

        # Add exception info if available
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }

        # Add extra fields if available
        if hasattr(record, 'extra'):
            log_data.update(record.extra)

        return json.dumps(log_data)


def log_with_context(logger: logging.Logger, level: int, msg: str, extra: Optional[Dict[str, Any]] = None) -> None:
    """Log a message with additional context"""
    if extra is None:
        extra = {}

    # Add extra fields to the record
    logger_extra = {'extra': extra}
    logger.log(level, msg, extra=logger_extra)


def setup_logger(name: str = "ema_ha_strategy", log_level: int = logging.INFO,
                log_to_file: bool = True, structured: bool = True) -> logging.Logger:
    """
    Set up and configure logger with console and file handlers

    Args:
        name: Logger name
        log_level: Logging level (default: INFO)
        log_to_file: Whether to log to file (default: True)
        structured: Whether to use structured JSON logging for file output (default: True)

    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.handlers = []  # Clear existing handlers

    # Create console handler with rich formatting
    custom_theme = Theme({
        "info": "green",
        "warning": "yellow",
        "error": "bold red",
        "critical": "bold white on red"
    })
    console = Console(theme=custom_theme)
    console_handler = RichHandler(console=console, show_time=True, show_path=False)
    console_handler.setLevel(log_level)
    logger.addHandler(console_handler)

    # Create file handler if requested
    if log_to_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"{name}_{timestamp}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)

        # Create formatter
        if structured:
            formatter = StructuredLogFormatter()
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Add convenience methods for structured logging
    logger.info_with_context = lambda msg, extra=None: log_with_context(logger, logging.INFO, msg, extra)
    logger.warning_with_context = lambda msg, extra=None: log_with_context(logger, logging.WARNING, msg, extra)
    logger.error_with_context = lambda msg, extra=None: log_with_context(logger, logging.ERROR, msg, extra)
    logger.debug_with_context = lambda msg, extra=None: log_with_context(logger, logging.DEBUG, msg, extra)
    logger.critical_with_context = lambda msg, extra=None: log_with_context(logger, logging.CRITICAL, msg, extra)

    return logger
