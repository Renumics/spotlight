"""
Helper methods for tests
"""

import os.path
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Sequence, Type, Union, Dict

import numpy as np
import pytest
from _pytest.fixtures import SubRequest

from renumics.spotlight import (
    Embedding,
    Mesh,
    Sequence1D,
    Image,
    Audio,
    Category,
    Video,
    Dataset,
    Window,
)
from renumics.spotlight.dataset.typing import ColumnInputType
from renumics.spotlight.dtypes.typing import ColumnType


@dataclass
class ColumnData:
    """
    Data for a dataset column.
    """

    name: str
    column_type: Type[ColumnInputType]
    values: Union[Sequence[ColumnInputType], np.ndarray]
    optional: bool = False
    default: ColumnInputType = None
    description: Optional[str] = None
    attrs: Dict = field(default_factory=dict)


def get_append_column_fn_name(column_type: Type[ColumnType]) -> str:
    """
    Get name of the `append_column` dataset method for the given column type.
    """

    if column_type is bool:
        return "append_bool_column"
    if column_type is int:
        return "append_int_column"
    if column_type is float:
        return "append_float_column"
    if column_type is str:
        return "append_string_column"
    if column_type is datetime:
        return "append_datetime_column"
    if column_type is np.ndarray:
        return "append_array_column"
    if column_type is Embedding:
        return "append_embedding_column"
    if column_type is Image:
        return "append_image_column"
    if column_type is Sequence1D:
        return "append_sequence_1d_column"
    if column_type is Mesh:
        return "append_mesh_column"
    if column_type is Audio:
        return "append_audio_column"
    if column_type is Category:
        return "append_categorical_column"
    if column_type is Video:
        return "append_video_column"
    if column_type is Window:
        return "append_window_column"
    raise TypeError


@pytest.fixture
def optional_data() -> List[ColumnData]:
    """
    Get a list of optional column data.
    """
    return [
        ColumnData("bool", bool, [], default=True),
        ColumnData("bool1", bool, [], default=False),
        ColumnData("bool2", bool, [], default=np.bool_(True)),
        ColumnData("int", int, [], default=-5),
        ColumnData("int1", int, [], default=5),
        ColumnData("int2", int, [], default=np.int16(1000)),
        ColumnData("float", float, [], optional=True),
        ColumnData("float1", float, [], default=5.0),
        ColumnData("float2", float, [], default=np.float16(1000.0)),
        ColumnData("string", str, [], optional=True),
        ColumnData("string1", str, [], default="a"),
        ColumnData("string2", str, [], default=np.str_("b")),
        ColumnData("datetime", datetime, [], optional=True),
        ColumnData("datetime1", datetime, [], default=datetime.now().astimezone()),
        ColumnData("datetime2", datetime, [], default=np.datetime64("NaT")),
        ColumnData("array", np.ndarray, [], optional=True),
        ColumnData("array1", np.ndarray, [], default=np.empty(0)),
        ColumnData("embedding", Embedding, [], optional=True),
        ColumnData(
            "embedding1", Embedding, [], default=Embedding(np.array([np.nan, np.nan]))
        ),
        ColumnData("image", Image, [], optional=True),
        ColumnData("image1", Image, [], default=Image.empty()),
        ColumnData("sequence_1d", Sequence1D, [], optional=True),
        ColumnData("sequence_1d1", Sequence1D, [], default=Sequence1D.empty()),
        ColumnData("mesh", Mesh, [], optional=True),
        ColumnData("mesh1", Mesh, [], default=Mesh.empty()),
        ColumnData("audio", Audio, [], optional=True),
        ColumnData("audio1", Audio, [], default=Audio.empty()),
        ColumnData(
            "category1",
            Category,
            [],
            default="red",
            attrs={"categories": ["red", "green"]},
        ),
        ColumnData("window", Window, [], optional=True),
        ColumnData("window1", Window, [], default=[-1, np.nan]),
    ]


