from typing import Any

import numpy as np

from renumics.spotlight import dtypes
from renumics.spotlight.embeddings.decorator import embedder
from renumics.spotlight.embeddings.exceptions import CannotEmbed
from renumics.spotlight.embeddings.typing import Embedder


@embedder
class Dummy(Embedder):
    def __init__(self, data_store: Any, column: str) -> None:
        if not dtypes.is_image_dtype(data_store.dtypes[column]):
            raise CannotEmbed
        self._data_store = data_store
        self._column = column

    def __call__(self) -> np.ndarray:
        return np.random.random((len(self._data_store), 4))
