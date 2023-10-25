"""
Test Dataset class.
"""

import os.path
import shutil
import string
import tempfile
from datetime import datetime
from glob import glob
from typing import List, Optional, cast

import numpy as np
import pandas as pd
import pytest

from renumics.spotlight import (
    Audio,
    Dataset,
    Embedding,
    Image,
    Mesh,
    Sequence1D,
    Video,
)
from renumics.spotlight.dataset import escape_dataset_name, unescape_dataset_name
from renumics.spotlight import dtypes
from renumics.spotlight.dataset.typing import OutputType
from renumics.spotlight.dataset.pandas import infer_dtype
from .conftest import ColumnData
from .helpers import get_append_column_fn_name
from ..helpers import approx


@pytest.mark.parametrize(
    "name",
    [
        "",
        "foo",
        "foo/bar/baz",
        "file:///foo",
        "foo/\\/\\/\\bar",
        "a/sb",
        "a\\sb",
        "a//s",
    ],
)
def test_escape_unescape_dataset_name(name: str) -> None:
    """
    Test `renumics.spotlight.dataset._escape_dataset_name` and
    `renumics.spotlight.dataset._unescape_dataset_name` functions.
    """
    escaped_name = escape_dataset_name(name)
    assert "/" not in escaped_name
    assert unescape_dataset_name(escaped_name) == name


def test_empty_dataset() -> None:
    """
    Test dataset creation without filling.
    """
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            assert dataset.filepath == output_h5_file
            assert dataset.mode == "w"
            assert len(list(dataset.iterrows())) == 0
            assert len(dataset) == 0
            assert len(dataset.keys()) == 0
            print(dataset)
        with Dataset(output_h5_file, "r") as dataset:
            assert dataset.filepath == output_h5_file
            assert dataset.mode == "r"
            assert len(list(dataset.iterrows())) == 0
            assert len(dataset) == 0
            assert len(dataset.keys()) == 0
            print(dataset)


def test_initialized_dataset(optional_data: List[ColumnData]) -> None:
    """
    Test column creation without filling.
    """
    column_names = set(sample.name for sample in optional_data)
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            for sample in optional_data:
                append_fn = getattr(
                    dataset, get_append_column_fn_name(sample.dtype_name)
                )
                append_fn(sample.name, **sample.attrs)
            assert len(list(dataset.iterrows())) == 0
            assert len(dataset) == 0
            assert set(dataset.keys()) == column_names
            for sample in optional_data:
                assert dataset.get_dtype(sample.name).name is sample.dtype_name
            print(dataset)
        with Dataset(output_h5_file, "r") as dataset:
            assert len(list(dataset.iterrows())) == 0
            assert len(dataset) == 0
            assert set(dataset.keys()) == column_names
            for sample in optional_data:
                assert dataset.get_dtype(sample.name).name is sample.dtype_name
            print(dataset)


def test_optional_columns(optional_data: List[ColumnData]) -> None:
    """
    Test creation of and writing into optional columns with and without a default value.
    """

    column_names = set(sample.name for sample in optional_data)
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            sample = optional_data[0]
            values = [None] * 10
            append_fn = getattr(dataset, get_append_column_fn_name(sample.dtype_name))
            if sample.optional:
                append_fn(sample.name, values, optional=sample.optional, **sample.attrs)
            else:
                append_fn(sample.name, values, default=sample.default, **sample.attrs)
            for sample in optional_data[1:]:
                append_fn = getattr(
                    dataset, get_append_column_fn_name(sample.dtype_name)
                )
                if sample.optional:
                    append_fn(sample.name, optional=sample.optional, **sample.attrs)
                else:
                    append_fn(sample.name, default=sample.default, **sample.attrs)
            assert len(dataset) == 10
            assert set(dataset.keys()) == column_names
            for sample in optional_data:
                dtype_name = sample.dtype_name
                default = sample.default
                if default is None:
                    if dtype_name == "str":
                        default = ""
                    elif dtype_name == "float":
                        default = float("nan")
                    elif dtype_name == "Window":
                        default = [float("nan"), float("nan")]
                assert dataset.get_dtype(sample.name).name == dtype_name
                assert approx(
                    default,
                    dataset.get_column_attributes(sample.name)["default"],
                    dataset.get_dtype(sample.name).name,
                )
            for _ in range(10):
                dataset.append_row()
            assert len(dataset) == 20
            assert set(dataset.keys()) == column_names
            for sample in optional_data:
                dtype_name = sample.dtype_name
                default = sample.default
                if default is None:
                    if dtype_name == "str":
                        default = ""
                    elif dtype_name == "float":
                        default = float("nan")
                    elif dtype_name == "Window":
                        default = [float("nan"), float("nan")]
                assert dataset.get_dtype(sample.name).name == sample.dtype_name
                for dataset_value in dataset[sample.name]:
                    assert approx(
                        default, dataset_value, dataset.get_dtype(sample.name).name
                    )
            print(dataset)


