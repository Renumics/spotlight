"""
Helper methods for tests
"""

import os.path
import tempfile
from datetime import datetime
from typing import Iterator, List

import numpy as np
import pytest
from _pytest.fixtures import SubRequest

from renumics.spotlight import Embedding, Mesh, Sequence1D, Image, Audio, Dataset

from .data import (
    ColumnData,
    categorical_data,
    array_data,
    window_data,
    embedding_data,
    sequence_1d_data,
    audio_data,
    image_data,
    mesh_data,
    video_data,
)


@pytest.fixture
def optional_data() -> List[ColumnData]:
    """
    Get a list of optional column data.
    """
    return [
        ColumnData("bool", "bool", [], default=True),
        ColumnData("bool1", "bool", [], default=False),
        ColumnData("bool2", "bool", [], default=np.bool_(True)),
        ColumnData("int", "int", [], default=-5),
        ColumnData("int1", "int", [], default=5),
        ColumnData("int2", "int", [], default=np.int16(1000)),
        ColumnData("float", "float", [], optional=True),
        ColumnData("float1", "float", [], default=5.0),
        ColumnData("float2", "float", [], default=np.float16(1000.0)),
        ColumnData("string", "str", [], optional=True),
        ColumnData("string1", "str", [], default="a"),
        ColumnData("string2", "str", [], default=np.str_("b")),
        ColumnData("datetime", "datetime", [], optional=True),
        ColumnData("datetime1", "datetime", [], default=datetime.now().astimezone()),
        ColumnData("datetime2", "datetime", [], default=np.datetime64("NaT")),
        ColumnData("array", "array", [], optional=True),
        ColumnData("array1", "array", [], default=np.empty(0)),
        ColumnData("embedding", "Embedding", [], optional=True),
        ColumnData(
            "embedding1", "Embedding", [], default=Embedding(np.array([np.nan, np.nan]))
        ),
        ColumnData("image", "Image", [], optional=True),
        ColumnData("image1", "Image", [], default=Image.empty()),
        ColumnData("sequence_1d", "Sequence1D", [], optional=True),
        ColumnData("sequence_1d1", "Sequence1D", [], default=Sequence1D.empty()),
        ColumnData("mesh", "Mesh", [], optional=True),
        ColumnData("mesh1", "Mesh", [], default=Mesh.empty()),
        ColumnData("audio", "Audio", [], optional=True),
        ColumnData("audio1", "Audio", [], default=Audio.empty()),
        ColumnData(
            "category1",
            "Category",
            [],
            default="red",
            attrs={"categories": ["red", "green"]},
        ),
        ColumnData("window", "Window", [], optional=True),
        ColumnData("window1", "Window", [], default=[-1, np.nan]),
    ]


@pytest.fixture
def simple_data() -> List[ColumnData]:
    """
    Get a list of scalar column data.
    """
    return [
        ColumnData("bool", "bool", [True, False, True, True, False, True]),
        ColumnData(
            "bool1",
            "bool",
            np.array([True, False, True, True, False, True]),
            description="np.bool_ column",
        ),
        ColumnData("int", "int", [-1000, -1, 0, 4, 5, 6]),
        ColumnData(
            "int1",
            "int",
            np.array([-1000, -1, 0, 4, 5, 6]),
            description="numpy.int64 column",
        ),
        ColumnData(
            "int2",
            "int",
            np.array([-1000, -1, 0, 4, 5, 6], np.int16),
            description="np.int16 column",
        ),
        ColumnData(
            "int3",
            "int",
            np.array([1, 10, 0, 4, 5, 6], np.int16),
            description="np.uint16 column",
        ),
        ColumnData(
            "float",
            "float",
            [-float("inf"), -0.1, float("nan"), float("inf"), 0.1, 1000.0],
        ),
        ColumnData(
            "float1",
            "float",
            np.array([-float("inf"), -0.1, float("nan"), float("inf"), 0.1, 1000.0]),
            description="np.float64 column",
        ),
        ColumnData(
            "float2",
            "float",
            np.array(
                [-float("inf"), -0.1, float("nan"), float("inf"), 0.1, 1000.0],
                np.float16,
            ),
            description="np.float16 column",
        ),
        ColumnData("string", "str", ["", "a", "bc", "def", "ghijш", "klmnoü"]),
        ColumnData(
            "string1",
            "str",
            np.array(["", "a", "bc", "def", "ghij", "klmno"]),
            description="",
        ),
        ColumnData(
            "datetime",
            "datetime",
            [
                datetime.now(),
                datetime.now().astimezone(),
                datetime.now().astimezone(),
                datetime.utcnow(),
                datetime.utcnow().astimezone(),
                datetime.utcnow().astimezone(),
            ],
        ),
        ColumnData(
            "datetime1",
            "datetime",
            np.arange("2002-10-27T04:30", 6 * 60, 60, np.datetime64),
            description="np.datetime64 column",
        ),
    ]


@pytest.fixture
def complex_data() -> List[ColumnData]:
    """
    Get a list of custom column data.
    """
    return (
        array_data()
        + embedding_data()
        + image_data()
        + sequence_1d_data()
        + mesh_data()
        + audio_data()
        + categorical_data()
        + video_data()
        + window_data()
    )


@pytest.fixture
def empty_dataset() -> Iterator[Dataset]:
    """
    An empty dataset.
    """
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            yield dataset


@pytest.fixture
def categorical_color_dataset(request: SubRequest) -> Iterator[Dataset]:
    """a dataset with category column"""
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            dataset.append_categorical_column(
                "my_new_cat",
                default=request.param,
                categories=["red", "green", "blue"],
            )
            for data in 2 * ["green", "red", "blue"]:
                dataset.append_row(my_new_cat=data)
            yield dataset


