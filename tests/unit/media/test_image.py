"""
Test `renumics.spotlight.media.Image` class.
"""
import io
from typing import Optional

import numpy as np
import pytest

from renumics.spotlight.media import Image

from .data import IMAGES_FOLDER, SEED
from ...integration.helpers import approx


@pytest.mark.parametrize("size", [1, 10, 100])
@pytest.mark.parametrize("num_channels", [None, 1, 3, 4])
@pytest.mark.parametrize("dtype", ["float32", "float64", "uint8", "int32"])
@pytest.mark.parametrize("input_type", ["array", "list", "tuple"])
def test_image_from_array(
    size: int, num_channels: Optional[int], dtype: str, input_type: str
) -> None:
    """
    Test image creation.
    """
    np.random.seed(SEED)
    shape = (size, size) if num_channels is None else (size, size, num_channels)
    np_dtype = np.dtype(dtype)
    if np_dtype.str[1] == "f":
        array = np.random.uniform(0, 1, shape).astype(dtype)
        target = (255 * array).round().astype("uint8")
    else:
        array = np.random.randint(0, 256, shape, dtype)  # type: ignore
        target = array.astype("uint8")
    if num_channels == 1:
        target = target.squeeze(axis=2)
    if input_type == "list":
        array = array.tolist()
    elif input_type == "tuple":
        array = tuple(array.tolist())  # type: ignore
    image = Image(array)

    assert approx(target, image, "Image")
    encoded_image = image.encode()
    decoded_image = Image.decode(encoded_image)
    assert approx(image, decoded_image, "Image")


@pytest.mark.parametrize(
    "filename",
    [
        "nature-256p.ico",
        "nature-360p.bmp",
        "nature-360p.gif",
        "nature-360p.jpg",
        "nature-360p.png",
        "nature-360p.tif",
        "nature-360p.webp",
        "nature-720p.jpg",
        "nature-1080p.jpg",
        "sea-360p.gif",
        "sea-360p.apng",
    ],
)
def test_image_from_filepath(filename: str) -> None:
    """
    Test reading image from an existing file.
    """
    filepath = IMAGES_FOLDER / filename
    assert filepath.is_file()
    _ = Image.from_file(str(filepath))
    _ = Image.from_file(filepath)


@pytest.mark.parametrize(
    "filename",
    [
        "nature-256p.ico",
        "nature-360p.bmp",
        "nature-360p.gif",
        "nature-360p.jpg",
        "nature-360p.png",
        "nature-360p.tif",
        "nature-360p.webp",
        "nature-720p.jpg",
        "nature-1080p.jpg",
        "sea-360p.gif",
        "sea-360p.apng",
    ],
)
def test_image_from_file(filename: str) -> None:
    """
    Test reading image from a file descriptor.
    """
    filepath = IMAGES_FOLDER / filename
    assert filepath.is_file()
    with filepath.open("rb") as file:
        _ = Image.from_file(file)


@pytest.mark.parametrize(
    "filename",
    [
        "nature-256p.ico",
        "nature-360p.bmp",
        "nature-360p.gif",
        "nature-360p.jpg",
        "nature-360p.png",
        "nature-360p.tif",
        "nature-360p.webp",
        "nature-720p.jpg",
        "nature-1080p.jpg",
        "sea-360p.gif",
        "sea-360p.apng",
    ],
)
def test_image_from_io(filename: str) -> None:
    """
    Test reading image from an IO object.
    """
    filepath = IMAGES_FOLDER / filename
    assert filepath.is_file()
    with filepath.open("rb") as file:
        blob = file.read()
        buffer = io.BytesIO(blob)
        _ = Image.from_file(buffer)


@pytest.mark.parametrize(
    "filename",
    [
        "nature-256p.ico",
        "nature-360p.bmp",
        "nature-360p.gif",
        "nature-360p.jpg",
        "nature-360p.png",
        "nature-360p.tif",
        "nature-360p.webp",
        "nature-720p.jpg",
        "nature-1080p.jpg",
        "sea-360p.gif",
        "sea-360p.apng",
    ],
)
def test_image_from_bytes(filename: str) -> None:
    """
    Test reading image from bytes.
    """
    filepath = IMAGES_FOLDER / filename
    assert filepath.is_file()
    with filepath.open("rb") as file:
        blob = file.read()
        _ = Image.from_bytes(blob)
