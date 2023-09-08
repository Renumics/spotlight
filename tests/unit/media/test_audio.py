"""
Test `renumics.spotlight.media.Audio` class.
"""
import io
from typing import Optional

import numpy as np
import pytest

from renumics.spotlight.media import Audio

from .data import AUDIO_FOLDER


@pytest.mark.parametrize("sampling_rate", [100, 8000, 44100, 48000, 96000])
@pytest.mark.parametrize("channels", [1, 2, 5])
@pytest.mark.parametrize("length", [0.5, 1.0, 2.0])
@pytest.mark.parametrize("dtype", ["f4", "i2", "u1"])
@pytest.mark.parametrize("target", ["wav", "flac"])
def test_lossless_audio(
    sampling_rate: int, channels: int, length: float, dtype: str, target: Optional[str]
) -> None:
    """
    Test audio creation and lossless saving.
    """

    time = np.linspace(0.0, length, round(sampling_rate * length))
    y = 0.4 * np.sin(2.0 * np.pi * 100 * time)
    if dtype.startswith("f"):
        data = y.astype(dtype)
    elif dtype.startswith("i"):
        data = (y * np.iinfo(dtype).max).astype(dtype)
    elif dtype.startswith("u"):
        data = ((y + 1) * np.iinfo(dtype).max / 2).astype(dtype)
    else:
        assert False
    if channels > 1:
        data = np.broadcast_to(data[:, np.newaxis], (len(data), channels))
    audio = Audio(sampling_rate, data)

    encoded_audio = audio.encode(target)
    decoded_audio = Audio.decode(encoded_audio)

    decoded_sr = decoded_audio.sampling_rate
    decoded_data = decoded_audio.data

    assert decoded_sr == sampling_rate
    assert decoded_data.shape == (len(y), channels)


@pytest.mark.parametrize("sampling_rate", [32000, 44100, 48000])
@pytest.mark.parametrize("channels", [1, 2])
@pytest.mark.parametrize("length", [0.5, 1.0, 2.0])
@pytest.mark.parametrize("dtype", ["f4", "i2", "u1"])
def test_lossy_audio(
    sampling_rate: int, channels: int, length: float, dtype: str
) -> None:
    """
    Test audio creation and lossy saving.
    """
    time = np.linspace(0.0, length, round(sampling_rate * length))
    y = 0.4 * np.sin(2.0 * np.pi * 100 * time)
    if dtype.startswith("f"):
        data = y.astype(dtype)
    elif dtype.startswith("i"):
        data = (y * np.iinfo(dtype).max).astype(dtype)
    elif dtype.startswith("u"):
        data = ((y + 1) * np.iinfo(dtype).max / 2).astype(dtype)
    else:
        assert False
    if channels > 1:
        data = np.broadcast_to(data[:, np.newaxis], (len(data), channels))
    audio = Audio(sampling_rate, data)

    encoded_audio = audio.encode("ogg")
    decoded_audio = Audio.decode(encoded_audio)

    decoded_sr = decoded_audio.sampling_rate
    _decoded_data = decoded_audio.data

    assert decoded_sr == sampling_rate


@pytest.mark.parametrize(
    "filename",
    [
        "gs-16b-1c-44100hz.aac",
        "gs-16b-1c-44100hz.ac3",
        "gs-16b-1c-44100hz.aiff",
        "gs-16b-1c-44100hz.flac",
        "gs-16b-1c-44100hz.m4a",
        "gs-16b-1c-44100hz.mp3",
        "gs-16b-1c-44100hz.ogg",
        "gs-16b-1c-44100hz.ogx",
        "gs-16b-1c-44100hz.wav",
        "gs-16b-1c-44100hz.wma",
    ],
)
def test_audio_from_filepath_mono(filename: str) -> None:
    """
    Test `Audio.from_file` method on mono data.
    """
    filepath = AUDIO_FOLDER / "mono" / filename
    assert filepath.is_file()
    _ = Audio.from_file(str(filepath))
    _ = Audio.from_file(filepath)


