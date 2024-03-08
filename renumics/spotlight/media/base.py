"""
Base classes for dtypes.
"""

from abc import ABC, abstractmethod
from typing import Optional, Sequence, Union

import numpy as np

from renumics.spotlight.typing import NumberType, PathType

Array1dLike = Union[Sequence[NumberType], np.ndarray]
Array2dLike = Union[Sequence[Sequence[NumberType]], Sequence[np.ndarray], np.ndarray]
ImageLike = Union[
    Sequence[Sequence[Union[NumberType, Sequence[NumberType]]]], np.ndarray
]


class MediaType(ABC):
    """
    Base Spotlight dataset field data.
    """

    @classmethod
    @abstractmethod
    def decode(cls, value: Union[np.ndarray, np.void]) -> "MediaType":
        """
        Restore class from its numpy representation.
        """
        raise NotImplementedError

    @abstractmethod
    def encode(self, target: Optional[str] = None) -> Union[np.ndarray, np.void]:
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