@pytest.fixture
def simple_data() -> List[ColumnData]:
    """
    Get a list of scalar column data.
    """
    return [
        ColumnData("bool", bool, [True, False, True, True, False, True]),
        ColumnData(
            "bool1",
            bool,
            np.array([True, False, True, True, False, True]),
            description="np.bool_ column",
        ),
        ColumnData("int", int, [-1000, -1, 0, 4, 5, 6]),
        ColumnData(
            "int1",
            int,
            np.array([-1000, -1, 0, 4, 5, 6]),
            description="numpy.int64 column",
        ),
        ColumnData(
            "int2",
            int,
            np.array([-1000, -1, 0, 4, 5, 6], np.int16),
            description="np.int16 column",
        ),
        ColumnData(
            "int3",
            int,
            np.array([1, 10, 0, 4, 5, 6], np.int16),
            description="np.uint16 column",
        ),
        ColumnData(
            "float",
            float,
            [-float("inf"), -0.1, float("nan"), float("inf"), 0.1, 1000.0],
        ),
        ColumnData(
            "float1",
            float,
            np.array([-float("inf"), -0.1, float("nan"), float("inf"), 0.1, 1000.0]),
            description="np.float64 column",
        ),
        ColumnData(
            "float2",
            float,
            np.array(
                [-float("inf"), -0.1, float("nan"), float("inf"), 0.1, 1000.0],
                np.float16,
            ),
            description="np.float16 column",
        ),
        ColumnData("string", str, ["", "a", "bc", "def", "ghijш", "klmnoü"]),
        ColumnData(
            "string1",
            str,
            np.array(["", "a", "bc", "def", "ghij", "klmno"]),
            description="",
        ),
        ColumnData(
            "datetime",
            datetime,
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
            datetime,
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


def array_data() -> List[ColumnData]:
    """
    Get a list of array column data.
    """
    return [
        ColumnData(
            "array",
            np.ndarray,
            [
                np.array([1, 2]),
                np.array([3, 4]),
                np.array([5, 6]),
                np.array([7, 8]),
                np.array([9, 10]),
                np.array([11, 12]),
            ],
            description="list of np.ndarray of fixed shape",
        ),
        ColumnData(
            "array1",
            np.ndarray,
            [
                np.zeros(0, np.int64),
                np.array([1], np.int64),
                np.array([2, 3], np.int64),
                np.array([4, 5, 6], np.int64),
                np.array([7, 8, 9, 10], np.int64),
                np.array([11, 12, 13, 14, 15], np.int64),
            ],
            description="list of np.ndarray of variable shape",
        ),
        ColumnData(
            "array2",
            np.ndarray,
            [
                1.0,
                [],
                [[[[]]]],
                [[1.0, 2, 3], [4, 5, 6]],
                (7.0, 8, 9, 10),
                np.array([11.0, 12, 13, 14, 15]),
            ],
            description="mixed types",
        ),
        ColumnData(
            "array3", np.ndarray, np.random.rand(6, 2, 2), description="batch array"
        ),
    ]


def embedding_data() -> List[ColumnData]:
    """
    Get a list of embedding column data.
    """
    return [
        ColumnData(
            "embedding",
            Embedding,
            [
                Embedding(np.array([1.0, 2.0])),
                Embedding(np.array([3.0, 4.0])),
                Embedding(np.array([5.0, 6.0])),
                Embedding(np.array([7.0, np.nan])),
                Embedding(np.array([np.nan, 8.0])),
                Embedding(np.array([np.nan, np.nan])),
            ],
        ),
        ColumnData(
            "embedding1",
            Embedding,
            [
                [1.0, 2.0],
                (3.0, 4.0),
                np.array([5.0, 6.0]),
                [7.0, float("nan")],
                (float("nan"), 8.0),
                np.array([np.nan, np.nan]),
            ],
            description="mixed types",
        ),
        ColumnData(
            "embedding2", Embedding, np.random.rand(6, 2), description="batch array"
        ),
    ]


def image_data() -> List[ColumnData]:
    """
    Get a list of image column data.
    """
    return [
        ColumnData(
            "image",
            Image,
            [
                Image.empty(),
                Image.empty(),
                Image(np.zeros((10, 10), dtype=np.uint8)),
                Image(np.zeros((10, 20, 1), dtype=np.int64)),
                Image(np.zeros((20, 10, 3), dtype=np.float64)),
                Image(np.zeros((20, 20, 4), dtype=np.uint8)),
            ],
        ),
        ColumnData(
            "image1",
            Image,
            [
                [[0]],
                [[[1.0]]],
                [[[127, 127, 127]]],
                np.zeros((10, 10), dtype=np.uint8),
                np.zeros((20, 10), dtype=np.int64),
                np.zeros((20, 10, 3), dtype=np.float64),
            ],
            description="mixed types",
        ),
        ColumnData(
            "image2",
            Image,
            np.random.randint(0, 256, (6, 10, 20, 3), "uint8"),
            description="batch array",
        ),
    ]


def sequence_1d_data() -> List[ColumnData]:
    """
    Get a list of 1d-sequence column data.
    """
    return [
        ColumnData(
            "sequence_1d",
            Sequence1D,
            [
                Sequence1D(np.array([0.0, 1.0]), np.array([1.0, 2.0])),
                Sequence1D(np.array([0.0, 1.0]), np.array([3.0, 4.0])),
                Sequence1D(np.array([0.0, 1.0]), np.array([5.0, 6.0])),
                Sequence1D(np.array([0.0, 1.0]), np.array([7.0, 8.0])),
                Sequence1D(np.array([np.inf, 1.0]), np.array([-np.inf, 1.0])),
                Sequence1D(np.array([np.nan, np.nan]), np.array([np.nan, np.nan])),
            ],
            description="fixed shape",
        ),
        ColumnData(
            "sequence_1d1",
            Sequence1D,
            [
                Sequence1D.empty(),
                Sequence1D(np.array([0.0]), np.array([1.0])),
                Sequence1D(np.array([0.0, 1.0, 2.0]), np.array([2.0, 3.0, 4.0])),
                Sequence1D(
                    np.array([0.0, 1.0, 2.0, 3.0]), np.array([5.0, 6.0, 7.0, 8.0])
                ),
                Sequence1D(np.array([np.inf, 1.0]), np.array([-np.inf, 1.0])),
                Sequence1D(np.array([np.nan, np.nan]), np.array([np.nan, np.nan])),
            ],
            description="variable shape",
        ),
        ColumnData(
            "sequence_1d2",
            Sequence1D,
            [
                [],
                [1.0],
                (float("nan"), float("inf"), -float("inf")),
                np.array([5.0, 6.0, 7.0, 8.0]),
                np.array([-np.inf, 1.0]),
                np.array([np.nan, np.nan]),
            ],
            description="variable shape, mixed types",
        ),
    ]


def mesh_data() -> List[ColumnData]:
    """
    Get a list of mesh column data.
    """
    return [
        ColumnData(
            "mesh",
            Mesh,
            [
                Mesh.empty(),
                Mesh.empty(),
                Mesh(
                    np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0]]),
                    np.array([[0, 1, 2]]),
                ),
                Mesh(
                    np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0]]),
                    np.array([[0, 1, 2]]),
                ),
                Mesh(
                    np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0]]),
                    np.array([[0, 1, 2]]),
                ),
                Mesh(
                    np.array(
                        [
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 1.0],
                            [0.0, 1.0, 0.0],
                            [1.0, 0.0, 0.0],
                        ]
                    ),
                    np.array([[0, 1, 2], [0, 1, 3], [1, 2, 3]]),
                ),
            ],
            description="",
        ),
    ]


