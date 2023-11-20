import numpy as np
import pytest

from renumics import spotlight
from renumics.spotlight import dtypes
from renumics.spotlight.dataset.exceptions import InvalidShapeError


@pytest.mark.parametrize("length", [1, 2, 8])
def test_default(empty_dataset: spotlight.Dataset, length: int) -> None:
    """
    Test default embedding column creation and afterwards filling row-by-row.
    """
    empty_dataset.append_embedding_column("embedding")
    assert empty_dataset.get_dtype("embedding") == dtypes.embedding_dtype

    valid_inputs = (
        [0] * length,
        range(length),
        tuple(range(length)),
        np.ones(length),
        np.full(length, np.nan),
    )
    for embedding in valid_inputs:
        empty_dataset.append_row(embedding=embedding)
        assert empty_dataset.get_dtype("embedding") == dtypes.EmbeddingDType(
            length=length
        )

    invalid_inputs: tuple = ([], range(length + 1))
    for embedding in invalid_inputs:
        with pytest.raises(InvalidShapeError):
            empty_dataset.append_row(embedding=embedding)

    embeddings = empty_dataset["embedding"]
    assert len(embeddings) == len(valid_inputs)
    assert all(embedding.shape == (length,) for embedding in embeddings)
    assert all(embedding.dtype == np.float32 for embedding in embeddings)


def test_default_zero_length(empty_dataset: spotlight.Dataset) -> None:
    """
    Test default embedding column creation and afterwards filling row-by-row
    with embeddings of length 0.
    """
    empty_dataset.append_embedding_column("embedding")
    assert empty_dataset.get_dtype("embedding") == dtypes.embedding_dtype

    valid_inputs: tuple = ([], (), range(0), np.array([]))
    for embedding in valid_inputs:
        empty_dataset.append_row(embedding=embedding)
        assert empty_dataset.get_dtype("embedding") == dtypes.EmbeddingDType(length=0)

    invalid_inputs: tuple = ([1], (1, 2), range(5), np.zeros(10))
    for embedding in invalid_inputs:
        with pytest.raises(InvalidShapeError):
            empty_dataset.append_row(embedding=embedding)

    embeddings = empty_dataset["embedding"]
    assert len(embeddings) == len(valid_inputs)
    assert all(embedding is None for embedding in embeddings)


@pytest.mark.parametrize("length", [1, 2, 8])
def test_default_with_values(empty_dataset: spotlight.Dataset, length: int) -> None:
    """
    Test default embedding column creation with given values and afterwards
    filling row-by-row.
    """
    valid_inputs = (
        [0] * length,
        range(length),
        tuple(range(length)),
        np.ones(length),
        np.full(length, np.nan),
    )
    empty_dataset.append_embedding_column("embedding", values=valid_inputs)
    assert empty_dataset.get_dtype("embedding") == dtypes.EmbeddingDType(length=length)

    for embedding in valid_inputs:
        empty_dataset.append_row(embedding=embedding)
        assert empty_dataset.get_dtype("embedding") == dtypes.EmbeddingDType(
            length=length
        )

    invalid_inputs: tuple = ([], range(length + 1))
    for embedding in invalid_inputs:
        with pytest.raises(InvalidShapeError):
            empty_dataset.append_row(embedding=embedding)

    embeddings = empty_dataset["embedding"]
    assert len(embeddings) == len(valid_inputs) * 2
    assert all(embedding.shape == (length,) for embedding in embeddings)
    assert all(embedding.dtype == np.float32 for embedding in embeddings)


def test_default_with_values_zero_length(empty_dataset: spotlight.Dataset) -> None:
    """
    Test default embedding column creation with given values and afterwards
    filling row-by-row with embeddings of length 0.
    """
    valid_inputs: tuple = ([], (), range(0), np.array([]))
    empty_dataset.append_embedding_column("embedding", values=valid_inputs)
    assert empty_dataset.get_dtype("embedding") == dtypes.EmbeddingDType(length=0)

    for embedding in valid_inputs:
        empty_dataset.append_row(embedding=embedding)
        assert empty_dataset.get_dtype("embedding") == dtypes.EmbeddingDType(length=0)

    invalid_inputs: tuple = ([1], (1, 2), range(5), np.zeros(10))
    for embedding in invalid_inputs:
        with pytest.raises(InvalidShapeError):
            empty_dataset.append_row(embedding=embedding)

    embeddings = empty_dataset["embedding"]
    assert len(embeddings) == len(valid_inputs) * 2
    assert all(embedding is None for embedding in embeddings)


