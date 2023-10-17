"""
Renumics Spotlight
"""

from .__version__ import __version__  # noqa: F401
from .dataset import Dataset  # noqa: F401
from .media import (
    Audio,  # noqa: F401
    Embedding,  # noqa: F401
    Image,  # noqa: F401
    Mesh,  # noqa: F401
    Sequence1D,  # noqa: F401
    Video,  # noqa: F401
)
from .dtypes.legacy import Category, Window  # noqa: F401
from .viewer import Viewer, close, viewers, show
from .plugin_loader import load_plugins
from .settings import settings
from .analysis.typing import DataIssue
from . import cache, logging

if not settings.verbose:
    logging.disable()

__plugins__ = load_plugins()

__all__ = ["show", "close", "viewers", "Viewer", "clear_caches", "DataIssue"]


def clear_caches() -> None:
    """
    Clear all cached data.
    """
    cache.clear("external-data")
