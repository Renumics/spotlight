"""
Test Dataset class.
"""
# pylint: disable=too-many-lines
import os.path
import shutil
import string
import tempfile
from datetime import datetime
from glob import glob
from typing import List

import numpy as np
import pandas as pd
import pytest

from renumics.spotlight import (
    Audio,
    Category,
    Dataset,
    Embedding,
    Image,
    Mesh,
    Sequence1D,
    Video,
    Window,
)
from renumics.spotlight.dataset import escape_dataset_name, unescape_dataset_name
from renumics.spotlight.dtypes.typing import ColumnTypeMapping
from tests.test_dataset.conftest import approx, get_append_column_fn_name, ColumnData


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
                    dataset, get_append_column_fn_name(sample.column_type)
                )
                append_fn(sample.name, **sample.attrs)
            assert len(list(dataset.iterrows())) == 0
            assert len(dataset) == 0
            assert set(dataset.keys()) == column_names
            for sample in optional_data:
                assert dataset.get_column_type(sample.name) is sample.column_type
            print(dataset)
        with Dataset(output_h5_file, "r") as dataset:
            assert len(list(dataset.iterrows())) == 0
            assert len(dataset) == 0
            assert set(dataset.keys()) == column_names
            for sample in optional_data:
                assert dataset.get_column_type(sample.name) is sample.column_type
            print(dataset)


def test_optional_columns(optional_data: List[ColumnData]) -> None:
    """
    Test creation of and writing into optional columns with and without a default value.
    """
    # pylint: disable=too-many-branches, too-many-locals
    column_names = set(sample.name for sample in optional_data)
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            sample = optional_data[0]
            values = [None] * 10
            append_fn = getattr(dataset, get_append_column_fn_name(sample.column_type))
            if sample.optional:
                append_fn(sample.name, values, optional=sample.optional, **sample.attrs)
            else:
                append_fn(sample.name, values, default=sample.default, **sample.attrs)
            for sample in optional_data[1:]:
                append_fn = getattr(
                    dataset, get_append_column_fn_name(sample.column_type)
                )
                if sample.optional:
                    append_fn(sample.name, optional=sample.optional, **sample.attrs)
                else:
                    append_fn(sample.name, default=sample.default, **sample.attrs)
            assert len(dataset) == 10
            assert set(dataset.keys()) == column_names
            for sample in optional_data:
                column_type = sample.column_type
                default = sample.default
                if default is None:
                    if column_type is str:
                        default = ""
                    elif column_type is float:
                        default = float("nan")
                    elif column_type is Window:
                        default = [float("nan"), float("nan")]
                assert dataset.get_column_type(sample.name) is column_type
                assert approx(
                    default,
                    dataset.get_column_attributes(sample.name)["default"],
                    dataset.get_column_type(sample.name),
                )
            for _ in range(10):
                dataset.append_row()
            assert len(dataset) == 20
            assert set(dataset.keys()) == column_names
            for sample in optional_data:
                column_type = sample.column_type
                default = sample.default
                if default is None:
                    if column_type is str:
                        default = ""
                    elif column_type is float:
                        default = float("nan")
                    elif column_type is Window:
                        default = [float("nan"), float("nan")]
                assert dataset.get_column_type(sample.name) is sample.column_type
                for dataset_value in dataset[sample.name]:
                    assert approx(
                        default, dataset_value, dataset.get_column_type(sample.name)
                    )
            print(dataset)