@pytest.mark.parametrize("length", [1, 2, 8])
def test_optional(empty_dataset: spotlight.Dataset, length: int) -> None:
    """
    Test optional embedding column creation and afterwards filling row-by-row.
    """
    empty_dataset.append_embedding_column("embedding", optional=True)
    assert empty_dataset.get_dtype("embedding") == dtypes.embedding_dtype

    valid_inputs: tuple = (
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
    for embedding in valid_inputs:
        empty_dataset.append_row(embedding=embedding)
        assert empty_dataset.get_dtype("embedding") == dtypes.EmbeddingDType(
            length=length
        )

    invalid_inputs: tuple = (range(length + 1), np.full(length + 1, np.nan))
    for embedding in invalid_inputs:
        with pytest.raises(InvalidShapeError):
            empty_dataset.append_row(embedding=embedding)

    embeddings = empty_dataset["embedding"]
    assert len(embeddings) == len(valid_inputs)
    none_mask = np.array([False] * 5 + [True] * 5)
    assert all(embedding is None for embedding in embeddings[none_mask])
    assert all(embedding.shape == (length,) for embedding in embeddings[~none_mask])
    assert all(embedding.dtype == np.float32 for embedding in embeddings[~none_mask])


def test_optional_zero_length(empty_dataset: spotlight.Dataset) -> None:
    """
    Test optional embedding column creation and afterwards filling row-by-row
    with embeddings of length 0.
    """
    empty_dataset.append_embedding_column("embedding", optional=True)
    assert empty_dataset.get_dtype("embedding") == dtypes.embedding_dtype

    valid_inputs: tuple = (
        None,
        [],
        (),
        range(0),
        np.array([]),
    )
    for embedding in valid_inputs:
        empty_dataset.append_row(embedding=embedding)
        assert empty_dataset.get_dtype("embedding") == dtypes.embedding_dtype

    embeddings = empty_dataset["embedding"]
    assert len(embeddings) == len(valid_inputs)
    assert all(embedding is None for embedding in embeddings)

    empty_dataset.append_row(embedding=range(5))
    assert empty_dataset.get_dtype("embedding") == dtypes.EmbeddingDType(length=5)


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

    valid_inputs = (
        [0] * length,
        range(length),
        tuple(range(length)),
        np.ones(length),
        np.full(length, np.nan),
    )
    for embedding in valid_inputs:
        empty_dataset.append_row(embedding=embedding)
        assert empty_dataset.get_dtype("embedding") == dtypes.EmbeddingDType(
            length=length
        )

    embeddings = empty_dataset["embedding"]
    assert len(embeddings) == len(valid_inputs)
    assert all(embedding.shape == (length,) for embedding in embeddings)
    assert all(embedding.dtype == np_dtype for embedding in embeddings)


@pytest.mark.parametrize("length", [1, 2, 8])
def test_generic(empty_dataset: spotlight.Dataset, length: int) -> None:
    """
    Test generic embedding column creation and afterwards filling row-by-row.
    """
    dtype = dtypes.EmbeddingDType(length=length)
    empty_dataset.append_column("embedding", dtype)
    assert empty_dataset.get_dtype("embedding") == dtype

    valid_inputs = (
        [0] * length,
        range(length),
        tuple(range(length)),
        np.ones(length),
        np.full(length, np.nan),
    )
    for embedding in valid_inputs:
        empty_dataset.append_row(embedding=embedding)
        assert empty_dataset.get_dtype("embedding") == dtype

    invalid_inputs: tuple = ([], range(length + 1))
    for embedding in invalid_inputs:
        with pytest.raises(InvalidShapeError):
            empty_dataset.append_row(embedding=embedding)

    embeddings = empty_dataset["embedding"]
    assert len(embeddings) == len(valid_inputs)
    assert all(embedding.shape == (length,) for embedding in embeddings)
    assert all(embedding.dtype == np.float32 for embedding in embeddings)
