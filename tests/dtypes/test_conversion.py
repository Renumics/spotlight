"""
Tests for conversions from source to internal types
"""

from typing import Any, Dict, Type, Union
from pathlib import Path
import io
import datetime
import pytest
import numpy as np
import PIL.Image
from renumics.spotlight import dtypes
from renumics.spotlight.dtypes.conversion import convert_to_dtype, DTypeOptions

from renumics.spotlight.dtypes.typing import ColumnType


@pytest.mark.parametrize(
    "value, target_value",
    [
        (-1, -1),
        (0, 0),
        (42, 42),
        (12345678, 12345678),
        (1.0, 1),
        (42.0, 42),
        ("42", 42),
        (True, 1),
        (False, 0),
    ],
)
def test_conversion_to_int(value: Any, target_value: int) -> None:
    """
    Convert values to int
    """
    assert convert_to_dtype(value, int) == target_value


@pytest.mark.parametrize(
    "value, target_value",
    [
        (-1.0, -1.0),
        (0.0, 0.0),
        (42.0, 42.0),
        (1.2345678, 1.2345678),
        (1, 1.0),
        (42, 42.0),
        ("42", 42.0),
        ("1.234", 1.234),
        (True, 1),
        (False, 0),
        (np.array(42.0), 42.0),
        (np.array(42), 42.0),
        (np.array(np.inf), float("inf")),
    ],
)
def test_conversion_to_float(value: Any, target_value: int) -> None:
    """
    Convert values to float
    """
    assert convert_to_dtype(value, float) == target_value


@pytest.mark.parametrize(
    "value, target_value",
    [
        (True, True),
        (False, False),
        ("", False),
        ("anything", True),
        (1, True),
        (0, False),
        (1.0, True),
        (np.array(True), True),
        (np.array(False), False),
    ],
)
def test_conversion_to_bool(value: Any, target_value: int) -> None:
    """
    Convert values to bool
    """
    assert convert_to_dtype(value, bool) == target_value


@pytest.mark.parametrize(
    "value, target_value",
    [
        (datetime.datetime.max, datetime.datetime.max),
        (
            "2023-07-21T14:43:56.880476",
            datetime.datetime.fromisoformat("2023-07-21T14:43:56.880476"),
        ),
        (
            np.datetime64("2023-07-21T14:43:56"),
            datetime.datetime.fromisoformat("2023-07-21T14:43:56"),
        ),
    ],
)
def test_conversion_to_datetime(value: Any, target_value: datetime.datetime) -> None:
    """
    Convert values to datetime
    """
    assert convert_to_dtype(value, datetime.datetime) == target_value


@pytest.mark.parametrize(
    "value, target_value, categories",
    [
        ("foo", 1, {"foo": 1}),
        ("bar", 2, {"foo": 1, "bar": 2}),
        ("", 0, {"": 0}),
        (1, 1, {"foo": 1}),
        (2, 2, {"foo": 1, "bar": 2}),
        (0, 0, {"": 0}),
    ],
)
def test_conversion_to_category(
    value: Any, target_value: int, categories: Dict[str, int]
) -> None:
    """
    Convert values to category
    """
    assert (
        convert_to_dtype(value, dtypes.Category, DTypeOptions(categories=categories))
        == target_value
    )


@pytest.mark.parametrize(
    "value, target_value",
    [
        (np.array([1, 2, 3]), np.array([1, 2, 3])),
        (np.array([[1, 2, 3], [4, 5, 6]]), np.array([[1, 2, 3], [4, 5, 6]])),
        ([1, 2, 3], np.array([1, 2, 3])),
        ([[1, 2, 3], [4, 5, 6]], np.array([[1, 2, 3], [4, 5, 6]])),
    ],
)
def test_conversion_to_array(value: Any, target_value: np.ndarray) -> None:
    """
    Convert values to array
    """
    assert np.array_equal(convert_to_dtype(value, np.ndarray), target_value)


@pytest.mark.parametrize(
    "value, target_value",
    [
        (None, np.array([np.nan, np.nan])),
        (np.array([1, 2]), np.array([1, 2])),
        ([1, 2], np.array([1, 2])),
    ],
)
def test_conversion_to_window(value: Any, target_value: np.ndarray) -> None:
    """
    Convert values to window
    """
    assert np.array_equal(
        convert_to_dtype(value, dtypes.Window), target_value, equal_nan=True
    )


