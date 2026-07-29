"""
WorkPulse Logger
================
Import this anywhere in the project:

    from common.logger import get_logger
    logger = get_logger(__name__)

    logger.info("Employee created")
    logger.warning("Buffer below 10%")
    logger.error("Failed to send exit interview email")
    logger.debug("Query returned 42 rows")
"""
import logging


def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger under the 'apps' namespace.
    This ensures it uses the handlers defined in settings.LOGGING.

    Usage:
        logger = get_logger(__name__)
        # In apps/workforce/services/employee.py this becomes:
        # Logger name: apps.workforce.services.employee
    """
    return logging.getLogger(name)


# ── Pre-built loggers for common use ──────────────────────────────────────────
app_logger     = get_logger('apps.workpulse')
api_logger     = get_logger('api_requests')
service_logger = get_logger('apps.workforce.services')
auth_logger    = get_logger('apps.workforce.auth')