def test_append_row(
    simple_data: List[ColumnData], complex_data: List[ColumnData]
) -> None:
    """
    Test row-wise dataset filling.
    """

    data = simple_data + complex_data
    names = {sample.name for sample in data}
    length = len(data[0].values)
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            for sample in data:
                append_fn = getattr(
                    dataset, get_append_column_fn_name(sample.dtype_name)
                )
                append_fn(sample.name, **sample.attrs)
            for i in range(length):
                data_dict = {sample.name: sample.values[i] for sample in data}
                dataset.append_row(**data_dict)
            assert len(list(dataset.iterrows())) == length
            assert len(dataset) == length
            assert set(dataset.keys()) == names
            print(dataset)
        with Dataset(output_h5_file, "r") as dataset:
            assert len(list(dataset.iterrows())) == length
            assert len(dataset) == length
            assert set(dataset.keys()) == names
            print(dataset)
            for i, dataset_row in enumerate(dataset.iterrows()):
                data_dict = {sample.name: sample.values[i] for sample in data}
                assert dataset_row.keys() == names
                for name in names:
                    value = data_dict[name]
                    dataset_value = dataset_row[name]
                    dtype = dataset.get_dtype(name)
                    assert approx(value, dataset_value, dtype.name)
        with Dataset(output_h5_file, "a") as dataset:
            dataset_length = len(dataset)
            for i in range(length):
                dataset += {sample.name: sample.values[i] for sample in data}
            assert len(dataset) == dataset_length + length
            assert set(dataset.keys()) == names
            print(dataset)


def test_insert_row(
    simple_data: List[ColumnData], complex_data: List[ColumnData]
) -> None:
    """
    Test `Dataset.insert_row` method.
    """

    data = simple_data + complex_data
    names = {sample.name for sample in data}
    length = len(data[0].values)
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            for sample in data:
                append_fn = getattr(
                    dataset, get_append_column_fn_name(sample.dtype_name)
                )
                append_fn(sample.name, **sample.attrs)
            for i in range(length):
                data_dict = {sample.name: sample.values[i] for sample in data}
                dataset.append_row(**data_dict)
            assert len(list(dataset.iterrows())) == length
            assert len(dataset) == length
            assert set(dataset.keys()) == names
            print(dataset)
        with Dataset(output_h5_file, "a") as dataset:
            for i, index in enumerate([2, 0, 7, -1, -4, -11]):
                data_dict = {sample.name: sample.values[i] for sample in data}
                dataset.insert_row(index, data_dict)
                assert len(dataset) == length + 1
                length += 1
                if index < 0:
                    index -= 1
                dataset_row = dataset[index]
                assert dataset_row.keys() == names
                for name in names:
                    value = data_dict[name]
                    dataset_value = dataset_row[name]
                    assert approx(value, dataset_value, dataset.get_dtype(name).name)


