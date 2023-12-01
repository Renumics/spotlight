"""
Shared types for embeddings
"""

import itertools
from abc import ABC, abstractmethod
from typing import Any, Callable, Iterable, List, Optional

import numpy as np


class Embedder(ABC):
    data_store: Any
    column: str

    def __init__(self, data_store: Any, column: str) -> None:
        self.data_store = data_store
        self.column = column

    @abstractmethod
    def __call__(self) -> np.ndarray:
        """
        Embed the given column.
        """


PreprocessFunc = Callable[[list], list]
EmbedFunc = Callable[[Iterable[list]], Iterable[List[Optional[np.ndarray]]]]


class FunctionalEmbedder(Embedder):
    preprocess_func: PreprocessFunc
    embed_func: EmbedFunc
    batch_size: int
    _occupied_indices: List[int]

    def __init__(
        self,
        data_store: Any,
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
        Yield batches with data, i.e. without the `None` values.
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
        embeddings = itertools.chain(*self.embed_func(self._iter_batches()))
        res = np.empty(len(self.data_store), dtype=np.object_)
        res[self._occupied_indices] = list(embeddings)
        return res
