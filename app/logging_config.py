'''Simple logging configuration for Showrunner.

Provides a ``get_logger`` helper that returns a ``logging.Logger``
instance pre‑configured with a formatter that includes timestamps, the
module name and the log level.
''' 

import logging
from typing import Final

_LOG_FORMAT: Final = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
_DATE_FORMAT: Final = "%Y-%m-%d %H:%M:%S"

_logging_configured = False


def _configure_root_logger() -> None:
    """Configure the root logger once.

    The function is idempotent – calling it multiple times has no effect.
    """
    global _logging_configured
    if _logging_configured:
        return
    logging.basicConfig(level=logging.INFO, format=_LOG_FORMAT, datefmt=_DATE_FORMAT)
    _logging_configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a logger with the given *name*.

    The root logger is configured on the first call.
    """
    _configure_root_logger()
    return logging.getLogger(name)
