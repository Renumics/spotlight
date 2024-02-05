from typing import Union
import numpy as np
import pytest

from renumics import spotlight
from renumics.spotlight import dtypes
from renumics.spotlight.dataset.exceptions import InvalidDTypeError, InvalidShapeError


BOUNDING_BOXES = [
    [0, 1, 2, 3],
    [0.0, 1.0, np.nan, np.inf],
    range(4),
    (0, 1, 2, 3),
    (0.0, 1.0, np.nan, np.inf),
    np.ones(4),
    np.ones(4).astype(np.int8),
    np.full(4, np.nan),
]


def test_default(empty_dataset: spotlight.Dataset) -> None:
    """
    Test default column behaviour.
    """
    empty_dataset.append_bounding_box_column("column")
    assert empty_dataset.get_dtype("column") == dtypes.bounding_box_dtype

    valid_values: tuple = (
        [0, 1, 2, 3],
        [0.0, 1.0, np.nan, np.inf],
        range(4),
        (0, 1, 2, 3),
        (0.0, 1.0, np.nan, np.inf),
        np.ones(4),
        np.ones(4).astype(np.int8),
        np.full(4, np.nan),
    )
    for value in valid_values:
        empty_dataset.append_row(column=value)

    invalid_values: tuple = (
        [0, 1, 2, 3, 4],
        range(3),
        (0.0, 1.0, np.nan, np.inf, 5),
        np.ones(3).astype(np.int8),
        [],
        (),
        np.array([]),
        range(0),
    )
    for value in invalid_values:
        with pytest.raises(InvalidShapeError):
            empty_dataset.append_row(column=value)
    with pytest.raises(InvalidDTypeError):
        empty_dataset.append_row(column=None)

    assert empty_dataset.get_dtype("column") == dtypes.bounding_box_dtype

    values = empty_dataset["column"]
    assert values.shape == (len(valid_values), 4)


@pytest.mark.parametrize(
    "valid_values", [BOUNDING_BOXES, np.array(BOUNDING_BOXES, dtype=float)]
)
def test_default_with_values(
    empty_dataset: spotlight.Dataset, valid_values: Union[list, np.ndarray]
) -> None:
    """
    Test default column behaviour.
    """
    empty_dataset.append_bounding_box_column("column", values=valid_values)
    assert empty_dataset.get_dtype("column") == dtypes.bounding_box_dtype

    values = empty_dataset["column"]
    assert values.shape == (len(valid_values), 4)


def test_optional(empty_dataset: spotlight.Dataset) -> None:
    """
    Test optional column behaviour.
    """
    empty_dataset.append_bounding_box_column("column", optional=True)
    assert empty_dataset.get_dtype("column") == dtypes.bounding_box_dtype

    valid_values: tuple = (
        [0, 1, 2, 3],
        [0.0, 1.0, np.nan, np.inf],
        range(4),
        (0, 1, 2, 3),
        (0.0, 1.0, np.nan, np.inf),
        np.ones(4),
        np.ones(4).astype(np.int8),
        np.full(4, np.nan),
        None,
    )
    for value in valid_values:
        empty_dataset.append_row(column=value)

    invalid_values: tuple = (
        [0, 1, 2, 3, 4],
        range(3),
        (0.0, 1.0, np.nan, np.inf, 5),
        np.ones(3).astype(np.int8),
        [],
        (),
        np.array([]),
        range(0),
    )
    for value in invalid_values:
        with pytest.raises(InvalidShapeError):
            empty_dataset.append_row(column=value)

    assert empty_dataset.get_dtype("column") == dtypes.bounding_box_dtype

    values = empty_dataset["column"]
    assert values.shape == (len(valid_values), 4)
    none_mask = np.array([value is None for value in valid_values])
    assert np.isnan(values[none_mask]).all()


@pytest.mark.parametrize(
    "valid_values", [BOUNDING_BOXES, np.array(BOUNDING_BOXES, dtype=float)]
)
def test_generic_with_values(
    empty_dataset: spotlight.Dataset, valid_values: Union[list, np.ndarray]
) -> None:
    """
    Test default column behaviour.
    """
    empty_dataset.append_column(
        "column", dtypes.bounding_box_dtype, values=valid_values
    )
    assert empty_dataset.get_dtype("column") == dtypes.bounding_box_dtype

    values = empty_dataset["column"]
    assert values.shape == (len(valid_values), 4)