def test_append_row(
    simple_data: List[ColumnData], complex_data: List[ColumnData]
) -> None:
    """
    Test row-wise dataset filling.
    """
    # pylint: disable=too-many-locals,
    data = simple_data + complex_data
    names = {sample.name for sample in data}
    length = len(data[0].values)
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            for sample in data:
                append_fn = getattr(
                    dataset, get_append_column_fn_name(sample.column_type)
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
                    assert approx(value, dataset_value, dataset.get_column_type(name))
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
    # pylint: disable=too-many-locals
    data = simple_data + complex_data
    names = {sample.name for sample in data}
    length = len(data[0].values)
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            for sample in data:
                append_fn = getattr(
                    dataset, get_append_column_fn_name(sample.column_type)
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
                    assert approx(value, dataset_value, dataset.get_column_type(name))


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
                    sample.column_type,
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
                column_type = sample.column_type
                assert dataset.get_column_type(sample.name) is column_type
                dataset_values = dataset[sample.name]
                for value, dataset_value in zip(sample.values, dataset_values):
                    assert approx(value, dataset_value, column_type)


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
                    sample.name, sample.column_type, sample.values, **sample.attrs
                )

        with Dataset(output_h5_file, "a") as dataset:
            for key in dataset.keys():  # pylint: disable=consider-using-dict-items
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
    # pylint: disable=too-many-statements
    # Test non-nullable data types.
    empty_dataset.append_bool_column("bool", [True, False] * 5)
    null_mask = np.full(len(empty_dataset), False)
    assert approx(null_mask, empty_dataset.isnull("bool"), np.ndarray)
    assert approx(~null_mask, empty_dataset.notnull("bool"), np.ndarray)
    empty_dataset.append_int_column("int", range(len(empty_dataset)))
    assert approx(null_mask, empty_dataset.isnull("int"), np.ndarray)
    assert approx(~null_mask, empty_dataset.notnull("int"), np.ndarray)
    empty_dataset.append_string_column("string", ["", "foo", "barbaz", "", ""] * 2)
    assert approx(null_mask, empty_dataset.isnull("string"), np.ndarray)
    assert approx(~null_mask, empty_dataset.notnull("string"), np.ndarray)
    # Test simple nullable data types.
    empty_dataset.append_float_column(
        "float", [0, 1, np.nan, np.nan, np.nan, -1000, np.inf, -np.inf, 8, np.nan]
    )
    null_mask = np.array(
        [False, False, True, True, True, False, False, False, False, True]
    )
    assert approx(null_mask, empty_dataset.isnull("float"), np.ndarray)
    assert approx(~null_mask, empty_dataset.notnull("float"), np.ndarray)
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
    assert approx(null_mask, empty_dataset.isnull("datetime"), np.ndarray)
    assert approx(~null_mask, empty_dataset.notnull("datetime"), np.ndarray)
    empty_dataset.append_categorical_column(
        "category",
        ["foo", "foo", "", "", "", "barbaz", "barbaz", "barbaz", "foo", ""],
        optional=True,
    )
    assert approx(null_mask, empty_dataset.isnull("category"), np.ndarray)
    assert approx(~null_mask, empty_dataset.notnull("category"), np.ndarray)
    # Test complex nullable data types.
    values = np.full(len(empty_dataset), None)
    values[~null_mask] = Embedding([0, 1, 2, 3])
    empty_dataset.append_embedding_column("embedding", values, optional=True)
    assert approx(null_mask, empty_dataset.isnull("embedding"), np.ndarray)
    assert approx(~null_mask, empty_dataset.notnull("embedding"), np.ndarray)
    values[~null_mask] = Sequence1D([0, 1, 2, 3])
    empty_dataset.append_sequence_1d_column("sequence_1d", values, optional=True)
    assert approx(null_mask, empty_dataset.isnull("sequence_1d"), np.ndarray)
    assert approx(~null_mask, empty_dataset.notnull("sequence_1d"), np.ndarray)
    values[~null_mask] = Mesh.empty()
    empty_dataset.append_mesh_column("mesh", values, optional=True)
    assert approx(null_mask, empty_dataset.isnull("mesh"), np.ndarray)
    assert approx(~null_mask, empty_dataset.notnull("mesh"), np.ndarray)
    values[~null_mask] = Image.empty()
    empty_dataset.append_image_column("image", values, optional=True)
    assert approx(null_mask, empty_dataset.isnull("image"), np.ndarray)
    assert approx(~null_mask, empty_dataset.notnull("image"), np.ndarray)
    values[~null_mask] = Audio.empty()
    empty_dataset.append_audio_column("audio", values, optional=True)
    assert approx(null_mask, empty_dataset.isnull("audio"), np.ndarray)
    assert approx(~null_mask, empty_dataset.notnull("audio"), np.ndarray)
    values[~null_mask] = Video.empty()
    empty_dataset.append_video_column("video", values, optional=True)
    assert approx(null_mask, empty_dataset.isnull("video"), np.ndarray)
    assert approx(~null_mask, empty_dataset.notnull("video"), np.ndarray)
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
    assert approx(null_mask, empty_dataset.isnull("window"), np.ndarray)
    assert approx(~null_mask, empty_dataset.notnull("window"), np.ndarray)


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
                    sample.name, sample.column_type, sample.values, **sample.attrs
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
                column_type = sample.column_type
                for value, dataset_value in zip(sample.values, dataset_values):
                    assert approx(value, dataset_value, column_type)


def test_getitem(simple_data: List[ColumnData], complex_data: List[ColumnData]) -> None:
    """
    Test `Dataset.__getitem__` method.
    """
    # pylint: disable=too-many-locals
    data = simple_data + complex_data
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            for sample in data:
                dataset.append_column(
                    sample.name,
                    sample.column_type,
                    sample.values,
                    description=sample.description,
                    **sample.attrs,
                )

        with Dataset(output_h5_file, "r") as dataset:
            for sample in data:
                column_name, values = sample.name, sample.values
                column_type = dataset.get_column_type(column_name)
                # Test `dataset[column_name]` getter.
                dataset_values = list(dataset[column_name])
                assert len(dataset_values) == len(values)
                for dataset_value, value in zip(dataset_values, values):
                    approx(value, dataset_value, column_type)

            for i in range(-len(dataset), len(dataset)):
                data_dict = {sample.name: sample.values[i] for sample in data}
                # Test `dataset[row_index]` getter.
                dataset_row = dataset[i]
                assert isinstance(dataset_row, dict)
                assert dataset_row.keys() == data_dict.keys()
                for key, value in data_dict.items():
                    dataset_value = dataset_row[key]
                    assert approx(value, dataset_value, dataset.get_column_type(key))
                for key, value in data_dict.items():
                    column_type = dataset.get_column_type(key)
                    # Test `dataset[column_name, row_index]` getter.
                    dataset_value = dataset[key, i]
                    assert approx(value, dataset_value, column_type)
                    # Test `dataset[row_index, column_name]` getter.
                    dataset_value = dataset[i, key]
                    assert approx(value, dataset_value, column_type)


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
                    sample.column_type,
                    sample.values,
                    description=sample.description,
                    **sample.attrs,
                )

        with Dataset(output_h5_file, "a") as dataset:
            for key in dataset.keys():  # pylint: disable=consider-using-dict-items
                values = dataset[key]
                if dataset.get_column_type(key) is not np.ndarray:
                    for value in values:
                        dataset[key] = value
                dataset[key] = values
            for i in range(-len(dataset), len(dataset)):
                dataset[i] = dataset[i]
            dataset[0] = dataset[-3]
            dataset[-3] = dataset[5]
            dataset[2] = dataset[-1]
            dataset.append_row(**dataset[-2])  # pylint: disable=not-a-mapping
            dataset.append_row(**dataset[1])  # pylint: disable=not-a-mapping
            dataset[-7] = dataset[7]
            for key in dataset.keys():  # pylint: disable=consider-using-dict-items
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
                    sample.column_type,
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
    # pylint: disable=too-many-locals
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
                    sample.column_type,
                    sample.values,
                    description=sample.description,
                    **sample.attrs,
                )
            for dataset_row in dataset.iterrows():  # pylint: disable=not-an-iterable
                assert dataset_row.keys() == set(dataset.keys())
            for keys in (keys1, keys2, keys3, keys4, keys5, keys6):
                for dataset_row in dataset.iterrows(  # pylint: disable=not-an-iterable
                    keys
                ):
                    assert dataset_row.keys() == set(keys)
            for dataset_row in dataset.iterrows(  # pylint: disable=not-an-iterable
                sample.name for sample in data
            ):
                assert dataset_row.keys() == set(sample.name for sample in data)
            for sample in data:
                values = sample.values
                column_type = dataset.get_column_type(sample.name)
                dataset_values = dataset.iterrows(sample.name)
                for value, dataset_value in zip(values, dataset_values):
                    assert approx(value, dataset_value, column_type)


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
                    sample.column_type,
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
                    sample.column_type,
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
    # pylint: disable=too-many-locals
    data = simple_data + complex_data
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            for sample in data:
                dataset.append_column(
                    sample.name,
                    sample.column_type,
                    sample.values,
                    description=sample.description,
                    **sample.attrs,
                )

        with Dataset(output_h5_file, "a") as dataset:
            for name in dataset.keys():  # pylint: disable=consider-using-dict-items
                column_type = dataset.get_column_type(name)
                kwargs = dataset.get_column_attributes(name)
                values = dataset[name]
                dataset.append_column(f"new {name}", column_type, values, **kwargs)


