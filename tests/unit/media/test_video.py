"""
Test `renumics.spotlight.media.Mesh` class.
"""
import pytest

from renumics.spotlight.media import Video

from .data import VIDEOS_FOLDER


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
def test_video_from_filepath(filename: str) -> None:
    """
    Test reading video from an existing file.
    """
    filepath = VIDEOS_FOLDER / filename
    assert filepath.is_file()
    _ = Video.from_file(str(filepath))
    _ = Video.from_file(filepath)


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
def test_video_from_bytes(filename: str) -> None:
    """
    Test reading video from bytes.
    """
    filepath = VIDEOS_FOLDER / filename
    assert filepath.is_file()
    with filepath.open("rb") as file:
        blob = file.read()
        _ = Video.from_bytes(blob)
