"""
Shared types for embeddings
"""

from abc import ABC, abstractmethod
from typing import Any

import numpy as np


class Embedder(ABC):
    @abstractmethod
    def __init__(self, data_store: Any, column: str) -> None:
        """
        Raise if dtype of the given column is not supported.
        """

    @abstractmethod
    def __call__(self) -> np.ndarray:
        """
        Embed the given column.
        """
