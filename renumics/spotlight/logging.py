"""
    Logging facilities for Spotlight
"""

from loguru import logger


def enable() -> None:
    """
    Enable logging for all spotlight modules
    """
    logger.enable("renumics.spotlight")
    logger.enable("renumics.spotlight_plugins")


def disable() -> None:
    """
    Disable logging for all spotlight modules
    """
    logger.disable("renumics.spotlight")
    logger.disable("renumics.spotlight_plugins")
