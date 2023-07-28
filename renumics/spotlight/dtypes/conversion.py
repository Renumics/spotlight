"""
DType Conversion
"""

from collections import defaultdict
from inspect import signature
from dataclasses import dataclass
from typing import Any, Callable, List, TypeVar, Union, Type, Optional, Dict
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


NormalizedValue = Union[
    int,
    float,
    bool,
    str,
    bytes,
    datetime.datetime,
    np.ndarray,
    None,
    list,
]
ConvertedValue = Union[
    int, float, bool, str, bytes, datetime.datetime, np.ndarray, None
]


@dataclass(frozen=True)
class DTypeOptions:
    """
    All possible dtype options
    """

    categories: Optional[Dict[str, int]] = None


class ConversionError(Exception):
    """
    Type Conversion failed
    """


N = TypeVar("N", bound=NormalizedValue)

Converter = Callable[[N, DTypeOptions], ConvertedValue]
ConverterWithoutOptions = Callable[[N], ConvertedValue]
_converters_table: Dict[
    Type[NormalizedValue], Dict[Type[ColumnType], List[Converter]]
] = defaultdict(lambda: defaultdict(list))
_simple_converters_table: Dict[
    Type[NormalizedValue], Dict[Type[ColumnType], List[Converter]]
] = defaultdict(lambda: defaultdict(list))


def register_converter(
    from_type: Type[N],
    to_type: Type[ColumnType],
    converter: Converter[N],
    simple: bool = False,
) -> None:
    """
    register a converter from NormalizedType to ColumnType
    """
    if simple:
        _simple_converters_table[from_type][to_type].append(converter)  # type: ignore
    else:
        _converters_table[from_type][to_type].append(converter)  # type: ignore


def convert(
    from_type: Type[N], to_type: Type[ColumnType], simple: bool = False
) -> Callable:
    """
    Decorator for simplified registration of converters
    """

    def _decorate(
        func: Union[Converter[N], ConverterWithoutOptions[N]]
    ) -> Converter[N]:
        if len(signature(func).parameters) == 1:

            def _converter(value: Any, _: DTypeOptions) -> ConvertedValue:
                return func(value)  # type: ignore

        else:
            _converter = func  # type: ignore

        register_converter(from_type, to_type, _converter, simple)
        return _converter

    return _decorate


def convert_to_dtype(
    value: NormalizedValue,
    dtype: Type[ColumnType],
    dtype_options: DTypeOptions = DTypeOptions(),
    simple: bool = False,
) -> ConvertedValue:
    """
    Convert normalized type from data source to internal Spotlight DType
    """
    # pylint: disable=too-many-return-statements, too-many-branches, too-many-statements
    registered_converters = (
        (
            _simple_converters_table[type(value)][dtype]
            or _converters_table[type(value)][dtype]
        )
        if simple
        else _converters_table[type(value)][dtype]
    )
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
            str_value = str(value)
            if simple and len(str_value) > 100:
                return str_value[:97] + "..."
            return str_value
        if value is None:
            return None
        if dtype is np.ndarray:
            if simple:
                return "[...]"
            if isinstance(value, list):
                return np.array(value)
            if isinstance(value, np.ndarray):
                return value

        # TODO: normalize integer types in datasource?
        if dtype is Category and np.issubdtype(np.dtype(type(value)), np.integer):
            assert dtype_options.categories is not None
            value_int = int(value)  # type: ignore
            if value_int != -1 and value_int not in dtype_options.categories.values():
                raise ConversionError()
            return value_int

    except (TypeError, ValueError) as e:
        raise ConversionError() from e
    raise ConversionError()


@convert(datetime.datetime, datetime.datetime)
def _(value: datetime.datetime) -> datetime.datetime:
    return value


@convert(str, datetime.datetime)
@convert(np.str_, datetime.datetime)
def _(value: Union[str, np.str_]) -> Optional[datetime.datetime]:
    if value == "":
        return None
    return datetime.datetime.fromisoformat(value)


@convert(np.datetime64, datetime.datetime)  # type: ignore
def _(value: np.datetime64) -> datetime.datetime:
    return value.tolist()


@convert(str, Category)
def _(value: str, options: DTypeOptions) -> int:
    if not options.categories:
        return -1
    return options.categories[value]


@convert(type(None), Category)
def _(_: None) -> int:
    return -1


@convert(int, Category)
def _(value: int) -> int:
    return value


@convert(type(None), Window)
def _(_: None) -> np.ndarray:
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
def _(value: Union[np.ndarray, list], _: DTypeOptions) -> np.ndarray:
    return Sequence1D(value).encode()


@convert(str, Image)
def _(value: str) -> bytes:
    data = read_external_value(value, Image)
    if data is None:
        raise ConversionError()
    return data.tolist()


@convert(bytes, Image)
def _(value: bytes) -> bytes:
    return Image.from_bytes(value).encode().tolist()


@convert(np.ndarray, Image)
def _(value: np.ndarray) -> bytes:
    return Image(value).encode().tolist()


@convert(str, Audio)
def _(value: str) -> bytes:
    if data := read_external_value(value, Audio):
        return data.tolist()
    raise ConversionError()


@convert(bytes, Audio)
def _(value: bytes) -> bytes:
    return Audio.from_bytes(value).encode().tolist()


@convert(str, Video)
def _(value: str) -> bytes:
    if data := read_external_value(value, Video):
        return data.tolist()
    raise ConversionError()


@convert(bytes, Video)
def _(value: bytes) -> bytes:
    return Video.from_bytes(value).encode().tolist()


@convert(str, Mesh)
def _(value: str) -> bytes:
    if data := read_external_value(value, Mesh):
        return data.tolist()
    raise ConversionError()


@convert(bytes, Mesh)
def _(value: bytes) -> bytes:
    return value


# this should not be necessary
@convert(trimesh.Trimesh, Mesh)  # type: ignore
def _(value: trimesh.Trimesh) -> bytes:
    return Mesh.from_trimesh(value).encode().tolist()


@convert(list, Embedding, simple=True)
@convert(np.ndarray, Embedding, simple=True)
@convert(list, Sequence1D, simple=True)
@convert(np.ndarray, Sequence1D, simple=True)
@convert(np.ndarray, Image, simple=True)
def _(_: Union[np.ndarray, list]) -> str:
    return "[...]"


@convert(str, Image, simple=True)
@convert(str, Audio, simple=True)
@convert(str, Video, simple=True)
@convert(str, Mesh, simple=True)
def _(value: str) -> str:
    return value


@convert(bytes, Image, simple=True)
@convert(bytes, Audio, simple=True)
@convert(bytes, Video, simple=True)
@convert(bytes, Mesh, simple=True)
def _(_: bytes) -> str:
    return "<bytes>"


# this should not be necessary
@convert(trimesh.Trimesh, Mesh, simple=True)  # type: ignore
def _(_: trimesh.Trimesh) -> str:
    return "<object>"