def test_pop(simple_data: List[ColumnData], complex_data: List[ColumnData]) -> None:
    """
    Test `Dataset.pop` method.
    """
    # pylint: disable=too-many-locals
    data = simple_data + complex_data
    names = {sample.name for sample in data}
    length = len(data[0].values)
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            for sample in data:
                dataset.append_column(
                    sample.name,
                    sample.column_type,
                    sample.values,
                    description=sample.description,
                    **sample.attrs,
                )
            assert len(dataset) == length

        with Dataset(output_h5_file, "a") as dataset:
            for name in np.random.choice(list(names), 5, replace=False):
                type_ = dataset.get_column_type(name)
                actual_values = dataset.pop(name)
                for target, actual in zip(
                    next((x.values for x in data if x.name == name)), actual_values
                ):
                    assert approx(target, actual, type_)
                assert set(dataset.keys()) == names.difference({name})
                names.discard(name)

        with Dataset(output_h5_file, "a") as dataset:
            for index in (3, -2, 0, -1, *([0] * (length - 4))):
                target = dataset[index]
                actual = dataset.pop(index)
                assert target.keys() == actual.keys()
                for key, value in target.items():
                    assert approx(value, actual[key], dataset.get_column_type(key))
                assert len(dataset) == length - 1
                length -= 1
            assert len(dataset) == 0