def test_append_common_column(
    simple_data: List[ColumnData], complex_data: List[ColumnData]
) -> None:
    """
    Test `append_column` method on all data.
    """
    data = simple_data + complex_data
    names = {sample.name for sample in data}
    length = len(data[0].values)
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            for sample in data:
                dataset.append_column(
                    sample.name,
                    sample.dtype_name,
                    sample.values,
                    description=sample.description,
                    **sample.attrs,
                )
            assert len(list(dataset.iterrows())) == length
            assert len(dataset) == length
            assert set(dataset.keys()) == names
            print(dataset)
        with Dataset(output_h5_file, "r") as dataset:
            assert len(list(dataset.iterrows())) == length
            assert len(dataset) == length
            assert set(dataset.keys()) == names
            print(dataset)
            for sample in data:
                dtype_name = sample.dtype_name
                assert dataset.get_dtype(sample.name).name == dtype_name
                dataset_values = dataset[sample.name]
                for value, dataset_value in zip(sample.values, dataset_values):
                    assert approx(value, dataset_value, dtype_name)


def test_append_delete_column(
    simple_data: List[ColumnData], complex_data: List[ColumnData]
) -> None:
    """
    Test append/delete column.
    """
    data = simple_data + complex_data
    names = {sample.name for sample in data}
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            for sample in data:
                dataset.append_column(
                    sample.name, sample.dtype_name, sample.values, **sample.attrs
                )

        with Dataset(output_h5_file, "a") as dataset:
            for key in dataset.keys():
                del dataset[key]
                names.remove(key)
                assert set(dataset.keys()) == names
            assert len(list(dataset.iterrows())) == 0
            assert len(dataset) == 0
            assert len(dataset.keys()) == 0

        with Dataset(output_h5_file, "r") as dataset:
            assert len(list(dataset.iterrows())) == 0
            assert len(dataset) == 0
            assert len(dataset.keys()) == 0


def test_isnull_notnull(empty_dataset: Dataset) -> None:
    """
    Test `Dataset.isnull` and `Dataset.notnull` methods.
    """

    # Test non-nullable data types.
    empty_dataset.append_bool_column("bool", [True, False] * 5)
    null_mask = np.full(len(empty_dataset), False)
    assert approx(null_mask, empty_dataset.isnull("bool"), "array")
    assert approx(~null_mask, empty_dataset.notnull("bool"), "array")
    empty_dataset.append_int_column("int", range(len(empty_dataset)))
    assert approx(null_mask, empty_dataset.isnull("int"), "array")
    assert approx(~null_mask, empty_dataset.notnull("int"), "array")
    empty_dataset.append_string_column("string", ["", "foo", "barbaz", "", ""] * 2)
    assert approx(null_mask, empty_dataset.isnull("string"), "array")
    assert approx(~null_mask, empty_dataset.notnull("string"), "array")
    # Test simple nullable data types.
    empty_dataset.append_float_column(
        "float", [0, 1, np.nan, np.nan, np.nan, -1000, np.inf, -np.inf, 8, np.nan]
    )
    null_mask = np.array(
        [False, False, True, True, True, False, False, False, False, True]
    )
    assert approx(null_mask, empty_dataset.isnull("float"), "array")
    assert approx(~null_mask, empty_dataset.notnull("float"), "array")
    now = datetime.now()
    empty_dataset.append_datetime_column(
        "datetime",
        [
            now,
            now,
            np.datetime64("NaT"),
            None,
            None,
            now,
            now,
            now,
            now,
            np.datetime64("NaT"),
        ],
        optional=True,
    )
    assert approx(null_mask, empty_dataset.isnull("datetime"), "array")
    assert approx(~null_mask, empty_dataset.notnull("datetime"), "array")
    empty_dataset.append_categorical_column(
        "category",
        ["foo", "foo", None, None, None, "barbaz", "barbaz", "barbaz", "foo", None],
        optional=True,
        categories=["barbaz", "foo"],
    )
    assert approx(null_mask, empty_dataset.isnull("category"), "array")
    assert approx(~null_mask, empty_dataset.notnull("category"), "array")
    # Test complex nullable data types.
    values = np.full(len(empty_dataset), None)
    values[~null_mask] = Embedding([0, 1, 2, 3])
    empty_dataset.append_embedding_column("embedding", values, optional=True)
    assert approx(null_mask, empty_dataset.isnull("embedding"), "array")
    assert approx(~null_mask, empty_dataset.notnull("embedding"), "array")
    values[~null_mask] = Sequence1D([0, 1, 2, 3])
    empty_dataset.append_sequence_1d_column("sequence_1d", values, optional=True)
    assert approx(null_mask, empty_dataset.isnull("sequence_1d"), "array")
    assert approx(~null_mask, empty_dataset.notnull("sequence_1d"), "array")
    values[~null_mask] = Mesh.empty()
    empty_dataset.append_mesh_column("mesh", values, optional=True)
    assert approx(null_mask, empty_dataset.isnull("mesh"), "array")
    assert approx(~null_mask, empty_dataset.notnull("mesh"), "array")
    values[~null_mask] = Image.empty()
    empty_dataset.append_image_column("image", values, optional=True)
    assert approx(null_mask, empty_dataset.isnull("image"), "array")
    assert approx(~null_mask, empty_dataset.notnull("image"), "array")
    values[~null_mask] = Audio.empty()
    empty_dataset.append_audio_column("audio", values, optional=True)
    assert approx(null_mask, empty_dataset.isnull("audio"), "array")
    assert approx(~null_mask, empty_dataset.notnull("audio"), "array")
    values[~null_mask] = Video.empty()
    empty_dataset.append_video_column("video", values, optional=True)
    assert approx(null_mask, empty_dataset.isnull("video"), "array")
    assert approx(~null_mask, empty_dataset.notnull("video"), "array")
    # Test window data type.
    windows = np.random.random((len(empty_dataset), 2))
    null_mask = np.full(len(windows), False)
    windows[0] = np.nan
    windows[1, 0] = np.nan
    windows[2, 1] = np.nan
    windows[3] = [-np.inf, np.inf]
    windows[-1] = [np.nan, np.nan]
    null_mask[0] = True
    null_mask[-1] = True
    empty_dataset.append_window_column("window", windows)
    assert approx(null_mask, empty_dataset.isnull("window"), "array")
    assert approx(~null_mask, empty_dataset.notnull("window"), "array")


