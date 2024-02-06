import io
from typing import Optional, Tuple, Union

import numpy as np

from renumics.spotlight.media.base import Array2dLike, FileMediaType
from renumics.spotlight.typing import FileType

from ..io import audio
from . import exceptions


class Audio(FileMediaType):
    """
    An Audio Signal that will be saved in encoded form.

    All formats and codecs supported by AV are supported for read.

    Attributes:
        data: Array-like with shape `(num_samples, num_channels)`
            with `num_channels` <= 5.
            If `data` has a float dtype, its values should be between -1 and 1.
            If `data` has an int dtype, its values should be between minimum and
            maximum possible values for the particular int dtype.
            If `data` has an unsigned int dtype, ist values should be between 0
            and maximum possible values for the particular unsigned int dtype.
        sampling_rate: Sampling rate (samples per seconds)

    Example:
        >>> import numpy as np
        >>> from renumics.spotlight import Dataset, Audio
        >>> samplerate = 44100
        >>> fs = 100 # 100 Hz audio signal
        >>> time = np.linspace(0.0, 1.0, samplerate)
        >>> amplitude = np.iinfo(np.int16).max * 0.4
        >>> data = np.array(amplitude * np.sin(2.0 * np.pi * fs * time), dtype=np.int16)
        >>> audio = Audio(samplerate, np.array([data, data]).T)  # int16 stereo signal
        >>> float_data = 0.5 * np.cos(2.0 * np.pi * fs * time).astype(np.float32)
        >>> float_audio = Audio(samplerate, float_data)  # float32 mono signal
        >>> with Dataset("docs/example.h5", "w") as dataset:
        ...     dataset.append_audio_column("audio", [audio, float_audio])
        ...     dataset.append_audio_column("lossy_audio", [audio, float_audio], lossy=True)
        >>> with Dataset("docs/example.h5", "r") as dataset:
        ...     print(dataset["audio", 0].data[100])
        ...     print(f"{dataset['lossy_audio', 1].data[0, 0]:.5g}")
        [12967 12967]
        0.4596
    """

    data: np.ndarray
    sampling_rate: int

    def __init__(self, sampling_rate: int, data: Array2dLike) -> None:
        data_array = np.asarray(data)
        is_valid_multi_channel = (
            data_array.size > 0 and data_array.ndim == 2 and data_array.shape[1] <= 5
        )
        is_valid_mono = data_array.size > 0 and data_array.ndim == 1
        if not (is_valid_multi_channel or is_valid_mono):
            raise ValueError(
                f"`data` argument should be a 1D array for mono data"
                f" or a 2D numpy array with shape "
                f"`(num_samples, num_channels)` and with num_channels <= 5, "
                f"but shape {data_array.shape} received."
            )
        if data_array.dtype not in [np.float32, np.int32, np.int16, np.uint8]:
            raise ValueError(
                f"`data` argument should be a numpy array with "
                f"dtype np.float32, np.int32, np.int16 or np.uint8, "
                f"but dtype {data_array.dtype.name} received."
            )
        self.data = data_array
        self.sampling_rate = sampling_rate

    @classmethod
    def from_file(cls, filepath: FileType) -> "Audio":
        """
        Read audio file from a filepath, an URL, or a file-like object.

        `pyav` is used inside, so only supported formats are allowed.
        """
        try:
            data, sampling_rate = audio.read_audio(filepath)
        except Exception as e:
            raise exceptions.InvalidFile(
                f"Audio file {filepath} does not exist or could not be read."
            ) from e
        return cls(sampling_rate, data)

    @classmethod
    def from_bytes(cls, blob: bytes) -> "Audio":
        """
        Read audio from raw bytes.

        `pyav` is used inside, so only supported formats are allowed.
        """
        try:
            data, sampling_rate = audio.read_audio(io.BytesIO(blob))
        except Exception as e:
            raise exceptions.InvalidFile(
                "Audio could not be read from the given bytes."
            ) from e
        return cls(sampling_rate, data)

    @classmethod
    def empty(cls) -> "Audio":
        """
        Create a single zero-value sample stereo audio signal.
        """
        return cls(1, np.zeros((1, 2), np.int16))

    @classmethod
    def decode(cls, value: Union[np.ndarray, np.void]) -> "Audio":
        if isinstance(value, np.void):
            buffer = io.BytesIO(value.tolist())
            data, sampling_rate = audio.read_audio(buffer)
            return cls(sampling_rate, data)
        raise TypeError(
            f"`value` should be a `numpy.void` instance, but {type(value)} "
            f"received."
        )

    def encode(self, target: Optional[str] = None) -> np.void:
        format_, codec = self.get_format_codec(target)
        buffer = io.BytesIO()
        audio.write_audio(buffer, self.data, self.sampling_rate, format_, codec)
        return np.void(buffer.getvalue())

    @staticmethod
    def get_format_codec(target: Optional[str] = None) -> Tuple[str, str]:
        """
        Get an audio format and an audio codec by an `target`.
        """
        format_ = "wav" if target is None else target.lstrip(".").lower()
        codec = {"wav": "pcm_s16le", "ogg": "libvorbis", "mp3": "libmp3lame"}.get(
            format_, format_
        )
        return format_, codec
