from typing import Optional, Type, Union

import numpy as np

from renumics.spotlight.media.base import Array1dLike, MediaType


class Sequence1D(MediaType):
    """
    One-dimensional ndarray with optional index values.

    Attributes:
        index: 1-dimensional array-like of length `num_steps`. Index values (x-axis).
        value: 1-dimensional array-like of length `num_steps`. Respective values (y-axis).
        dtype: Optional data type of sequence. If `None`, data type inferred
            from data.

    Example:
        >>> import numpy as np
        >>> from renumics.spotlight import Dataset, Sequence1D
        >>> index = np.arange(100)
        >>> value = np.array(np.random.rand(100))
        >>> sequence = Sequence1D(index, value)
        >>> with Dataset("docs/example.h5", "w") as dataset:
        ...     dataset.append_sequence_1d_column("sequences", 5*[sequence])
        >>> with Dataset("docs/example.h5", "r") as dataset:
        ...     print(len(dataset["sequences", 2].value))
        100
    """

    index: np.ndarray
    value: np.ndarray

    def __init__(
        self,
        index: Optional[Array1dLike],
        value: Optional[Array1dLike] = None,
        dtype: Optional[Union[str, np.dtype, Type[np.number]]] = None,
    ) -> None:
        if value is None:
            if index is None:
                raise ValueError(
                    "At least one of arguments `index` or `value` should be "
                    "set, but both `None` values received."
                )
            value = index
            index = None

        value_array = np.asarray(value, dtype)
        if value_array.dtype.str[1] not in "fiu":
            raise ValueError(
                f"Input values should be array-likes with integer or float "
                f"dtype, but dtype {value_array.dtype.name} received."
            )
        if index is None:
            if value_array.ndim == 2:
                if value_array.shape[0] == 2:
                    self.index = value_array[0]
                    self.value = value_array[1]
                elif value_array.shape[1] == 2:
                    self.index = value_array[:, 0]
                    self.value = value_array[:, 1]
                else:
                    raise ValueError(
                        f"A single 2-dimensional input value should have one "
                        f"dimension of length 2, but shape {value_array.shape} received."
                    )
            elif value_array.ndim == 1:
                self.value = value_array
                if dtype is None:
                    dtype = self.value.dtype
                self.index = np.arange(len(self.value), dtype=dtype)
            else:
                raise ValueError(
                    f"A single input value should be 1- or 2-dimensional, but "
                    f"shape {value_array.shape} received."
                )
        else:
            if value_array.ndim != 1:
                raise ValueError(
                    f"Value should be 1-dimensional, but shape {value_array.shape} received."
                )
            index_array = np.asarray(index, dtype)
            if index_array.ndim != 1:
                raise ValueError(
                    f"INdex should be 1-dimensional array-like, but shape "
                    f"{index_array.shape} received."
                )
            if index_array.dtype.str[1] not in "fiu":
                raise ValueError(
                    f"Index should be array-like with integer or float "
                    f"dtype, but dtype {index_array.dtype.name} received."
                )
            self.value = value_array
            self.index = index_array
        if len(self.value) != len(self.index):
            raise ValueError(
                f"Lengths of `index` and `value` should match, but lengths "
                f"{len(self.index)} and {len(self.value)} received."
            )

    @classmethod
    def decode(cls, value: Union[np.ndarray, np.void]) -> "Sequence1D":
        if not isinstance(value, np.ndarray):
            raise TypeError(
                f"`value` argument should be a numpy array, but {type(value)} "
                f"received."
            )
        if value.ndim != 2 or value.shape[1] != 2:
            raise ValueError(
                f"`value` argument should be a numpy array with shape "
                f"`(num_steps, 2)`, but shape {value.shape} received."
            )
        return cls(value[:, 0], value[:, 1])

    def encode(self, _target: Optional[str] = None) -> np.ndarray:
        return np.stack((self.index, self.value), axis=1)

    @classmethod
    def empty(cls) -> "Sequence1D":
        """
        Create an empty sequence.
        """
        return cls(np.empty(0), np.empty(0))