def test_rename_column(
    simple_data: List[ColumnData], complex_data: List[ColumnData]
) -> None:
    """
    Test `Dataset.rename_column` method.
    """
    data = simple_data + complex_data
    names = {sample.name for sample in data}
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            for sample in data:
                dataset.append_column(
                    sample.name, sample.dtype_name, sample.values, **sample.attrs
                )

        with Dataset(output_h5_file, "a") as dataset:
            assert set(dataset.keys()) == names
            for key in dataset.keys():
                dataset.rename_column(key, f"{key}_")
            names = {f"{name}_" for name in names}
            assert set(dataset.keys()) == names

        with Dataset(output_h5_file, "r") as dataset:
            assert set(dataset.keys()) == names
            for sample in data:
                name = f"{sample.name}_"
                assert name in dataset.keys()
                dataset_values = dataset[name]
                column_type = sample.dtype_name
                for value, dataset_value in zip(sample.values, dataset_values):
                    assert approx(value, dataset_value, column_type)


def test_getitem(simple_data: List[ColumnData], complex_data: List[ColumnData]) -> None:
    """
    Test `Dataset.__getitem__` method.
    """

    data = simple_data + complex_data
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            for sample in data:
                dataset.append_column(
                    sample.name,
                    sample.dtype_name,
                    sample.values,
                    description=sample.description,
                    **sample.attrs,
                )

        with Dataset(output_h5_file, "r") as dataset:
            for sample in data:
                column_name, values = sample.name, sample.values
                dtype = dataset.get_dtype(column_name)
                # Test `dataset[column_name]` getter.
                dataset_values = list(dataset[column_name])
                assert len(dataset_values) == len(values)
                for dataset_value, value in zip(dataset_values, values):
                    approx(value, dataset_value, dtype.name)

            for i in range(-len(dataset), len(dataset)):
                data_dict = {sample.name: sample.values[i] for sample in data}
                # Test `dataset[row_index]` getter.
                dataset_row = dataset[i]
                assert isinstance(dataset_row, dict)
                assert dataset_row.keys() == data_dict.keys()
                for key, value in data_dict.items():
                    dataset_value = dataset_row[key]
                    assert approx(value, dataset_value, dataset.get_dtype(key).name)
                for key, value in data_dict.items():
                    dtype = dataset.get_dtype(key)
                    # Test `dataset[column_name, row_index]` getter.
                    dataset_value = dataset[key, i]
                    assert approx(value, dataset_value, dtype.name)
                    # Test `dataset[row_index, column_name]` getter.
                    dataset_value = dataset[i, key]
                    assert approx(value, dataset_value, dtype.name)


