"""
Base classes for dtypes.
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TypeAlias

import numpy as np

from renumics.spotlight.typing import NumberType, PathType

Array1dLike: TypeAlias = Sequence[NumberType] | np.ndarray
Array2dLike: TypeAlias = (
    Sequence[Sequence[NumberType]] | Sequence[np.ndarray] | np.ndarray
)
ImageLike: TypeAlias = (
    Sequence[Sequence[NumberType | Sequence[NumberType]]] | np.ndarray
)


class MediaType(ABC):
    """
    Base Spotlight dataset field data.
    """

    @classmethod
    @abstractmethod
    def decode(cls, value: np.ndarray | np.void) -> "MediaType":
        """
        Restore class from its numpy representation.
        """
        raise NotImplementedError

    @abstractmethod
    def encode(self, target: str | None = None) -> np.ndarray | np.void:
        """
        Convert to numpy for storing in dataset.

        Args:
            target: Optional target format.
        """
        raise NotImplementedError


class FileMediaType(MediaType):
    """
    Spotlight dataset field data which can be read from a file.
    """

    @classmethod
    @abstractmethod
    def from_file(cls, filepath: PathType) -> "FileMediaType":
        """
        Read data from a file.
        """
        raise NotImplementedError
