"""
DType Conversion
"""

from dataclasses import dataclass
from typing import Union, Type, Optional, Dict
import datetime

import numpy as np
import trimesh

from renumics.spotlight.backend.data_source import read_external_value
from .typing import (
    ColumnType,
    Category,
    Window,
    Sequence1D,
    Embedding,
    Image,
    Audio,
    Video,
    Mesh,
)


NormalizedType = Union[int, float, bool, str, bytes, datetime.datetime, np.ndarray]
ConvertedType = Union[
    int, float, bool, str, bytes, datetime.datetime, np.ndarray, np.void
]


@dataclass
class DTypeOptions:
    """
    All possible dtype options
    """

    categories: Optional[Dict[str, int]] = None


class ConversionError(Exception):
    """
    Type Conversion failed
    """


def convert_to_dtype(
    value: Optional[NormalizedType],
    dtype: Type[ColumnType],
    dtype_options: DTypeOptions = DTypeOptions(),
) -> Optional[ConvertedType]:
    """
    Convert normalized type from data source to internal Spotlight DType
    """
    # pylint: disable=too-many-return-statements, too-many-branches, too-many-statements

    try:
        if dtype is bool:
            return bool(value)  # type: ignore
        if dtype is int:
            return int(value)  # type: ignore
        if dtype is float:
            return float(value)  # type: ignore
        if dtype is str:
            return str(value)

        if dtype is datetime.datetime:
            if value is None:
                return None
            if isinstance(value, datetime.datetime):
                return value
            if isinstance(value, str):
                return datetime.datetime.fromisoformat(value)
            if isinstance(value, np.datetime64):
                return value.tolist()

        elif dtype is Category:
            assert dtype_options.categories is not None
            if value is None:
                # maybe simply return None?
                return -1
            if isinstance(value, str):
                return dtype_options.categories[value]
            if isinstance(value, int):
                if value not in dtype_options.categories.values():
                    raise ConversionError()
                return value

        elif dtype is np.ndarray:
            if isinstance(value, list):
                return np.array(value)
            if isinstance(value, np.ndarray):
                return value

        elif dtype is Window:
            if value is None:
                return np.full((2,), np.nan, dtype=np.float64)
            if isinstance(value, list):
                return np.array(value, dtype=np.float64)
            if isinstance(value, np.ndarray):
                return value.astype(np.float64)

        elif dtype is Embedding:
            if value is None:
                return None
            if isinstance(value, list):
                return np.array(value, dtype=np.float64)
            if isinstance(value, np.ndarray):
                return value.astype(np.float64)

        elif dtype is Sequence1D:
            if value is None:
                return None
            return Sequence1D(value).encode()  # type: ignore

        elif dtype is Image:
            if value is None:
                return None
            if isinstance(value, str):
                return read_external_value(value, Image)
            if isinstance(value, bytes):
                return Image.from_bytes(value).encode()
            if isinstance(value, np.ndarray):
                return Image(value).encode()

        elif dtype is Audio:
            if value is None:
                return None
            if isinstance(value, str):
                return read_external_value(value, Audio)
            if isinstance(value, bytes):
                return Audio.from_bytes(value).encode()

        elif dtype is Video:
            if value is None:
                return None
            if isinstance(value, str):
                return read_external_value(value, Video)
            if isinstance(value, bytes):
                return Audio.from_bytes(value).encode()

        elif dtype is Mesh:
            if value is None:
                return None
            if isinstance(value, str):
                return read_external_value(value, Mesh)
            if isinstance(value, trimesh.Trimesh):
                return Mesh.from_trimesh(value).encode()

    except (TypeError, ValueError) as e:
        raise ConversionError() from e
    raise ConversionError()