def test_setitem(simple_data: List[ColumnData], complex_data: List[ColumnData]) -> None:
    """
    Test `Dataset.__getitem__` method.
    """
    data = simple_data + complex_data
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            for sample in data:
                dataset.append_column(
                    sample.name,
                    sample.dtype_name,
                    sample.values,
                    description=sample.description,
                    **sample.attrs,
                )

        with Dataset(output_h5_file, "a") as dataset:
            for key in dataset.keys():
                values = dataset[key]
                if dataset.get_dtype(key).name != "array":
                    for value in values:
                        dataset[key] = value
                dataset[key] = values
            for i in range(-len(dataset), len(dataset)):
                dataset[i] = dataset[i]  # type: ignore
            dataset[0] = dataset[-3]  # type: ignore
            dataset[-3] = dataset[5]  # type: ignore
            dataset[2] = dataset[-1]  # type: ignore
            dataset.append_row(**dataset[-2])
            dataset.append_row(**dataset[1])
            dataset[-7] = dataset[7]  # type: ignore
            for key in dataset.keys():
                for i in range(-len(dataset), len(dataset)):
                    dataset[key, i] = dataset[key, i]
                    dataset[key, i] = dataset[i, key]
                    dataset[i, key] = dataset[key, i]
                    dataset[i, key] = dataset[i, key]
                column_values = dataset[key]
                for i, value in zip(range(-1, -len(dataset) - 1, -1), column_values):
                    dataset[key, i] = value


def test_delitem(simple_data: List[ColumnData], complex_data: List[ColumnData]) -> None:
    """
    Test `Dataset.__delitem__` method.
    """
    data = simple_data + complex_data
    names = {sample.name for sample in data}
    length = len(data[0].values)
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            for sample in data:
                dataset.append_column(
                    sample.name,
                    sample.dtype_name,
                    sample.values,
                    description=sample.description,
                    **sample.attrs,
                )
            dataset += dataset
            length *= 2
            assert len(dataset) == length

        with Dataset(output_h5_file, "a") as dataset:
            for name in np.random.choice(list(names), 5, replace=False):
                del dataset[name]
                assert set(dataset.keys()) == names.difference({name})
                names.discard(name)

        with Dataset(output_h5_file, "a") as dataset:
            del dataset[5]
            assert len(dataset) == length - 1
            length -= 1
            del dataset[-10]
            assert len(dataset) == length - 1
            length -= 1
            del dataset[-1]
            assert len(dataset) == length - 1
            length -= 1
            del dataset[0]
            assert len(dataset) == length - 1
            length -= 1
            for _ in range(length):
                del dataset[0]
            assert len(dataset) == 0


def test_iterrows(
    simple_data: List[ColumnData], complex_data: List[ColumnData]
) -> None:
    """
    Test `Dataset.iterrows` method.
    """

    data = simple_data + complex_data
    keys1 = (data[1].name, data[2].name, data[3].name)
    keys2 = [data[3].name, data[-5].name, data[-10].name]
    keys3 = {sample.name for sample in data}
    keys4 = [sample.name for sample in data]
    keys5 = [data[1].name, data[1].name, data[1].name]
    keys6 = [data[1].name, data[1].name, data[1].name]
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            for sample in data:
                dataset.append_column(
                    sample.name,
                    sample.dtype_name,
                    sample.values,
                    description=sample.description,
                    **sample.attrs,
                )
            for dataset_row in dataset.iterrows():
                assert dataset_row.keys() == set(dataset.keys())
            for keys in (keys1, keys2, keys3, keys4, keys5, keys6):
                for dataset_row1 in dataset.iterrows(keys):
                    assert dataset_row1.keys() == set(keys)  # type: ignore
            for dataset_row2 in dataset.iterrows(sample.name for sample in data):
                assert dataset_row2.keys() == set(sample.name for sample in data)  # type: ignore
            for sample in data:
                values = sample.values
                dtype_name = dataset.get_dtype(sample.name).name
                dataset_values = dataset.iterrows(sample.name)
                for value, dataset_value in zip(values, dataset_values):
                    dataset_value = cast(Optional[OutputType], dataset_value)
                    assert approx(value, dataset_value, dtype_name)


