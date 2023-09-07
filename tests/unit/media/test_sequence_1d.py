"""
Test `renumics.spotlight.media.Sequence1D` class.
"""
import numpy as np
import pytest

from renumics.spotlight.media import Sequence1D

from ...integration.helpers import approx


@pytest.mark.parametrize("length", [1, 10, 100])
@pytest.mark.parametrize("input_type", ["array", "list", "tuple"])
def test_sequence_1d(length: int, input_type: str) -> None:
    """
    Test sequence initialization, encoding/decoding.
    """

    index = np.random.rand(length)
    value = np.random.rand(length)
    if input_type == "list":
        index = index.tolist()
        value = value.tolist()
    elif input_type == "tuple":
        index = tuple(index.tolist())  # type: ignore
        value = tuple(value.tolist())  # type: ignore
    # Initialization with index and value.
    sequence_1d = Sequence1D(index, value)
    assert approx(index, sequence_1d.index, "array")
    assert approx(value, sequence_1d.value, "array")
    encoded_sequence_1d = sequence_1d.encode()
    decoded_sequence_1d = Sequence1D.decode(encoded_sequence_1d)
    assert approx(sequence_1d, decoded_sequence_1d, "Sequence1D")
    # Initialization with value only.
    sequence_1d = Sequence1D(value)
    assert approx(np.arange(len(value)), sequence_1d.index, "array")
    assert approx(value, sequence_1d.value, "array")
    encoded_sequence_1d = sequence_1d.encode()
    decoded_sequence_1d = Sequence1D.decode(encoded_sequence_1d)
    assert approx(sequence_1d, decoded_sequence_1d, "Sequence1D")