def audio_data() -> List[ColumnData]:
    """
    Get a list of audio column data.
    """

    samplerate = 44100
    time = np.linspace(0.0, 1.0, samplerate)
    amplitude = np.iinfo(np.int16).max * 0.4
    data = np.array(amplitude * np.sin(2.0 * np.pi * 1000 * time), dtype=np.int16)
    audio_data_left, audio_data_right = data, data
    return [
        ColumnData(
            "audio",
            Audio,
            6
            * [
                Audio(
                    samplerate,
                    np.array([audio_data_left, audio_data_right]).transpose(),
                ),
            ],
            description="List of 3 stereo Audio Signals",
        ),
        ColumnData(
            "audio1",
            Audio,
            6
            * [
                Audio(
                    samplerate,
                    np.array([audio_data_right, audio_data_right]).transpose(),
                ),
            ],
            description="List of 2 stereo Audio Signals",
        ),
    ]


def categorical_data() -> List[ColumnData]:
    """
    Get a list of categorical column data.
    """
    return [
        ColumnData(
            "category",
            Category,
            2 * ["red", "blue", "red"],
            description="strings of three categories",
            attrs={"categories": ["red", "green", "blue"]},
        ),
        ColumnData(
            "category1",
            Category,
            2 * ["red", "blue", "red"],
            description="strings of three categories",
            attrs={"categories": ["red", "green", "blue"]},
        ),
    ]