def test_append_dataset(
    simple_data: List[ColumnData], complex_data: List[ColumnData]
) -> None:
    """
    Test `append_dataset` method on all data.
    """
    data = simple_data + complex_data
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            for sample in data:
                dataset.append_column(
                    sample.name,
                    sample.dtype_name,
                    sample.values,
                    description=sample.description,
                    **sample.attrs,
                )
            assert len(dataset) == 6

        with Dataset(output_h5_file, "a") as dataset, Dataset(
            output_h5_file, "r"
        ) as dataset1:
            dataset_length = len(dataset)
            dataset.append_dataset(dataset1)
            assert len(dataset) == 2 * dataset_length

        output_h5_file1 = os.path.join(output_folder, "dataset1.h5")
        with Dataset(output_h5_file1, "w") as dataset:
            for sample in data:
                dataset.append_column(
                    sample.name,
                    sample.dtype_name,
                    sample.values,
                    description=sample.description,
                    **sample.attrs,
                )
            assert len(dataset) == 6

        with Dataset(output_h5_file, "a") as dataset, Dataset(
            output_h5_file1, "r"
        ) as dataset1:
            dataset_length = len(dataset)
            dataset_length1 = len(dataset1)
            dataset.append_dataset(dataset1)
            assert len(dataset) == dataset_length + dataset_length1

        with Dataset(output_h5_file, "a") as dataset, Dataset(
            output_h5_file1, "r"
        ) as dataset1:
            dataset_length = len(dataset)
            dataset_length1 = len(dataset1)
            dataset += dataset1
            assert len(dataset) == dataset_length + dataset_length1


def test_copy_column(
    simple_data: List[ColumnData], complex_data: List[ColumnData]
) -> None:
    """
    Test `append_column` method on all data.
    """

    data = simple_data + complex_data
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            for sample in data:
                dataset.append_column(
                    sample.name,
                    sample.dtype_name,
                    sample.values,
                    description=sample.description,
                    **sample.attrs,
                )

        with Dataset(output_h5_file, "a") as dataset:
            for name in dataset.keys():
                dtype = dataset.get_dtype(name)
                kwargs = dataset.get_column_attributes(name)
                values = dataset[name]
                dataset.append_column(f"new {name}", dtype, values, **kwargs)


def test_pop(simple_data: List[ColumnData], complex_data: List[ColumnData]) -> None:
    """
    Test `Dataset.pop` method.
    """

    data = simple_data + complex_data
    names = {sample.name for sample in data}
    length = len(data[0].values)
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            for sample in data:
                dataset.append_column(
                    sample.name,
                    sample.dtype_name,
                    sample.values,
                    description=sample.description,
                    **sample.attrs,
                )
            assert len(dataset) == length

        with Dataset(output_h5_file, "a") as dataset:
            for name in np.random.choice(list(names), 5, replace=False):
                dtype = dataset.get_dtype(name)
                actual_values = dataset.pop(name)
                for target, actual in zip(
                    next((x.values for x in data if x.name == name)), actual_values
                ):
                    assert approx(target, actual, dtype.name)
                assert set(dataset.keys()) == names.difference({name})
                names.discard(name)

        with Dataset(output_h5_file, "a") as dataset:
            for index in (3, -2, 0, -1, *([0] * (length - 4))):
                target = dataset[index]
                actual = dataset.pop(index)
                assert target.keys() == actual.keys()
                for key, value in target.items():
                    assert approx(value, actual[key], dataset.get_dtype(key).name)
                assert len(dataset) == length - 1
                length -= 1
            assert len(dataset) == 0


