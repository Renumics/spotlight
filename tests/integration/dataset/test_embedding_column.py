import numpy as np
import pytest

from renumics import spotlight
from renumics.spotlight import dtypes
from renumics.spotlight.dataset.exceptions import InvalidDTypeError, InvalidShapeError


@pytest.mark.parametrize("length", [1, 2, 8])
def test_default(empty_dataset: spotlight.Dataset, length: int) -> None:
    """
    Test default embedding column creation and afterwards filling row-by-row.
    """
    empty_dataset.append_embedding_column("embedding")
    assert empty_dataset.get_dtype("embedding") == dtypes.embedding_dtype

    valid_values: tuple = (
        [0] * length,
        range(length),
        tuple(range(length)),
        np.ones(length),
        np.full(length, np.nan),
    )
    for value in valid_values:
        empty_dataset.append_row(embedding=value)
        assert empty_dataset.get_dtype("embedding") == dtypes.EmbeddingDType(
            length=length
        )

    invalid_values: tuple = ([], range(length + 1))
    for value in invalid_values:
        with pytest.raises(InvalidShapeError):
            empty_dataset.append_row(embedding=value)

    values = empty_dataset["embedding"]
    assert len(values) == len(valid_values)
    assert all(value.shape == (length,) for value in values)
    assert all(value.dtype == np.float32 for value in values)


def test_default_zero_length(empty_dataset: spotlight.Dataset) -> None:
    """
    Test default embedding column creation and afterwards filling row-by-row
    with values of length 0.
    """
    empty_dataset.append_embedding_column("embedding")
    assert empty_dataset.get_dtype("embedding") == dtypes.embedding_dtype

    valid_values: tuple = ([], (), range(0), np.array([]))
    for value in valid_values:
        empty_dataset.append_row(embedding=value)
        assert empty_dataset.get_dtype("embedding") == dtypes.EmbeddingDType(length=0)

    invalid_values: tuple = ([1], (1, 2), range(5), np.zeros(10))
    for value in invalid_values:
        with pytest.raises(InvalidShapeError):
            empty_dataset.append_row(embedding=value)

    values = empty_dataset["embedding"]
    assert len(values) == len(valid_values)
    assert all(value is None for value in values)


@pytest.mark.parametrize("length", [1, 2, 8])
def test_default_with_values(empty_dataset: spotlight.Dataset, length: int) -> None:
    """
    Test default embedding column creation with given values and afterwards
    filling row-by-row.
    """
    valid_values: tuple = (
        [0] * length,
        range(length),
        tuple(range(length)),
        np.ones(length),
        np.full(length, np.nan),
    )
    empty_dataset.append_embedding_column("embedding", values=valid_values)
    assert empty_dataset.get_dtype("embedding") == dtypes.EmbeddingDType(length=length)

    for value in valid_values:
        empty_dataset.append_row(embedding=value)
        assert empty_dataset.get_dtype("embedding") == dtypes.EmbeddingDType(
            length=length
        )

    invalid_values: tuple = ([], range(length + 1))
    for value in invalid_values:
        with pytest.raises(InvalidShapeError):
            empty_dataset.append_row(embedding=value)

    values = empty_dataset["embedding"]
    assert len(values) == len(valid_values) * 2
    assert all(value.shape == (length,) for value in values)
    assert all(value.dtype == np.float32 for value in values)


def test_default_with_values_zero_length(empty_dataset: spotlight.Dataset) -> None:
    """
    Test default embedding column creation with given values and afterwards
    filling row-by-row with values of length 0.
    """
    valid_values: tuple = ([], (), range(0), np.array([]))
    empty_dataset.append_embedding_column("embedding", values=valid_values)
    assert empty_dataset.get_dtype("embedding") == dtypes.EmbeddingDType(length=0)

    for value in valid_values:
        empty_dataset.append_row(embedding=value)
        assert empty_dataset.get_dtype("embedding") == dtypes.EmbeddingDType(length=0)

    invalid_values: tuple = ([1], (1, 2), range(5), np.zeros(10))
    for value in invalid_values:
        with pytest.raises(InvalidShapeError):
            empty_dataset.append_row(embedding=value)

    values = empty_dataset["embedding"]
    assert len(values) == len(valid_values) * 2
    assert all(embedding is None for embedding in values)


@pytest.mark.parametrize("length", [1, 2, 8])
def test_optional(empty_dataset: spotlight.Dataset, length: int) -> None:
    """
    Test optional embedding column creation and afterwards filling row-by-row.
    """
    empty_dataset.append_embedding_column("embedding", optional=True)
    assert empty_dataset.get_dtype("embedding") == dtypes.embedding_dtype

    valid_values: tuple = (
        [0] * length,
        range(length),
        tuple(range(length)),
        np.ones(length),
        np.full(length, np.nan),
        None,
        [],
        (),
        range(0),
        np.array([]),
    )
    for value in valid_values:
        empty_dataset.append_row(embedding=value)
        assert empty_dataset.get_dtype("embedding") == dtypes.EmbeddingDType(
            length=length
        )

    invalid_values: tuple = (range(length + 1), np.full(length + 1, np.nan))
    for value in invalid_values:
        with pytest.raises(InvalidShapeError):
            empty_dataset.append_row(embedding=value)

    values = empty_dataset["embedding"]
    assert len(values) == len(valid_values)
    none_mask = np.array([False] * 5 + [True] * 5)
    assert all(value is None for value in values[none_mask])
    assert all(value.shape == (length,) for value in values[~none_mask])
    assert all(value.dtype == np.float32 for value in values[~none_mask])