def test_set_attributes_column(
    simple_data: List[ColumnData], complex_data: List[ColumnData]
) -> None:
    """
    Test `set_attributes` method on all data.
    """
    # pylint: disable=too-many-locals,too-many-branches
    data = simple_data + complex_data
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            for sample in data:
                dataset.append_column(
                    sample.name,
                    sample.column_type,
                    sample.values,
                    default=sample.values[0],
                    description=sample.description,
                    **sample.attrs,
                )

        with Dataset(output_h5_file, "a") as dataset:
            for name in dataset.keys():  # pylint: disable=consider-using-dict-items
                column_type = dataset.get_column_type(name)
                kwargs = dataset.get_column_attributes(name)
                values = dataset[name]
                name = f"new_{name}"
                dataset.append_column(
                    name,
                    column_type,
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
                                dataset.get_column_type(column_name),
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
            assert len(dataset) == len(df)
            assert set(dataset.keys()) == {"index", *df.columns}
        with Dataset(output_h5_file, "r") as dataset:
            assert len(dataset) == len(df)
            assert set(dataset.keys()) == {"index", *df.columns}
            df1 = dataset.to_pandas()
    df1 = df1.set_index("index", drop=True)
    assert df.columns.sort_values().equals(df1.columns.sort_values())
    diff = df.sort_index(axis=1).compare(df1.sort_index(axis=1))
    assert diff.empty


def test_import_pandas_with_dtype() -> None:
    """
    Test `Dataset.import_pandas` with defined `dtype` argument.
    """
    df = pd.read_csv("build/datasets/multimodal-random-1000.csv")
    dtype = {
        "audio": str,
        "image": str,
        "mesh": str,
        "video": str,
        "embedding": Embedding,
        "window": Window,
        "bool": bool,
        "int": int,
        "float": float,
        "str": str,
        "datetime": datetime,
        "category": Category,
    }
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            dataset.from_pandas(df, dtype=dtype)
            assert dtype == {key: dataset.get_column_type(key) for key in dtype}


def test_import_csv() -> None:
    """
    Test `Dataset.from_csv` method simple.
    """
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            dataset.from_csv("build/datasets/multimodal-random-1000.csv")
            assert set(dataset.keys()) == set(
                pd.read_csv(
                    "build/datasets/multimodal-random-1000.csv", nrows=1
                ).columns
            )


def test_import_csv_with_dtype() -> None:
    """
    Test `Dataset.from_csv` method advanced.
    """
    # pylint: disable=too-many-statements
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
        df.loc[indices, "float"] = [np.nan, np.inf, -np.inf]
        df.loc[indices, "float1"] = [np.nan, np.inf, -np.inf]
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
        optional_or_nan_columns = list(df.columns.difference(set(columns)))

        all_columns = df.columns.tolist()
        dtypes: ColumnTypeMapping = {key: str for key in all_columns}
        dtypes.update({key: bool for key in dtypes if key.startswith("bool")})
        dtypes.update({key: int for key in dtypes if key.startswith("int")})
        dtypes.update({key: float for key in dtypes if key.startswith("float")})

        df.loc[indices, optional_or_nan_columns] = ""

        df.to_csv(csv_file, index=False)

        with Dataset(output_h5_file, "w") as dataset:
            dataset.from_csv(csv_file)
            assert set(dataset.keys()) == set(all_columns)
            assert {
                key: dataset.get_column_type(key)
                for key in dataset.keys()
                if key in dtypes
            } == dtypes

        import_columns = np.random.choice(columns, len(columns) // 2)
        with Dataset(output_h5_file, "w") as dataset:
            dataset.from_csv(csv_file, columns=import_columns)
            assert set(dataset.keys()) == set(import_columns)
            assert {key: dataset.get_column_type(key) for key in import_columns} == {
                key: dtypes[key] for key in import_columns
            }

        dtypes.update(
            {
                "string1": Category,
                "datetime1": datetime,
                "array1": np.ndarray,
                "array2": Embedding,
                "array3": Sequence1D,
                "array4": np.ndarray,
                "audio1": Audio,
                "image1": Image,
                "mesh1": Mesh,
                "video1": Video,
            }
        )
        with Dataset(output_h5_file, "w") as dataset:
            dataset.from_csv(csv_file, dtypes)
            assert set(dataset.keys()) == set(df.keys())
            assert {
                key: dataset.get_column_type(key) for key in dataset.keys()
            } == dtypes

        columns += optional_or_nan_columns
        dtypes.update(
            {
                "string2": Category,
                "datetime2": datetime,
                "array5": np.ndarray,
                "array6": Embedding,
                "array7": Sequence1D,
                "array8": np.ndarray,
                "audio3": Audio,
                "image3": Image,
                "mesh3": Mesh,
                "video3": Video,
            }
        )
        with Dataset(output_h5_file, "w") as dataset:
            dataset.from_csv(csv_file, dtypes)
            assert set(dataset.keys()) == set(columns)
            assert {
                key: dataset.get_column_type(key) for key in dataset.keys()
            } == dtypes

        import_columns = np.random.choice(columns, len(columns) // 2)
        with Dataset(output_h5_file, "w") as dataset:
            dataset.from_csv(
                csv_file,
                {key: value for key, value in dtypes.items() if key in import_columns},
                import_columns,
            )
            assert set(dataset.keys()) == set(import_columns)
            assert {key: dataset.get_column_type(key) for key in dataset.keys()} == {
                key: value for key, value in dtypes.items() if key in import_columns
            }

        with tempfile.TemporaryDirectory() as output_folder2:
            csv_file = shutil.move(csv_file, output_folder2)
            with Dataset(output_h5_file, "w") as dataset:
                dataset.from_csv(csv_file, dtypes, workdir=output_folder)
                assert set(dataset.keys()) == set(columns)
                assert {
                    key: dataset.get_column_type(key) for key in dataset.keys()
                } == dtypes