def video_data() -> List[ColumnData]:
    """
    Get a list of video column data.
    """
    return [
        ColumnData(
            "video",
            Video,
            [
                Video.empty(),
                Video.empty(),
                Video.from_file("data/videos/sea-360p.avi"),
                Video.from_file("data/videos/sea-360p.mp4"),
                Video.from_file("data/videos/sea-360p.wmv"),
                Video.empty(),
            ],
            description="",
        ),
    ]


def window_data() -> List[ColumnData]:
    """
    Get a list of window column data.
    """
    return [
        ColumnData(
            "window",
            Window,
            np.random.uniform(-1, 1, (6, 2)),
        ),
        ColumnData(
            "window1",
            Window,
            np.random.randint(-1000, 1000, (6, 2)),
        ),
        ColumnData(
            "window2",
            Window,
            [
                (1, 2),
                (1.0, np.nan),
                [np.nan, np.inf],
                [1.0, -1.0],
                np.array([1, 2]),
                np.array([np.nan, -np.inf]),
            ],
        ),
    ]


@pytest.fixture
def empty_dataset() -> Dataset:
    """
    An empty dataset.
    """
    with tempfile.TemporaryDirectory() as output_folder:
        output_h5_file = os.path.join(output_folder, "dataset.h5")
        with Dataset(output_h5_file, "w") as dataset:
            yield dataset


@pytest.fixture
def categorical_color_dataset(request: SubRequest) -> Dataset:
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
def fancy_indexing_dataset() -> Dataset:
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
def descriptors_dataset_for_compress_dataset() -> Dataset:
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
def descriptors_dataset() -> Dataset:
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


def approx(
    expected: Optional[ColumnType], actual: ColumnInputType, type_: Type[ColumnType]
) -> bool:
    """
    Check whether expected and actual dataset values are almost equal.
    """

    if expected is None and actual is None:
        return True
    if issubclass(type_, (bool, int, float, str)):
        # Cast and compare scalars.
        expected = np.array(expected, dtype=type_)
        actual = np.array(actual, dtype=type_)
        return approx(expected, actual, np.ndarray)
    if issubclass(type_, datetime):
        # Cast and compare datetimes.
        expected = np.array(expected, dtype="datetime64")
        actual = np.array(actual, dtype="datetime64")
        return approx(expected, actual, np.ndarray)
    if issubclass(type_, Window):
        return approx(
            np.array(expected, dtype=float), np.array(actual), type_=np.ndarray
        )
    if issubclass(type_, np.ndarray):
        # Cast and compare arrays.
        expected = np.asarray(expected)
        actual = np.asarray(actual)
        if actual.shape != expected.shape:
            return False
        if issubclass(expected.dtype.type, np.inexact):
            return np.allclose(actual, expected, equal_nan=True)
        return actual.tolist() == expected.tolist()
    if issubclass(type_, (Embedding, Image, Mesh, Sequence1D, Audio, Video)):
        # Cast and compare custom types.
        if not isinstance(expected, type_):
            expected = type_(expected)
        if not isinstance(actual, type_):
            actual = type_(actual)
        if issubclass(type_, (Embedding, Image, Video)):
            return approx(actual.data, expected.data, np.ndarray)
        if issubclass(type_, Audio):
            return (
                approx(actual.data, expected.data, np.ndarray)
                and actual.sampling_rate == expected.sampling_rate
            )
        if issubclass(type_, Mesh):
            return (
                approx(actual.points, expected.points, np.ndarray)
                and approx(actual.triangles, expected.triangles, np.ndarray)
                and len(actual.point_displacements) == len(expected.point_displacements)
                and all(
                    approx(actual_displacement, expected_displacement, np.ndarray)
                    for actual_displacement, expected_displacement in zip(
                        actual.point_displacements, expected.point_displacements
                    )
                )
                and actual.point_attributes.keys() == expected.point_attributes.keys()
                and all(
                    approx(
                        actual.point_attributes[attribute_name],
                        point_attribute,
                        np.ndarray,
                    )
                    for attribute_name, point_attribute in expected.point_attributes.items()
                )
            )
        if issubclass(type_, Sequence1D):
            return approx(actual.index, expected.index, np.ndarray) and approx(
                actual.value, expected.value, np.ndarray
            )
    raise TypeError(f"Invalid `type_` received: value {type_} of type {type(type_)}.")
