"""
Base classes for dtypes.
"""
from abc import ABC, abstractmethod
from typing import Optional, Union

import numpy as np

from renumics.spotlight.typing import PathType


class DType(ABC):
    """
    Base Spotlight dataset field data.
    """

    @classmethod
    @abstractmethod
    def decode(cls, value: Union[np.ndarray, np.void]) -> "DType":
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


class FileBasedDType(DType):
    """
    Spotlight dataset field data which can be read from a file.
    """

    @classmethod
    @abstractmethod
    def from_file(cls, filepath: PathType) -> "FileBasedDType":
        """
        Read data from a file.
        """
        raise NotImplementedError
