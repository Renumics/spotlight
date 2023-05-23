"""
Test open of an existing H5 file with any structure as a dataset.
"""
from pathlib import Path

import h5py
import numpy as np
import pytest

from renumics import spotlight


def test_empty_file(tmp_path: Path) -> None:
    """
    Test an empty H5 file.
    """
    h5_filepath = tmp_path / "dataset.h5"
    length = 0
    num_columns = 0
    with h5py.File(h5_filepath, "w"):
        ...
    assert h5_filepath.is_file()
    with spotlight.Dataset(h5_filepath, "r") as dataset:
        assert len(dataset.keys()) == num_columns
        assert len(dataset) == length
    with h5py.File(h5_filepath, "r") as h5_file:
        assert len(h5_file) == num_columns
    with spotlight.Dataset(h5_filepath, "a") as dataset:
        assert len(dataset.keys()) == num_columns
        assert len(dataset) == length
    # When an even empty dataset will be opened
    with h5py.File(h5_filepath, "r") as h5_file:
        assert len(h5_file) == num_columns + 2
        for column_name in spotlight.dataset.INTERNAL_COLUMN_NAMES:
            assert column_name in h5_file
            h5_dataset = h5_file[column_name]
            assert isinstance(h5_dataset, h5py.Dataset)
            assert len(h5_dataset) == length


@pytest.mark.parametrize("length", [0, 1, 10, 50])
@pytest.mark.parametrize("num_columns", [1, 10, 20])
def test_consistent_file(tmp_path: Path, length: int, num_columns: int) -> None:
    """
    Test a H5 file with multiple datasets of the same length.
    """
    h5_filepath = tmp_path / "dataset.h5"
    with h5py.File(h5_filepath, "w") as h5_file:
        for i in range(num_columns):
            h5_dataset = h5_file.create_dataset(
                f"column_{i}", (length,), np.float64, maxshape=(None,)
            )
            h5_dataset.attrs["type"] = "float"
    assert h5_filepath.is_file()
    with spotlight.Dataset(h5_filepath, "r") as dataset:
        assert len(dataset.keys()) == num_columns
        assert len(dataset) == length
    with h5py.File(h5_filepath, "r") as h5_file:
        assert len(h5_file) == num_columns
    with spotlight.Dataset(h5_filepath, "a") as dataset:
        assert len(dataset.keys()) == num_columns
        assert len(dataset) == length
    # When a dataset is opened if w/a mode, internal columns should be created.
    with h5py.File(h5_filepath, "r") as h5_file:
        assert len(h5_file) == num_columns + 2
        for column_name in spotlight.dataset.INTERNAL_COLUMN_NAMES:
            assert column_name in h5_file
            h5_dataset = h5_file[column_name]
            assert isinstance(h5_dataset, h5py.Dataset)
            assert len(h5_dataset) == length


def test_inconsistent_file(tmp_path: Path) -> None:
    """
    Test a H5 file with multiple columns of different lengths.
    """
    h5_filepath = tmp_path / "dataset.h5"
    length = 10
    with h5py.File(h5_filepath, "w") as h5_file:
        # Valid columns.
        for i in (0, 1, 2):
            h5_dataset = h5_file.create_dataset(
                f"column_{i}", (length,), np.float64, maxshape=(None,)
            )
            h5_dataset.attrs["type"] = "float"
        # Short columns.
        for i in (3, 4):
            h5_dataset = h5_file.create_dataset(
                f"column_{i}", (length - 2,), np.float64, maxshape=(None,)
            )
            h5_dataset.attrs["type"] = "float"
        # Invalid short columns.
        for i in (5, 6):
            h5_file.create_dataset(
                f"column_{i}", (length - 2,), np.float64, maxshape=(None,)
            )
        # Long columns.
        for i in (7, 8):
            h5_dataset = h5_file.create_dataset(
                f"column_{i}", (length + 2,), np.float64, maxshape=(None,)
            )
            h5_dataset.attrs["type"] = "float"
    assert h5_filepath.is_file()
    columns = {"column_0", "column_1", "column_2"}
    num_columns = len(columns)
    with spotlight.Dataset(h5_filepath, "r") as dataset:
        assert len(dataset.keys()) == 3
        assert set(dataset.keys()) == columns
        assert len(dataset) == length
    with h5py.File(h5_filepath, "r") as h5_file:
        assert len(h5_file) == 9
    with spotlight.Dataset(h5_filepath, "a") as dataset:
        assert len(dataset.keys()) == num_columns
        assert len(dataset) == length
    # When a dataset is opened if w/a mode, internal columns should be created.
    with h5py.File(h5_filepath, "r") as h5_file:
        assert len(h5_file) == 9 + 2
        for column_name in spotlight.dataset.INTERNAL_COLUMN_NAMES:
            assert column_name in h5_file
            h5_dataset = h5_file[column_name]
            assert isinstance(h5_dataset, h5py.Dataset)
            assert len(h5_dataset) == length
    with spotlight.Dataset(h5_filepath, "a") as dataset:
        dataset.append_string_column("column_9", optional=True)
        with pytest.raises(spotlight.dataset.exceptions.ColumnExistsError):
            dataset.append_string_column("column_1", optional=True)
            dataset.append_string_column("column_3", optional=True)
            dataset.append_string_column("column_5", optional=True)
            dataset.append_string_column("column_8", optional=True)


def test_inconsistent_file_multiple_modes(tmp_path: Path) -> None:
    """
    Test a H5 file with multiple columns of different lengths with multiple
    modes.
    """
    h5_filepath = tmp_path / "dataset.h5"
    length = 10
    with h5py.File(h5_filepath, "w") as h5_file:
        for i in (0, 1, 2):
            h5_dataset = h5_file.create_dataset(
                f"column_{i}", (length,), np.float64, maxshape=(None,)
            )
            h5_dataset.attrs["type"] = "float"
    columns = {"column_0", "column_1", "column_2"}
    with spotlight.Dataset(h5_filepath, "r") as dataset:
        assert set(dataset.keys()) == columns
    # Add longer columns.
    with h5py.File(h5_filepath, "a") as h5_file:
        for i in (3, 4, 5):
            h5_dataset = h5_file.create_dataset(
                f"column_{i}", (length * 2,), np.float64, maxshape=(None,)
            )
            h5_dataset.attrs["type"] = "float"
    columns = {"column_3", "column_4", "column_5"}
    with spotlight.Dataset(h5_filepath, "r") as dataset:
        assert set(dataset.keys()) == columns
    # Add longer columns.
    with h5py.File(h5_filepath, "a") as h5_file:
        for i in (6, 7, 8):
            h5_dataset = h5_file.create_dataset(
                f"column_{i}", (length * 3,), np.float64, maxshape=(None,)
            )
            h5_dataset.attrs["type"] = "float"
    columns = {"column_6", "column_7", "column_8"}
    with spotlight.Dataset(h5_filepath, "r") as dataset:
        assert set(dataset.keys()) == columns
    # Add not so long columns.
    with h5py.File(h5_filepath, "a") as h5_file:
        for i in (9, 10, 11):
            h5_dataset = h5_file.create_dataset(
                f"column_{i}", (length * 3 - 1,), np.float64, maxshape=(None,)
            )
            h5_dataset.attrs["type"] = "float"
    with spotlight.Dataset(h5_filepath, "r") as dataset:
        assert set(dataset.keys()) == columns
