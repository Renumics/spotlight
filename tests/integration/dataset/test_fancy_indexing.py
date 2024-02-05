"""
Test fancy indexing of `spotlight.Dataset` class.
"""

import datetime
from typing import Any, List, cast

import numpy as np
import pytest

from renumics.spotlight import Dataset
from renumics.spotlight.dataset import exceptions


def test_getitem(fancy_indexing_dataset: Dataset) -> None:
    """
    Test `spotlight.Dataset.__getitem__` with fancy indices.
    """
    length = len(fancy_indexing_dataset)
    column_name = fancy_indexing_dataset.keys()[0]
    target = np.array(fancy_indexing_dataset[column_name])

    # Whole column.
    assert (fancy_indexing_dataset[column_name] == target).all()
    assert (fancy_indexing_dataset[column_name, :] == target[:]).all()
    assert (fancy_indexing_dataset[:, column_name] == target[:]).all()

    good_indices: List[Any] = [[]]

    all_indices = np.arange(length)
    for _ in range(3):
        # Boolean arrays.
        indices = np.random.randint(2, size=length).astype(bool)
        good_indices.extend((indices, indices.tolist()))
        # Unique indices.
        indices = all_indices[indices]
        good_indices.extend((indices, indices.tolist()))

    # Slices.
    for arg in (
        -length * 2,
        -length - 10,
        -length,
        -length + 10,
        -length // 2,
        -5,
        -2,
        -1,
        1,
        2,
        5,
        length // 2,
        length - 10,
        length,
        length + 10,
        length * 2,
    ):
        # Use as step.
        good_indices.append(slice(None, None, arg))
        good_indices.append(slice(0, None, arg))
        good_indices.append(slice(None, length, arg))
        # Use as start.
        good_indices.append(slice(arg, None, None))
        good_indices.append(slice(arg, length, None))
        good_indices.append(slice(arg, None, 3))
        good_indices.append(slice(arg, length, 3))
        # Use as stop.
        good_indices.append(slice(0, arg, None))
        good_indices.append(slice(None, arg, None))
        good_indices.append(slice(0, arg, 3))
        good_indices.append(slice(None, arg, 3))

    # Duplicated indices.
    all_indices = np.arange(-length, length)
    for length_ in (length // 4, length // 2, length, length * 2, length * 4):
        for _ in range(3):
            indices = np.random.choice(all_indices, length_)
            good_indices.extend((indices, indices.tolist()))

    for indices in good_indices:
        target_ = target[indices]
        assert (target_ == fancy_indexing_dataset[column_name, indices]).all()
        assert (target_ == fancy_indexing_dataset[indices, column_name]).all()

    bad_indices: List[Any] = [slice(None, None, 0)]

    for length_ in [
        1,
        length // 4,
        length // 2,
        length - 1,
        length + 1,
        length * 2,
        length * 4,
    ]:
        indices = np.random.randint(2, size=length_).astype(bool)
        bad_indices.extend((indices, indices.tolist()))

    invalid_indices = np.append(
        np.arange(-length * 2, -length), np.arange(length, length * 2)
    )
    for length_ in (length // 4, length // 2, length, length * 2, length * 4):
        for _ in range(3):
            indices = np.random.choice(invalid_indices, length_)
            bad_indices.extend((indices, indices.tolist()))

    for indices in bad_indices:
        with pytest.raises(exceptions.InvalidIndexError):
            _ = fancy_indexing_dataset[column_name, indices]
        with pytest.raises(exceptions.InvalidIndexError):
            _ = fancy_indexing_dataset[indices, column_name]


def test_delitem(fancy_indexing_dataset: Dataset) -> None:
    """
    Test `spotlight.Dataset.__delitem__` with fancy indices.
    """

    length = len(fancy_indexing_dataset)
    column_name = fancy_indexing_dataset.keys()[0]
    dtype = fancy_indexing_dataset.get_dtype(column_name)
    target = np.array(fancy_indexing_dataset[column_name])

    def _restore_column() -> None:
        del fancy_indexing_dataset[column_name]
        assert column_name not in fancy_indexing_dataset.keys()
        fancy_indexing_dataset.append_column(column_name, dtype, target)
        assert column_name in fancy_indexing_dataset.keys()
        assert (target == fancy_indexing_dataset[column_name]).all()

    _restore_column()

    good_indices: List[Any] = [slice(None, None, None), []]

    all_indices = np.arange(length)
    for _ in range(3):
        # Boolean arrays.
        indices = np.random.randint(2, size=length).astype(bool)
        good_indices.extend((indices, indices.tolist()))
        # Unique indices.
        indices = all_indices[indices]
        good_indices.extend((indices, indices.tolist()))

    # Slices.
    for arg in (
        -length * 2,
        -length - 10,
        -length,
        -length + 10,
        -length // 2,
        -5,
        -2,
        -1,
        1,
        2,
        5,
        length // 2,
        length - 10,
        length,
        length + 10,
        length * 2,
    ):
        # Use as step.
        good_indices.append(slice(None, None, arg))
        good_indices.append(slice(0, None, arg))
        good_indices.append(slice(None, length, arg))
        # Use as start.
        good_indices.append(slice(arg, None, None))
        good_indices.append(slice(arg, length, None))
        good_indices.append(slice(arg, None, 3))
        good_indices.append(slice(arg, length, 3))
        # Use as stop.
        good_indices.append(slice(0, arg, None))
        good_indices.append(slice(None, arg, None))
        good_indices.append(slice(0, arg, 3))
        good_indices.append(slice(None, arg, 3))

    # Duplicated indices.
    all_indices = np.arange(-length, length)
    for length_ in (length // 4, length // 2, length, length * 2, length * 4):
        for _ in range(3):
            indices = np.random.choice(all_indices, length_)
            good_indices.extend((indices, indices.tolist()))

    for indices in good_indices:
        mask = np.full(length, True)
        mask[indices] = False
        target_ = target[mask]
        del fancy_indexing_dataset[indices]
        assert (target_ == fancy_indexing_dataset[column_name]).all()
        _restore_column()
        del fancy_indexing_dataset[indices]
        assert (target_ == fancy_indexing_dataset[column_name]).all()
        _restore_column()

    bad_indices: List[Any] = [slice(None, None, 0)]

    for length_ in [
        1,
        length // 4,
        length // 2,
        length - 1,
        length + 1,
        length * 2,
        length * 4,
    ]:
        indices = np.random.randint(2, size=length_).astype(bool)
        bad_indices.extend((indices, indices.tolist()))

    invalid_indices = np.append(
        np.arange(-length * 2, -length), np.arange(length, length * 2)
    )
    for length_ in (length // 4, length // 2, length, length * 2, length * 4):
        for _ in range(3):
            indices = np.random.choice(invalid_indices, length_)
            bad_indices.extend((indices, indices.tolist()))

    for indices in bad_indices:
        with pytest.raises(exceptions.InvalidIndexError):
            del fancy_indexing_dataset[indices]
        assert column_name in fancy_indexing_dataset.keys()
        assert len(fancy_indexing_dataset) == length
        assert (target == fancy_indexing_dataset[column_name]).all()
        with pytest.raises(exceptions.InvalidIndexError):
            del fancy_indexing_dataset[indices]
        assert column_name in fancy_indexing_dataset.keys()
        assert len(fancy_indexing_dataset) == length
        assert (target == fancy_indexing_dataset[column_name]).all()


def _assert_unique_datetime(values: np.ndarray) -> datetime.datetime:
    unique_values = np.unique(values)
    assert len(unique_values) == 1
    return datetime.datetime.fromisoformat(unique_values[0].decode("utf-8"))


def test_setitem(fancy_indexing_dataset: Dataset) -> None:
    """
    Test `spotlight.Dataset.__setitem__` with fancy indices.
    """

    length = len(fancy_indexing_dataset)
    column_name = fancy_indexing_dataset.keys()[0]
    last_edited_at_column = fancy_indexing_dataset._h5_file["__last_edited_at__"]
    timestamp = _assert_unique_datetime(last_edited_at_column[:])

    good_indices: List[Any] = [slice(None, None, None), []]

    all_indices = np.arange(length)
    for _ in range(3):
        # Boolean arrays.
        indices = np.random.randint(2, size=length).astype(bool)
        good_indices.extend((indices, indices.tolist()))
        # Unique indices.
        indices = all_indices[indices]
        good_indices.extend((indices, indices.tolist()))

    # Slices.
    for arg in (
        -length * 2,
        -length - 10,
        -length,
        -length + 10,
        -length // 2,
        -5,
        -2,
        -1,
        1,
        2,
        5,
        length // 2,
        length - 10,
        length,
        length + 10,
        length * 2,
    ):
        # Use as step.
        good_indices.append(slice(None, None, arg))
        good_indices.append(slice(0, None, arg))
        good_indices.append(slice(None, length, arg))
        # Use as start.
        good_indices.append(slice(arg, None, None))
        good_indices.append(slice(arg, length, None))
        good_indices.append(slice(arg, None, 3))
        good_indices.append(slice(arg, length, 3))
        # Use as stop.
        good_indices.append(slice(0, arg, None))
        good_indices.append(slice(None, arg, None))
        good_indices.append(slice(0, arg, 3))
        good_indices.append(slice(None, arg, 3))

    for indices in good_indices:
        last_edited_at_indices = np.unique(all_indices[indices])
        for values in (
            np.random.randint(-1000, 1000, size=len(all_indices[indices])),
            np.random.randint(-1000, 1000),
        ):
            bad_values = np.random.randint(
                -1000, 1000, size=len(last_edited_at_indices) + 5
            )
            target = np.array(fancy_indexing_dataset[column_name])
            target[indices] = values
            fancy_indexing_dataset[column_name, indices] = cast(np.ndarray, values)
            last_edited_at = last_edited_at_column[last_edited_at_indices]
            if len(last_edited_at_indices) > 0:
                timestamp_ = _assert_unique_datetime(
                    last_edited_at_column[last_edited_at_indices]
                )
                assert timestamp_ >= timestamp
                timestamp = timestamp_

                with pytest.raises(exceptions.InvalidShapeError):
                    # Must raise
                    fancy_indexing_dataset[column_name, indices] = bad_values
            else:
                # Must do nothing
                fancy_indexing_dataset[column_name, indices] = bad_values

            assert (
                last_edited_at == last_edited_at_column[last_edited_at_indices]
            ).all()
            assert (target == fancy_indexing_dataset[column_name]).all()

    target = np.array(fancy_indexing_dataset[column_name])
    bad_indices: List[Any] = [slice(None, None, 0)]

    for length_ in [
        1,
        length // 4,
        length // 2,
        length - 1,
        length + 1,
        length * 2,
        length * 4,
    ]:
        indices = np.random.randint(2, size=length_).astype(bool)
        bad_indices.extend((indices, indices.tolist()))

    invalid_indices = np.append(
        np.arange(-length * 2, -length), np.arange(length, length * 2)
    )
    for length_ in (length // 4, length // 2, length, length * 2, length * 4):
        for _ in range(3):
            indices = np.random.choice(invalid_indices, length_)
            bad_indices.extend((indices, indices.tolist()))

    # Duplicated indices.
    all_indices = np.arange(-length, length)
    for length_ in (length * 2, length * 4):
        for _ in range(3):
            indices = np.random.choice(all_indices, length_)
            bad_indices.extend((indices, indices.tolist()))

    for indices in bad_indices:
        value = np.random.randint(-1000, 1000)
        with pytest.raises(exceptions.InvalidIndexError):
            fancy_indexing_dataset[column_name, indices] = value
        assert (target == fancy_indexing_dataset[column_name]).all()
        with pytest.raises(exceptions.InvalidIndexError):
            fancy_indexing_dataset[indices, column_name] = value
        assert (target == fancy_indexing_dataset[column_name]).all()
