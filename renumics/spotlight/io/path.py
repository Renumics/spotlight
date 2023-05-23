"""
path helper functions
"""

from pathlib import Path

from renumics.spotlight.typing import PathType


def is_path_relative_to(path: PathType, parent: PathType) -> bool:
    """
    Is the path a subpath of the parent
    """
    try:
        Path(path).relative_to(parent)
        return True
    except ValueError:
        return False