def test_optional_zero_length(empty_dataset: spotlight.Dataset) -> None:
    """
    Test optional embedding column creation and afterwards filling row-by-row
    with values of length 0.
    """
    empty_dataset.append_embedding_column("embedding", optional=True)
    assert empty_dataset.get_dtype("embedding") == dtypes.embedding_dtype

    valid_values: tuple = (
        None,
        [],
        (),
        range(0),
        np.array([]),
    )
    for value in valid_values:
        empty_dataset.append_row(embedding=value)
        assert empty_dataset.get_dtype("embedding") == dtypes.embedding_dtype

    values = empty_dataset["embedding"]
    assert len(values) == len(valid_values)
    assert all(value is None for value in values)

    empty_dataset.append_row(embedding=range(5))
    assert empty_dataset.get_dtype("embedding") == dtypes.EmbeddingDType(length=5)


@pytest.mark.parametrize("length", [1, 2, 8])
def test_length(empty_dataset: spotlight.Dataset, length: int) -> None:
    """
    Test default embedding with length column creation and afterwards filling
    row-by-row.
    """
    empty_dataset.append_embedding_column("embedding", length=length)
    assert empty_dataset.get_dtype("embedding") == dtypes.EmbeddingDType(length=length)

    valid_values: tuple = (
        [0] * length,
        range(length),
        tuple(range(length)),
        np.ones(length),
        np.full(length, np.nan),
    )
    for value in valid_values:
        empty_dataset.append_row(embedding=value)
        assert empty_dataset.get_dtype("embedding") == dtypes.EmbeddingDType(
            length=length
        )

    invalid_values: tuple = ([], range(length + 1))
    for value in invalid_values:
        with pytest.raises(InvalidShapeError):
            empty_dataset.append_row(embedding=value)
    with pytest.raises(InvalidDTypeError):
        empty_dataset.append_row(embedding=None)

    values = empty_dataset["embedding"]
    assert len(values) == len(valid_values)
    assert all(value.shape == (length,) for value in values)
    assert all(value.dtype == np.float32 for value in values)


def test_zero_length(empty_dataset: spotlight.Dataset) -> None:
    """
    Test default embedding with length of 0 column creation and afterwards
    filling row-by-row.
    """
    empty_dataset.append_embedding_column("embedding", length=0)
    assert empty_dataset.get_dtype("embedding") == dtypes.EmbeddingDType(length=0)

    valid_values: tuple = ([], (), range(0), np.array([]))
    for value in valid_values:
        empty_dataset.append_row(embedding=value)
        assert empty_dataset.get_dtype("embedding") == dtypes.EmbeddingDType(length=0)

    invalid_values: tuple = ([1], (1, 2), range(5), np.zeros(10))
    for value in invalid_values:
        with pytest.raises(InvalidShapeError):
            empty_dataset.append_row(embedding=value)
    with pytest.raises(InvalidDTypeError):
        empty_dataset.append_row(embedding=None)

    values = empty_dataset["embedding"]
    assert len(values) == len(valid_values)
    assert all(value is None for value in values)


@pytest.mark.parametrize("length", [1, 2, 8])
@pytest.mark.parametrize("np_dtype", [np.float16, np.float32, np.float64])
def test_dtype(
    empty_dataset: spotlight.Dataset, length: int, np_dtype: np.dtype
) -> None:
    """
    Test embedding column creation with dtype and afterwards filling row-by-row.
    """
    empty_dataset.append_embedding_column("embedding", dtype=np_dtype)
    assert empty_dataset.get_dtype("embedding") == dtypes.embedding_dtype

    valid_values: tuple = (
        [0] * length,
        range(length),
        tuple(range(length)),
        np.ones(length),
        np.full(length, np.nan),
    )
    for value in valid_values:
        empty_dataset.append_row(embedding=value)
        assert empty_dataset.get_dtype("embedding") == dtypes.EmbeddingDType(
            length=length
        )

    values = empty_dataset["embedding"]
    assert len(values) == len(valid_values)
    assert all(value.shape == (length,) for value in values)
    assert all(value.dtype == np_dtype for value in values)


@pytest.mark.parametrize("length", [1, 2, 8])
def test_generic(empty_dataset: spotlight.Dataset, length: int) -> None:
    """
    Test generic embedding column creation and afterwards filling row-by-row.
    """
    dtype = dtypes.EmbeddingDType(length=length)
    empty_dataset.append_column("embedding", dtype)
    assert empty_dataset.get_dtype("embedding") == dtype

    valid_values: tuple = (
        [0] * length,
        range(length),
        tuple(range(length)),
        np.ones(length),
        np.full(length, np.nan),
    )
    for value in valid_values:
        empty_dataset.append_row(embedding=value)
        assert empty_dataset.get_dtype("embedding") == dtype

    invalid_values: tuple = ([], range(length + 1))
    for value in invalid_values:
        with pytest.raises(InvalidShapeError):
            empty_dataset.append_row(embedding=value)
    with pytest.raises(InvalidDTypeError):
        empty_dataset.append_row(embedding=None)

    values = empty_dataset["embedding"]
    assert len(values) == len(valid_values)
    assert all(value.shape == (length,) for value in values)
    assert all(value.dtype == np.float32 for value in values)