def test_set_attributes_column(
    simple_data: List[ColumnData], complex_data: List[ColumnData]
) -> None:
    """
    Test `set_attributes` method on all data.
    """

    data = simple_data + complex_data
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            for sample in data:
                dataset.append_column(
                    sample.name,
                    sample.dtype_name,
                    sample.values,
                    default=sample.values[0],
                    description=sample.description,
                    **sample.attrs,
                )

        with Dataset(output_h5_file, "a") as dataset:
            for name in dataset.keys():
                dtype = dataset.get_dtype(name)
                kwargs = dataset.get_column_attributes(name)
                values = dataset[name]
                name = f"new_{name}"
                dataset.append_column(
                    name,
                    dtype,
                    values,
                    **(
                        {"categories": kwargs["categories"]}
                        if "categories" in kwargs
                        else {}
                    ),
                )
                if "lookup" in kwargs:
                    del kwargs["lookup"]
                dataset.set_column_attributes(name, **kwargs)
                dataset.set_column_attributes(name, **kwargs)

        with Dataset(output_h5_file, "a") as dataset:
            for column_name in dataset.keys():
                if column_name.startswith("new "):
                    column_attributes = dataset.get_column_attributes(column_name[4:])
                    column_attributes_new = dataset.get_column_attributes(column_name)
                    for attribute_key, column_attribute in column_attributes.items():
                        if attribute_key == "default":
                            approx(
                                column_attribute,
                                column_attributes_new[attribute_key],
                                dataset.get_dtype(column_name).name,
                            )
                        else:
                            assert (
                                column_attributes_new[attribute_key] == column_attribute
                            )


def test_import_export_pandas() -> None:
    """
    Test `Dataset.from_pandas` and `Dataset.to_pandas` methods on australian
    weather dataset.
    """
    df = pd.read_csv("build/datasets/multimodal-random-1000.csv")
    df["category"] = df["category"].astype("category")
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    for name, dtype in df.dtypes.items():
        if dtype is np.dtype(object):
            df[name].fillna("", inplace=True)
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            dataset.from_pandas(df, index=True)

        with Dataset(output_h5_file, "r") as dataset:
            assert len(dataset) == len(df)
            # A few columns are dropped because of incompatible values,
            # so just check that some are imported for now
            assert dataset.keys()


def test_import_pandas_with_dtype() -> None:
    """
    Test `Dataset.import_pandas` with defined `dtype` argument.
    """
    df = pd.read_csv("build/datasets/multimodal-random-1000.csv")
    dtypes = {
        "audio": "str",
        "image": "str",
        "mesh": "str",
        "video": "str",
        "embedding": "Embedding",
        "window": "Window",
        "bool": "bool",
        "int": "int",
        "float": "float",
        "str": "str",
        "datetime": "datetime",
        "category": "Category",
    }
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            dataset.from_pandas(df, dtypes=dtypes)
            assert dtypes == {key: dataset.get_dtype(key).name for key in dtypes}


def test_import_csv() -> None:
    """
    Test `Dataset.from_csv` method simple.
    """
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            dataset.from_csv("build/datasets/multimodal-random-1000.csv")
            # A few columns are dropped because of incompatible values,
            # so just check that some are imported for now
            assert dataset.keys()


