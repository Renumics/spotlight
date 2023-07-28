"""
Test `renumics.spotlight.io.utils` module.
"""
import os
import tempfile
from glob import glob

import numpy as np
import pytest

from renumics.spotlight.io.audio import read_audio, write_audio


def test_read_audio() -> None:
    """
    Test `read_audio` function.
    """
    audio_folder = "data/audio"
    for filepath in glob(f"{audio_folder}/**", recursive=True):
        if os.path.isfile(filepath):
            y, sampling_rate = read_audio(filepath)
            assert sampling_rate > 0
            assert len(y) > 0


@pytest.mark.parametrize("sampling_rate", [32000, 44100, 48000])
@pytest.mark.parametrize("channels", [1, 2])
@pytest.mark.parametrize("length", [0.5, 1.0, 2.0])
@pytest.mark.parametrize("dtype", ["f4", "i2", "u1"])
@pytest.mark.parametrize("target", ["wav", "flac", "ogg"])
def test_write_audio(
    sampling_rate: int, channels: int, length: float, dtype: str, target: str
) -> None:
    """
    Test `write_audio` function.
    """
    if target == "wav":
        codec = "pcm_s16le"
    elif target == "ogg":
        codec = "libvorbis"
    else:
        codec = target
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
    with tempfile.TemporaryDirectory() as tempdir:
        write_audio(
            os.path.join(tempdir, f"audio.{target}"), data, sampling_rate, target, codec
        )