@pytest.mark.parametrize(
    "value, target_value",
    [
        (None, None),
        (np.array([1, 2, 3, 4]), np.array([1, 2, 3, 4])),
        ([1, 2, 3, 4], np.array([1, 2, 3, 4])),
    ],
)
def test_conversion_to_embedding(value: Any, target_value: np.ndarray) -> None:
    """
    Convert values to embedding
    """
    assert np.array_equal(convert_to_dtype(value, dtypes.Embedding), target_value)


@pytest.mark.parametrize(
    "value, target_value",
    [
        (None, None),
        (np.array([1, 2, 3, 4]), np.array([[0, 1], [1, 2], [2, 3], [3, 4]])),
        (
            np.array([[1, 2, 3, 4], [1, 2, 3, 4]]),
            np.array([[1, 1], [2, 2], [3, 3], [4, 4]]),
        ),
        (np.array([[1, 2], [2, 3], [2, 4]]), np.array([[1, 2], [2, 3], [2, 4]])),
        ([1, 2, 3, 4], np.array([[0, 1], [1, 2], [2, 3], [3, 4]])),
    ],
)
def test_conversion_to_sequence(value: Any, target_value: np.ndarray) -> None:
    """
    Convert values to sequence
    """
    assert np.array_equal(convert_to_dtype(value, dtypes.Sequence1D), target_value)


@pytest.mark.parametrize(
    "value",
    [
        "./data/images/nature-360p.jpg",
        Path("./data/images/nature-360p.jpg").read_bytes(),
        np.array(PIL.Image.new(mode="RGBA", size=(1, 1))),
    ],
)
def test_conversion_to_image(value: Union[str, bytes]) -> None:
    """
    Convert values to image
    """
    image_bytes = convert_to_dtype(value, dtypes.Image)
    image = PIL.Image.open(io.BytesIO(image_bytes))
    assert image.width > 0


@pytest.mark.parametrize(
    "value",
    [
        "./data/audio/1.wav",
        Path("./data/audio/1.wav").read_bytes(),
    ],
)
def test_conversion_to_audio(value: Union[str, bytes]) -> None:
    """
    Convert values to audio
    """
    audio_bytes = convert_to_dtype(value, dtypes.Audio)
    assert len(audio_bytes) > 0


@pytest.mark.parametrize(
    "value",
    [
        "./data/videos/sea-360p.ogg",
    ],
)
def test_conversion_to_video(value: Union[str, bytes]) -> None:
    """
    Convert values to video
    """
    video_bytes = convert_to_dtype(value, dtypes.Video)
    assert len(video_bytes) > 0


@pytest.mark.parametrize(
    "value",
    [
        "./data/meshes/tree.glb",
    ],
)
def test_conversion_to_mesh(value: Union[str, bytes]) -> None:
    """
    Convert values to mesh
    """
    mesh_bytes = convert_to_dtype(value, dtypes.Mesh)
    assert len(mesh_bytes) > 0


@pytest.mark.parametrize(
    "dtype,value,target_value",
    [
        (bool, True, True),
        (int, 42, 42),
        (float, 1.0, 1.0),
        (str, "foobar", "foobar"),
        (str, "foobar" * 20, ("foobar" * 20)[:97] + "..."),
        (datetime.datetime, datetime.datetime.min, datetime.datetime.min),
        (np.ndarray, np.array([1, 2, 3]), "[...]"),
        (np.ndarray, [], "[...]"),
        (np.ndarray, None, None),
        (dtypes.Embedding, np.array([1, 2, 3]), "[...]"),
        (dtypes.Sequence1D, np.array([1, 2, 3]), "[...]"),
        (dtypes.Image, np.array([[0.5, 0.7], [0.5, 0.7]]), "[...]"),
        (
            dtypes.Image,
            "./data/images/nature-360p.jpg",
            "./data/images/nature-360p.jpg",
        ),
        (dtypes.Audio, "./data/audio/1.wav", "./data/audio/1.wav"),
        (dtypes.Video, "./data/videos/sea-360p.ogg", "./data/videos/sea-360p.ogg"),
        (dtypes.Mesh, "./data/meshes/tree.glb", "./data/meshes/tree.glb"),
        (dtypes.Image, Path("./data/images/nature-360p.jpg").read_bytes(), "<bytes>"),
        (dtypes.Audio, Path("./data/audio/1.wav").read_bytes(), "<bytes>"),
        (dtypes.Video, Path("./data/videos/sea-360p.ogg").read_bytes(), "<bytes>"),
    ],
)
def test_simple_conversion(dtype: Type[ColumnType], value: Any, target_value: Any):
    """
    Convert values for simple view.
    """
    simple_converted_value = convert_to_dtype(value, dtype, simple=True)
    assert simple_converted_value == target_value
