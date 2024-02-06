import os
from typing import Optional, Union

import numpy as np
import requests
import validators

from renumics.spotlight.media.base import FileMediaType
from renumics.spotlight.requests import headers
from renumics.spotlight.typing import PathType

from ..media import exceptions


class Video(FileMediaType):
    """
    A video object. No encoding or decoding is currently performed on the python
    side, so all formats will be saved into dataset without compatibility check,
    but only the formats supported by your browser (apparently .mp4, .ogg,
    .webm, .mov etc.) can be played in Spotlight.
    """

    data: bytes

    def __init__(self, data: bytes) -> None:
        if not isinstance(data, bytes):
            raise TypeError(
                f"`data` argument should be video bytes, but type {type(data)} "
                f"received."
            )
        self.data = data

    @classmethod
    def from_file(cls, filepath: PathType) -> "Video":
        """
        Read video from a filepath or an URL.
        """
        prepared_file = str(filepath) if isinstance(filepath, os.PathLike) else filepath
        if not isinstance(prepared_file, str):
            raise TypeError(
                "`filepath` should be a string or an `os.PathLike` instance, "
                f"but value {prepared_file} or type {type(prepared_file)} "
                f"received."
            )
        if validators.url(prepared_file):
            response = requests.get(
                prepared_file, headers=headers, stream=True, timeout=10
            )
            if not response.ok:
                raise exceptions.InvalidFile(f"URL {prepared_file} does not exist.")
            return cls(response.raw.data)
        if os.path.isfile(prepared_file):
            with open(filepath, "rb") as f:
                return cls(f.read())
        raise exceptions.InvalidFile(
            f"File {prepared_file} is neither an existing file nor an existing URL."
        )

    @classmethod
    def from_bytes(cls, blob: bytes) -> "Video":
        """
        Read video from raw bytes.
        """
        return cls(blob)

    @classmethod
    def empty(cls) -> "Video":
        """
        Create an empty video instance.
        """
        return cls(b"\x00")

    @classmethod
    def decode(cls, value: Union[np.ndarray, np.void]) -> "Video":
        if isinstance(value, np.void):
            return cls(value.tolist())
        raise TypeError(
            f"`value` should be a `numpy.void` instance, but {type(value)} "
            f"received."
        )

    def encode(self, _target: Optional[str] = None) -> np.void:
        return np.void(self.data)
