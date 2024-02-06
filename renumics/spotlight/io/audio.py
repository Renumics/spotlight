"""
This module contains helpers for reading and writing of audio.
"""

import io
import os
from typing import IO, Dict, Tuple, Union

import av
import numpy as np
import requests
import validators

from renumics.spotlight.requests import headers
from renumics.spotlight.typing import FileType

# Some AV warning messages have ERROR level and can be confusing.
av.logging.set_level(av.logging.CRITICAL)

_PACKET_AV_DATA_FORMATS: Dict[str, str] = {
    value: key
    for key, value in av.audio.frame.format_dtypes.items()
    if key.endswith("p")
}


def prepare_input_file(
    file: FileType, timeout: Union[int, float] = 30, reusable: bool = False
) -> Union[str, IO]:
    """
    Prepare an input file depending on its type and value:
        - download URL (`str`) and open it for file-like reading;
        - check that a filepath (`str` or `os.PathLike`) exists and convert it to `str`;
        - assume all other types as file-like and return as-is.

    Args:
        file: A filepath, an URL or a file-like object.
        timeout: For URLs only. Download timeout.
        reusable: For URLs only. If `True`, file-like return value is reusable
            (use `file.seek(0)`). If `False` (default), return value can be used
            only once.

    Raises:
        ValueError: if `file` is `str` or `os.PathLike`, but isn't a
            valid/existing URL or an existing file.

    """
    if isinstance(file, os.PathLike):
        file = str(file)
    if not isinstance(file, str):
        # Assume that `file` is file-like.
        return file
    if validators.url(file):
        response = requests.get(file, headers=headers, stream=True, timeout=timeout)
        if response.ok:
            if not reusable:
                return response.raw
            return io.BytesIO(response.content)
        raise ValueError(f"URL {file} not found.")
    if not os.path.isfile(file):
        raise ValueError(f"File {file} is neither an URL nor an existing file.")
    return file


def read_audio(file: FileType) -> Tuple[np.ndarray, int]:
    """
    Read an audio file or file-like object using AV.

    Args:
        file: An audio filepath, file or file-like object. An input audio file.

    Returns:
        y: Array of shape `(num_samples, num_channels)`. PCM audio data, dtype
            left as-is.
        sampling_rate: Sampling rate of the audio data.
    """
    file = prepare_input_file(file)
    with av.open(file, "r") as container:
        stream = container.streams.audio[0]
        num_channels = stream.codec_context.channels
        sampling_rate = stream.codec_context.rate

        data = []
        for frame in container.decode(audio=0):
            frame_array = frame.to_ndarray()
            if len(frame_array) == 1:
                frame_array = frame_array.reshape((-1, num_channels))
            else:
                frame_array = frame_array.T
            data.append(frame_array)

    y = np.concatenate(data, axis=0)
    return y, sampling_rate


def write_audio(
    file: FileType, data: np.ndarray, sampling_rate: int, format_: str, codec: str
) -> None:
    """
    Write audio data to a file or file-like object using AV.

    Args:
        file: A filepath, file or file-like object. An output audio file.
        data: Array of shape `(num_samples, )` or `(num_samples, num_channels)`.
            PCM audio data with any dtype supported by AV.
        sampling_rate: Sampling rate of the audio data.
        format_: An audio format supported by AV.
        codec: An audio codec for the given audio format supported by AV
            (s. `av.codec.codecs_available`).
    """
    if isinstance(file, os.PathLike):
        file = str(file)
    data_format = _PACKET_AV_DATA_FORMATS[data.dtype.str[1:]]
    if data.ndim == 1:
        data = data[np.newaxis, :]
    elif data.ndim == 2:
        data = data.T
    else:
        raise ValueError(
            f"`data` argument is expected to be an array with 1 or 2 dimensions, "
            f"but array with {data.ndim} dimensions received."
        )
    # `AudioFrame.from_ndarray` expects an C-contiguous array as input.
    data = np.ascontiguousarray(data)
    num_channels = len(data)
    frame = av.audio.AudioFrame.from_ndarray(data, data_format, num_channels)
    frame.rate = sampling_rate
    with av.open(file, "w", format_) as container:
        stream = container.add_stream(codec, sampling_rate)
        stream.channels = num_channels
        container.mux(stream.encode(frame))
        container.mux(stream.encode(None))


def transcode_audio(
    input_file: FileType, output_file: FileType, output_format: str, output_codec: str
) -> None:
    """
    Transcode an input audio file to an output audio file using AV.

    Args:
        input_file: A filepath, file or file-like object. An input audio file.
        output_file: A filepath, file or file-like object. An output audio file.
        output_format: An audio format supported by AV.
        output_codec: An audio codec for the given audio format supported by AV
            (s. `av.codec.codecs_available`).
    """
    input_file = prepare_input_file(input_file)
    if isinstance(output_file, os.PathLike):
        output_file = str(output_file)
    with av.open(input_file, "r") as input_container:
        input_stream = input_container.streams.audio[0]
        with av.open(output_file, "w", output_format) as output_container:
            output_stream = output_container.add_stream(output_codec)

            for frame in input_container.decode(input_stream):
                frame.pts = None
                for packet in output_stream.encode(frame):
                    output_container.mux(packet)

            for packet in output_stream.encode(None):
                output_container.mux(packet)


def get_format_codec(file: FileType) -> Tuple[str, str]:
    """
    Get audio format and audio codec of an audio file.
    """
    file = prepare_input_file(file)
    with av.open(file, "r") as input_container:
        stream = input_container.streams.audio[0]
        return input_container.format.name, stream.name


def get_waveform(file: FileType) -> np.ndarray:
    """
    Calculate waveform of an audio file or file-like object.
    """
    y, input_sampling_rate = read_audio(file)
    if y.dtype.str[1] == "i":
        y = y.astype(np.float32) / np.iinfo(y.dtype).max
    elif y.dtype.str[1] == "u":
        y = 2 * y.astype(np.float32) / np.iinfo(y.dtype).max - 1

    length = len(y) / input_sampling_rate
    sampling_rate = max(50, min(1000, 10000 / length))

    step = max(1.0, input_sampling_rate / sampling_rate)
    num_windows = round(len(y) / step)
    waveform = []
    for window in np.array_split(y, num_windows):
        waveform.append(window.max())
        waveform.append(window.min())
    return np.array(waveform)
