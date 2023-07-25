"""
DType Conversion
"""

from collections import defaultdict
from inspect import signature
from dataclasses import dataclass
from types import NoneType
from typing import Callable, List, Union, Type, Optional, Dict
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


NormalizedType = Union[int, float, bool, str, bytes, datetime.datetime, np.ndarray, Type[None]]
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


Converter = Callable[[Optional[NormalizedType], DTypeOptions], ColumnType]
ConverterWithoutOptions = Callable[[Optional[NormalizedType]], ColumnType]
_converters_table: Dict[
    Type[NormalizedType], Dict[Type[ColumnType], List[Converter]]
] = defaultdict(lambda: defaultdict(list))


def register_converter(fromType: Type[NormalizedType], toType: Type[ColumnType], converter: Converter):
    """
    register a converter from NormalizedType to ColumnType
    """
    _converters_table[fromType][toType].append(converter)



def convert(fromType: Type[NormalizedType], toType: Type[ConvertedType]):
    """
    Decorator for simplified registration of converters
    """
    def _decorate(func: Union[Converter, ConverterWithoutOptions]):
        if len(signature(func).parameters) == 1:
            def _converter(value, options):
                return func(value) # type: ignore
        else: 
            _converter = func # type: ignore

        register_converter(fromType, toType, _converter)
        return _converter
    return _decorate


def convert_to_dtype(
    value: Optional[NormalizedType],
    dtype: Type[ColumnType],
    dtype_options: DTypeOptions = DTypeOptions(),
) -> Optional[ConvertedType]:
    """
    Convert normalized type from data source to internal Spotlight DType
    """
    # pylint: disable=too-many-return-statements, too-many-branches, too-many-statements
    registered_converters = _converters_table[type(value)][dtype]
    for converter in registered_converters:
        try:
            return converter(value, dtype_options)
        except ConversionError:
            pass

    try:
        if dtype is bool:
            return bool(value)  # type: ignore
        if dtype is int:
            return int(value)  # type: ignore
        if dtype is float:
            return float(value)  # type: ignore
        if dtype is str:
            return str(value)
        if value is None:
            return None
        if dtype is np.ndarray:
            if isinstance(value, list):
                return np.array(value)
            if isinstance(value, np.ndarray):
                return value
        if isinstance(value, dtype):
            return value

        # TODO: normalize integer types in datasource?
        if dtype is Category and np.issubdtype(np.dtype(type(value)), np.integer):
            if int(value) not in dtype_options.categories.values():  # type: ignore
                raise ConversionError()
            return int(value) # type: ignore

    except (TypeError, ValueError) as e:
        raise ConversionError() from e
    raise ConversionError()

@convert(str, datetime.datetime)
def _(value: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(value)

@convert(np.datetime64, datetime.datetime)
def _(value: np.datetime64) -> datetime.datetime:
    return value.tolist()

@convert(str, Category)
def _(value: str, options: DTypeOptions) -> int:
    return options.categories[value]

@convert(NoneType, Category)
def _(_: NoneType) -> int:
    return -1

@convert(NoneType, Window)
def _(_: NoneType) -> np.ndarray:
    return np.full((2,), np.nan, dtype=np.float64)

@convert(list, Window)
def _(value: list) -> np.ndarray:
    return np.array(value, dtype=np.float64)
    
@convert(np.ndarray, Window)
def _(value: np.ndarray) -> np.ndarray:
    return value.astype(np.float64)

@convert(list, Embedding)
def _(value: list) -> np.ndarray:
    return np.array(value, dtype=np.float64)

@convert(np.ndarray, Embedding)
def _(value: np.ndarray) -> np.ndarray:
    return value.astype(np.float64)

@convert(list, Sequence1D)
@convert(np.ndarray, Sequence1D)
def _(value: Union[np.ndarray, list]):
    return Sequence1D(value).encode().tolist()

@convert(str, Image)
def _(value: str) -> Optional[bytes]:
    data = read_external_value(value, Image)
    if data is None:
        return None
    else:
        return data.tolist()

@convert(bytes, Image)
def _(value: bytes) -> bytes:
    return Image.from_bytes(value).encode().tolist()

@convert(np.ndarray, Image)
def _(value: np.ndarray) -> bytes:
    return Image(value).encode().tolist()

@convert(str, Audio)
def _(value: str) -> Optional[bytes]:
    if data := read_external_value(value, Audio):
        return data.tolist()
    else:
        return None

@convert(bytes, Audio)
def _(value: bytes) -> bytes:
    return Audio.from_bytes(value).encode().tolist()


@convert(str, Video)
def _(value: str) -> Optional[bytes]:
    if data := read_external_value(value, Video):
        return data.tolist()
    else:
        return None

@convert(bytes, Video)
def _(value: str) -> bytes:
    return Video.from_bytes(value).encode().tolist()

@convert(str, Mesh)
def _(value: str) -> Optional[bytes]:
    if data := read_external_value(value, Mesh):
        return data.tolist()
    else:
        return None

@convert(bytes, Mesh)
def _(value: bytes) -> bytes:
    return value

@convert(trimesh.Trimesh, Mesh)
def _(value: trimesh.Trimesh) -> bytes:
    return Mesh.from_trimesh(value).encode().tolist()
