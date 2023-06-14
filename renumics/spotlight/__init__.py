"""
Renumics Spotlight
"""

from loguru import logger
from .__version__ import __version__
from .dataset import Dataset
from .dtypes import (
    Audio,
    Category,
    Embedding,
    Image,
    Mesh,
    Sequence1D,
    Video,
    Window,
)
from .viewer import Viewer, close, viewers, show
from .plugin_loader import load_plugins
from .settings import settings
from . import cache, logging

if not settings.verbose:
    logging.disable()

__plugins__ = load_plugins()

__all__ = ["show", "close", "viewers", "Viewer", "clear_caches"]


def clear_caches() -> None:
    """
    Clear all cached data.
    """
    cache.clear("external-data")
