"""
Test `renumics.spotlight.media.Image` class.
"""

from urllib.parse import urljoin

import pytest

from renumics.spotlight.media import Image

from .data import BASE_URL


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
def test_image_from_url(filename: str) -> None:
    """
    Test reading image from a URL.
    """
    url = urljoin(BASE_URL, filename)
    _ = Image.from_file(url)
