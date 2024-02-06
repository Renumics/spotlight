"""
Test `renumics.spotlight.media.Mesh` class.
"""

from urllib.parse import urljoin

import pytest

from renumics.spotlight.media import Video

from .data import BASE_URL


@pytest.mark.parametrize(
    "filename",
    [
        "sea-360p.avi",
        "sea-360p.mkv",
        "sea-360p.mov",
        "sea-360p.mp4",
        "sea-360p.mpg",
        "sea-360p.ogg",
        "sea-360p.webm",
        "sea-360p.wmv",
        "sea-360p-10s.mp4",
    ],
)
def test_video_from_url(filename: str) -> None:
    """
    Test reading video from an URL.
    """
    url = urljoin(BASE_URL, filename)
    _ = Video.from_file(url)
