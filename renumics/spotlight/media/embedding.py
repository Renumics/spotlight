from typing import Optional, Type, Union

import numpy as np

from renumics.spotlight.media.base import Array1dLike, MediaType


class Embedding(MediaType):
    """
    Data sample projected onto a new space.

    Attributes:
        data: 1-dimensional array-like. Sample embedding.
        dtype: Optional data type of embedding. If `None`, data type inferred
            from data.

    Example:
        >>> import numpy as np
        >>> from renumics.spotlight import Dataset, Embedding
        >>> value = np.array(np.random.rand(2))
        >>> embedding = Embedding(value)
        >>> with Dataset("docs/example.h5", "w") as dataset:
        ...     dataset.append_embedding_column("embeddings", 5*[embedding])
        >>> with Dataset("docs/example.h5", "r") as dataset:
        ...     print(len(dataset["embeddings", 3].data))
        2
    """

    data: np.ndarray

    def __init__(
        self,
        data: Array1dLike,
        dtype: Optional[Union[str, np.dtype, Type[np.number]]] = None,
    ) -> None:
        data_array = np.asarray(data, dtype)
        if data_array.ndim != 1 or data_array.size == 0:
            raise ValueError(
                f"`data` argument should an array-like with shape "
                f"`(num_features,)` with `num_features > 0`, but shape "
                f"{data_array.shape} received."
            )
        if data_array.dtype.str[1] not in "fiu":
            raise ValueError(
                f"`data` argument should be an array-like with integer or "
                f"float dtypes, but dtype {data_array.dtype.name} received."
            )
        self.data = data_array

    @classmethod
    def decode(cls, value: Union[np.ndarray, np.void]) -> "Embedding":
        if not isinstance(value, np.ndarray):
            raise TypeError(
                f"`value` argument should be a numpy array, but {type(value)} "
                f"received."
            )
        return cls(value)

    def encode(self, _target: Optional[str] = None) -> np.ndarray:
        return self.data
