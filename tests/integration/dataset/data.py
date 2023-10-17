from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Union, Dict

import numpy as np

from renumics.spotlight import Embedding, Mesh, Sequence1D, Image, Audio, Video
from renumics.spotlight.dataset.typing import ColumnInputType


@dataclass
class ColumnData:
    """
    Data for a dataset column.
    """

    name: str
    dtype_name: str
    values: Union[Sequence[ColumnInputType], np.ndarray]
    optional: bool = False
    default: ColumnInputType = None
    description: Optional[str] = None
    attrs: Dict = field(default_factory=dict)


def array_data() -> List[ColumnData]:
    """
    Get a list of array column data.
    """
    return [
        ColumnData(
            "array",
            "array",
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
            "array",
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
            "array",
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
            "array3", "array", np.random.rand(6, 2, 2), description="batch array"
        ),
    ]


def embedding_data() -> List[ColumnData]:
    """
    Get a list of embedding column data.
    """
    return [
        ColumnData(
            "embedding",
            "Embedding",
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
            "Embedding",
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
            "embedding2", "Embedding", np.random.rand(6, 2), description="batch array"
        ),
    ]


def image_data() -> List[ColumnData]:
    """
    Get a list of image column data.
    """
    return [
        ColumnData(
            "image",
            "Image",
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
            "Image",
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
            "Image",
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
            "Sequence1D",
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
            "Sequence1D",
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
            "Sequence1D",
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
            "Mesh",
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
            "Audio",
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
            "Audio",
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
            "Category",
            2 * ["red", "blue", "red"],
            description="strings of three categories",
            attrs={"categories": ["red", "green", "blue"]},
        ),
        ColumnData(
            "category1",
            "Category",
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
            "Video",
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
            "Window",
            np.random.uniform(-1, 1, (6, 2)),
        ),
        ColumnData(
            "window1",
            "Window",
            np.random.randint(-1000, 1000, (6, 2)),
        ),
        ColumnData(
            "window2",
            "Window",
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