@pytest.mark.parametrize(
    "filename",
    [
        "gs-16b-2c-44100hz.aac",
        "gs-16b-2c-44100hz.ac3",
        "gs-16b-2c-44100hz.aiff",
        "gs-16b-2c-44100hz.flac",
        "gs-16b-2c-44100hz.m4a",
        "gs-16b-2c-44100hz.mp3",
        "gs-16b-2c-44100hz.mp4",
        "gs-16b-2c-44100hz.ogg",
        "gs-16b-2c-44100hz.ogx",
        "gs-16b-2c-44100hz.wav",
        "gs-16b-2c-44100hz.wma",
    ],
)
def test_audio_from_filepath_stereo(filename: str) -> None:
    """
    Test `Audio.from_file` method on stereo data.
    """
    filepath = AUDIO_FOLDER / "stereo" / filename
    assert filepath.is_file()
    _ = Audio.from_file(str(filepath))
    _ = Audio.from_file(filepath)


@pytest.mark.parametrize(
    "filename",
    [
        "gs-16b-2c-44100hz.aac",
        "gs-16b-2c-44100hz.ac3",
        "gs-16b-2c-44100hz.aiff",
        "gs-16b-2c-44100hz.flac",
        "gs-16b-2c-44100hz.m4a",
        "gs-16b-2c-44100hz.mp3",
        "gs-16b-2c-44100hz.mp4",
        "gs-16b-2c-44100hz.ogg",
        "gs-16b-2c-44100hz.ogx",
        "gs-16b-2c-44100hz.wav",
        "gs-16b-2c-44100hz.wma",
    ],
)
def test_audio_from_file(filename: str) -> None:
    """
    Test reading audio from a file descriptor.
    """
    filepath = AUDIO_FOLDER / "stereo" / filename
    assert filepath.is_file()
    with filepath.open("rb") as file:
        _ = Audio.from_file(file)


@pytest.mark.parametrize(
    "filename",
    [
        "gs-16b-2c-44100hz.aac",
        "gs-16b-2c-44100hz.ac3",
        "gs-16b-2c-44100hz.aiff",
        "gs-16b-2c-44100hz.flac",
        "gs-16b-2c-44100hz.m4a",
        "gs-16b-2c-44100hz.mp3",
        "gs-16b-2c-44100hz.mp4",
        "gs-16b-2c-44100hz.ogg",
        "gs-16b-2c-44100hz.ogx",
        "gs-16b-2c-44100hz.wav",
        "gs-16b-2c-44100hz.wma",
    ],
)
def test_audio_from_io(filename: str) -> None:
    """
    Test reading audio from an IO object.
    """
    filepath = AUDIO_FOLDER / "stereo" / filename
    assert filepath.is_file()
    with filepath.open("rb") as file:
        blob = file.read()
        buffer = io.BytesIO(blob)
        _ = Audio.from_file(buffer)


@pytest.mark.parametrize(
    "filename",
    [
        "gs-16b-2c-44100hz.aac",
        "gs-16b-2c-44100hz.ac3",
        "gs-16b-2c-44100hz.aiff",
        "gs-16b-2c-44100hz.flac",
        "gs-16b-2c-44100hz.m4a",
        "gs-16b-2c-44100hz.mp3",
        "gs-16b-2c-44100hz.mp4",
        "gs-16b-2c-44100hz.ogg",
        "gs-16b-2c-44100hz.ogx",
        "gs-16b-2c-44100hz.wav",
        "gs-16b-2c-44100hz.wma",
    ],
)
def test_audio_from_bytes(filename: str) -> None:
    """
    Test reading audio from bytes.
    """
    filepath = AUDIO_FOLDER / "stereo" / filename
    assert filepath.is_file()
    with filepath.open("rb") as file:
        blob = file.read()
        _ = Audio.from_bytes(blob)
