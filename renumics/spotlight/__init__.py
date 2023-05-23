"""
Renumics Spotlight
"""

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

__plugins__ = load_plugins()

__all__ = [
    "show",
    "close",
    "viewers",
    "Viewer",
]
