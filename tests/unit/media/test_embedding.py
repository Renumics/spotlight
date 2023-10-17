"""
Test `renumics.spotlight.media.Embedding` class.
"""

import numpy as np
import pytest

from renumics.spotlight.media import Embedding

from .data import SEED
from ...integration.helpers import approx


@pytest.mark.parametrize("length", [1, 10, 100])
@pytest.mark.parametrize("dtype", ["float32", "float64", "uint16", "int32"])
@pytest.mark.parametrize("input_type", ["array", "list", "tuple"])
def test_embedding(length: int, dtype: str, input_type: str) -> None:
    """
    Test embedding initialization, encoding/decoding.
    """
    np.random.seed(SEED)
    np_dtype = np.dtype(dtype)
    if np_dtype.str[1] == "f":
        array = np.random.uniform(0, 1, length).astype(dtype)
    else:
        array = np.random.randint(  # type: ignore
            np.iinfo(np_dtype).min, np.iinfo(np_dtype).max, length, dtype
        )
    if input_type == "list":
        array = array.tolist()
    elif input_type == "tuple":
        array = tuple(array.tolist())  # type: ignore

    # Test instantiation
    embedding = Embedding(array)
    assert approx(array, embedding.data, "Embedding")

    # Test encode
    encoded_embedding = embedding.encode()
    assert isinstance(encoded_embedding, np.ndarray)

    # Test decode
    decoded_embedding = Embedding.decode(encoded_embedding)
    assert approx(embedding, decoded_embedding.data, "Embedding")


@pytest.mark.parametrize("input_type", ["array", "list", "tuple"])
def test_zero_length_embedding_fails(input_type: str) -> None:
    """
    Test if `Embedding` fails with zero-length data.
    """
    array = np.empty(0)
    if input_type == "list":
        array = array.tolist()
    elif input_type == "tuple":
        array = tuple(array.tolist())  # type: ignore
    with pytest.raises(ValueError):
        _ = Embedding(array)


@pytest.mark.parametrize("num_dims", [0, 2, 3, 4])
def test_multidimensional_embedding_fails(num_dims: int) -> None:
    """
    Test if `Embedding` fails with not one-dimensional data.
    """
    np.random.seed(SEED)
    dims = np.random.randint(1, 20, num_dims)
    array = np.random.uniform(0, 1, dims)
    with pytest.raises(ValueError):
        _ = Embedding(array)
