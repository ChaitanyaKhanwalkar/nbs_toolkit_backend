"""Logging setup for the backend application.

This module keeps logging configuration in one place. It does not configure
deployment, secrets, database tables, or scientific recommendation behavior.
"""

import logging


def configure_logging(log_level: str) -> None:
    """Configure simple console logging for local development."""

    logging.basicConfig(
        level=log_level.upper(),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