def test_import_csv_with_dtype() -> None:
    """
    Test `Dataset.from_csv` method advanced.
    """

    with tempfile.TemporaryDirectory() as output_folder:
        csv_file = os.path.join(output_folder, "input.csv")
        output_h5_file = os.path.join(output_folder, "dataset.h5")

        for folder_name in ("audio", "images", "meshes", "videos"):
            shutil.copytree(
                os.path.join("data", folder_name),
                os.path.join(output_folder, folder_name) + ".copy",
            )

        df = pd.DataFrame()
        df["bool"] = df["bool1"] = np.random.randint(2, size=10).astype(bool)
        df["int"] = df["int1"] = df["int2"] = np.random.randint(-1000, 1000, 10)
        df["float"] = df["float1"] = np.random.random(10)
        indices = np.random.choice(len(df), 3, replace=False)
        df.loc[indices, "float"] = [np.nan, np.inf, -np.inf]  # type: ignore
        df.loc[indices, "float1"] = [np.nan, np.inf, -np.inf]  # type: ignore
        df["string"] = df["string1"] = [
            "".join(
                np.random.choice(list(string.ascii_letters), np.random.randint(1, 22))
            )
            for _ in range(10)
        ]
        df["datetime"] = df["datetime1"] = np.arange(
            "2002-10-27T04:30", 10 * 60, 60, np.datetime64
        )
        df["array"] = df["array1"] = df["array2"] = df["array3"] = np.random.randint(
            -1000, 1000, (10, 4)
        ).tolist()
        df["array4"] = [
            np.random.random(np.random.randint(0, 10)).tolist() for _ in range(8)
        ] + [[], []]
        df["audio"] = df["audio1"] = df["audio2"] = np.random.choice(
            list(
                filter(
                    os.path.isfile,
                    glob(
                        f"{os.path.join(output_folder, 'audio.copy')}/**",
                        recursive=True,
                    ),
                )
            ),
            10,
        )
        df["image"] = df["image1"] = df["image2"] = np.random.choice(
            list(
                filter(
                    os.path.isfile,
                    glob(
                        f"{os.path.join(output_folder, 'images.copy')}/**",
                        recursive=True,
                    ),
                )
            ),
            10,
        )
        df["mesh"] = df["mesh1"] = df["mesh2"] = np.random.choice(
            list(
                filter(
                    os.path.isfile,
                    glob(
                        f"{os.path.join(output_folder, 'meshes.copy')}/**",
                        recursive=True,
                    ),
                )
            ),
            10,
        )
        df["video"] = df["video1"] = df["video2"] = np.random.choice(
            list(
                filter(
                    os.path.isfile,
                    glob(
                        f"{os.path.join(output_folder, 'videos.copy')}/**",
                        recursive=True,
                    ),
                )
            ),
            10,
        )
        columns = df.columns.tolist()

        df["string2"] = df["string1"]
        df["datetime2"] = df["datetime1"]
        df["array5"] = df["array6"] = df["array7"] = df["array3"]
        df["array8"] = df["array4"]
        df["audio3"] = df["audio2"]
        df["image3"] = df["image2"]
        df["mesh3"] = df["mesh2"]
        df["video3"] = df["video2"]
        optional_or_nan_columns: List[str] = list(df.columns.difference(columns))

        df.loc[indices, optional_or_nan_columns] = ""  # type: ignore

        df.to_csv(csv_file, index=False)

        dtypes = {
            "string1": "Category",
            "datetime1": "datetime",
        }
        with Dataset(output_h5_file, "w") as dataset:
            dataset.from_csv(csv_file, dtypes)
            assert set(dataset.keys()) == set(df.keys())
            assert {key: dataset.get_dtype(key).name for key in dtypes} == dtypes

        columns += optional_or_nan_columns
        dtypes.update(
            {
                "string2": "Category",
                "datetime2": "datetime",
                "array5": "array",
                "array6": "Embedding",
                "array7": "Sequence1D",
                "array8": "array",
                "audio3": "Audio",
                "image3": "Image",
                "mesh3": "Mesh",
                "video3": "Video",
            }
        )
        with Dataset(output_h5_file, "w") as dataset:
            dataset.from_csv(csv_file, dtypes)
            assert set(dataset.keys()) == set(columns)
            assert {key: dataset.get_dtype(key).name for key in dtypes} == dtypes


def test_to_pandas() -> None:
    exported_dtypes = (
        dtypes.bool_dtype,
        dtypes.int_dtype,
        dtypes.float_dtype,
        dtypes.str_dtype,
        dtypes.datetime_dtype,
        dtypes.CategoryDType(["foo", "bar"]),
    )

    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            for dtype in exported_dtypes:
                dataset.append_column(dtype.name, dtype, optional=True)
            df = dataset.to_pandas()
        for dtype in exported_dtypes:
            column_name = dtype.name
            assert column_name in df
            inferred_dtype = infer_dtype(df[column_name])
            if dtypes.is_category_dtype(dtype):
                assert dtypes.is_category_dtype(inferred_dtype)
                assert inferred_dtype.categories == dtype.categories
            else:
                assert inferred_dtype.name == dtype.name
