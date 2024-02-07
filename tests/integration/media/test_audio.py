"""
Test `renumics.spotlight.media.Audio` class.
"""

from urllib.parse import urljoin

import pytest

from renumics.spotlight.media import Audio

from .data import BASE_URL


@pytest.mark.parametrize(
    "filename",
    [
        "gs-16b-2c-44100hz.aac",
        "gs-16b-2c-44100hz.ac3",
        "gs-16b-2c-44100hz.aiff",
        "gs-16b-2c-44100hz.flac",
        "gs-16b-2c-44100hz.mp3",
        "gs-16b-2c-44100hz.ogg",
        "gs-16b-2c-44100hz.ogx",
        "gs-16b-2c-44100hz.ts",
        "gs-16b-2c-44100hz.wav",
        "gs-16b-2c-44100hz.wma",
    ],
)
def test_audio_from_url(filename: str) -> None:
    """
    Test reading audio from a URL.
    """
    url = urljoin(BASE_URL, filename)
    _ = Audio.from_file(url)
