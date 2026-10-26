"""
Shared types for embeddings
"""

import itertools
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from typing import TypeAlias

import numpy as np
import PIL.Image

from renumics.spotlight.data_store import DataStore


class Embedder(ABC):
    """
    Base data store embedder class.

    Args:
        data_store: Data store.
        column: A column in the data store to embed.
    """

    data_store: DataStore
    column: str

    def __init__(self, data_store: DataStore, column: str) -> None:
        self.data_store = data_store
        self.column = column

    @abstractmethod
    def __call__(self) -> np.ndarray:
        """
        Embed the given column.
        """


PreprocessFunc: TypeAlias = Callable[[list], list]
EmbedFunc: TypeAlias = Callable[[Iterable[list]], Iterable[list[np.ndarray | None]]]
EmbedImageFunc: TypeAlias = Callable[
    [Iterable[list[PIL.Image.Image]]], Iterable[list[np.ndarray | None]]
]
EmbedArrayFunc: TypeAlias = Callable[
    [Iterable[list[np.ndarray]]], Iterable[list[np.ndarray | None]]
]


class FunctionalEmbedder(Embedder):
    """
    Wrapper for preprocessing and embedding functions.

    Attrs:
        preprocess_func: Preprocessing function. Receives a batch of data in our
            internal format and prepares is for embedding.
        embed_func: Embedding function. Receives an iterable with preprocessed
            data batches and yields batches of generated embeddings.
    """

    preprocess_func: PreprocessFunc
    embed_func: EmbedFunc
    batch_size: int
    _occupied_indices: list[int]

    def __init__(
        self,
        data_store: DataStore,
        column: str,
        preprocess_func: PreprocessFunc,
        embed_func: EmbedFunc,
    ) -> None:
        super().__init__(data_store, column)
        self.preprocess_func = preprocess_func
        self.embed_func = embed_func
        self.batch_size = 16
        self._occupied_indices = []

    def _iter_batches(self) -> Iterable[list]:
        """
        Yield batches with valid data, i.e. without the `None` values.
        """
        self._occupied_indices = []
        batch = []
        for i in range(len(self.data_store)):
            value = self.data_store.get_converted_value(
                self.column, i, simple=False, check=False
            )

            if value is None:
                continue

            self._occupied_indices.append(i)
            batch.append(value)
            if len(batch) == self.batch_size:
                yield self.preprocess_func(batch)
                batch = []
        if batch:
            yield self.preprocess_func(batch)

    def __call__(self) -> np.ndarray:
        """
        Embed the given column.
        """
        embeddings = itertools.chain(*self.embed_func(self._iter_batches()))
        res = np.empty(len(self.data_store), dtype=np.object_)
        res[self._occupied_indices] = list(embeddings)
        return res