@pytest.fixture
def fancy_indexing_dataset() -> Iterator[Dataset]:
    """a dataset with a single range column"""
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            dataset.append_int_column(
                "int",
                range(1000),
            )
            yield dataset


@pytest.fixture
def descriptors_dataset_for_compress_dataset() -> Iterator[Dataset]:
    """
    dataset without faulty/ problematic columns
    """
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as data:
            normal_embedding = [Embedding([3]), Embedding([2]), Embedding([1])]

            data.append_embedding_column("embedding", values=normal_embedding)

            sequence_1 = Sequence1D([1.0, 2.0], dtype=np.float32)
            sequence_2 = Sequence1D([1.0, 3.0], dtype=np.float32)

            data.append_sequence_1d_column(
                "sequence_1d", values=[sequence_1, sequence_2, sequence_1]
            )

            image_1 = Image(np.full([2, 100, 3], 255, dtype=np.float16))

            data.append_image_column("image", [image_1, image_1, image_1])

            audio_1 = Audio(100, np.full([1, 2], 255, dtype=np.float32))

            data.append_audio_column("audio", [audio_1, audio_1, audio_1])

            yield data


@pytest.fixture
def descriptors_dataset() -> Iterator[Dataset]:
    """
    builds descriptor testing dataset
    """

    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as data:
            normal_embedding = np.random.random((3, 20))
            none_embedding = [None, [1, 2, 3], [3, 4, 5]]
            # nan_embedding = [Embedding([3]), Embedding([2]), Embedding([np.nan])]

            data.append_embedding_column("embedding", values=normal_embedding)
            data.append_embedding_column(
                "embedding_none", values=none_embedding, optional=True
            )
            # data.append_embedding_column("embedding_nan", values=nan_embedding, optional=True)
            # no nan allowed in embedding object

            sequence_1 = Sequence1D([1.0, 2.0, 10, 20], dtype=np.float32)
            sequence_1_extended = Sequence1D([1.0, 2.0, 3.0, 10, 20], dtype=np.float32)
            sequence_2 = Sequence1D([1.0, 3.0, 10, 30], dtype=np.float32)
            sequence_2_extended = Sequence1D([1.0, 3.0, 4.0, 20, 40], dtype=np.float32)
            sequence_nan = Sequence1D(np.array([np.nan, 3.0], dtype=np.float32))
            # sequence_nan_extended = Sequence1D(
            #     np.array([np.nan, 3.0, 2.0], dtype=np.float32)
            # )
            # Sequences with different dtypes not allowed in same column
            # sequence_dtype= Sequence1D(np.array([1.0, 0.0], dtype=np.float64))
            # None not allowed
            # sequence_none = Sequence1D([None, 3])

            data.append_sequence_1d_column(
                "sequence_1d", values=[sequence_1, sequence_2, sequence_1]
            )
            data.append_sequence_1d_column(
                "sequence_1d_extended",
                values=[sequence_1_extended, sequence_2_extended, sequence_1_extended],
            )
            data.append_sequence_1d_column(
                "sequence_1d_nan", values=[sequence_nan, sequence_2, sequence_1]
            )
            data.append_sequence_1d_column(
                "sequence_1d_nan_extended",
                values=[sequence_nan, sequence_2_extended, sequence_1_extended],
            )

            image_data_local = np.full([100, 100, 3], 255, dtype=np.float16)
            image_data_2 = np.full([100, 100, 3], 255, dtype=np.float32)

            image_1 = Image(np.full([2, 100, 3], 255, dtype=np.float16))
            image_2 = Image(np.full([100, 200, 3], 255, dtype=np.float16))
            image_3 = Image(image_data_2)
            # None cannot be set in numpy array -> automatically NaN
            image_data_local[0][1] = np.nan
            image_4 = Image(image_data_local)
            image_5 = Image(np.full([2, 200, 1], 255, dtype=np.float16))
            image_6 = Image(np.full([2, 200, 4], 255, dtype=np.float16))

            data.append_image_column("image", [image_1, image_1, image_1])
            data.append_image_column("image_shapes", [image_1, image_2, image_1])
            # None cannot be appended to column as object
            # data.append_image_column("image_None", [None, image_1, image_1])
            data.append_image_column("image_dtypes", [image_1, image_3, image_1])
            data.append_image_column("image_nan", [image_4, image_1, image_1])
            data.append_image_column("image_rgba_gray", [image_5, image_6, image_5])
            data.append_image_column("image_rgba_rgb", [image_6, image_2, image_6])
            data.append_image_column("image_gray_rgb", [image_5, image_2, image_5])

            data_array = np.array([100], dtype=np.float32)
            audio_1 = Audio(100, np.full([10, 2], 255, dtype=np.float32))
            audio_2 = Audio(100, np.full([10, 2], 255, dtype=np.uint8))
            audio_3 = Audio(100, 5 * [data_array])
            audio_4 = Audio(100, np.full([100, 2], 255, dtype=np.float32))
            data_array = np.full([1, 2], 255, dtype=np.float32)
            data_array[0] = np.nan
            audio_5 = Audio(100, data_array)
            data_array[0] = None
            audio_6 = Audio(100, data_array)

            data.append_audio_column("audio", [audio_1, audio_1, audio_1])
            data.append_audio_column("audio_dtypes", [audio_1, audio_2, audio_1])
            # data.append_audio_column("audio_None", [None, audio_2, audio_1])
            data.append_audio_column("audio_channels", [audio_1, audio_3, audio_1])
            data.append_audio_column("audio_shapes", [audio_1, audio_4, audio_1])
            data.append_audio_column("audio_nan", [audio_1, audio_5, audio_1])
            data.append_audio_column("audio_none", [audio_1, audio_6, audio_1])

            yield data
