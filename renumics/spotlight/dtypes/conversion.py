"""
DType Conversion
"""

from collections import defaultdict
from inspect import signature
from dataclasses import dataclass
import io
import os
from typing import Any, Callable, List, TypeVar, Union, Type, Optional, Dict
import datetime
from filetype import filetype

import numpy as np
import trimesh
import validators

from renumics.spotlight.typing import PathOrUrlType, PathType
from renumics.spotlight.cache import external_data_cache
from renumics.spotlight.io import audio
from renumics.spotlight.io.file import as_file

from .typing import (
    ColumnType,
    Category,
    FileBasedColumnType,
    Window,
    Sequence1D,
    Embedding,
    Image,
    Audio,
    Video,
    Mesh,
    get_column_type_name,
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


class NoConverterAvailable(Exception):
    """
    No matching converter could be applied
    """

    def __init__(self, value: NormalizedValue, dtype: Type[ColumnType]) -> None:
        msg = f"No Converter for {type(value)} -> {dtype}"
        super().__init__(msg)


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
    simple: Optional[bool] = None,
) -> None:
    """
    register a converter from NormalizedType to ColumnType
    """
    if simple is None:
        _simple_converters_table[from_type][to_type].append(converter)  # type: ignore
        _converters_table[from_type][to_type].append(converter)  # type: ignore
    elif simple:
        _simple_converters_table[from_type][to_type].append(converter)  # type: ignore
    else:
        _converters_table[from_type][to_type].append(converter)  # type: ignore


def convert(
    from_type: Type[N], to_type: Type[ColumnType], simple: Optional[bool] = None
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

    registered_converters = (
        _simple_converters_table[type(value)][dtype]
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

        if dtype is Category and np.issubdtype(np.dtype(type(value)), np.integer):
            assert dtype_options.categories is not None
            value_int = int(value)  # type: ignore
            if value_int != -1 and value_int not in dtype_options.categories.values():
                raise ConversionError()
            return value_int

    except (TypeError, ValueError) as e:
        raise ConversionError() from e

    raise NoConverterAvailable(value, dtype)


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
@convert(np.str_, Category)
def _(value: Union[str, np.str_], options: DTypeOptions) -> int:
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


@convert(list, Embedding, simple=False)
def _(value: list) -> np.ndarray:
    return np.array(value, dtype=np.float64)


@convert(np.ndarray, Embedding, simple=False)
def _(value: np.ndarray) -> np.ndarray:
    return value.astype(np.float64)


@convert(list, Sequence1D, simple=False)
@convert(np.ndarray, Sequence1D, simple=False)
def _(value: Union[np.ndarray, list], _: DTypeOptions) -> np.ndarray:
    return Sequence1D(value).encode()


@convert(str, Image, simple=False)
@convert(np.str_, Image, simple=False)
def _(value: Union[str, np.str_]) -> bytes:
    data = read_external_value(value, Image)
    if data is None:
        raise ConversionError()
    return data.tolist()


@convert(bytes, Image, simple=False)
@convert(np.bytes_, Image, simple=False)
def _(value: Union[bytes, np.bytes_]) -> bytes:
    return Image.from_bytes(value).encode().tolist()


@convert(np.ndarray, Image, simple=False)
def _(value: np.ndarray) -> bytes:
    return Image(value).encode().tolist()


@convert(str, Audio, simple=False)
@convert(np.str_, Audio, simple=False)
def _(value: Union[str, np.str_]) -> bytes:
    if data := read_external_value(value, Audio):
        return data.tolist()
    raise ConversionError()


@convert(bytes, Audio, simple=False)
@convert(np.bytes_, Audio, simple=False)
def _(value: Union[bytes, np.bytes_]) -> bytes:
    return Audio.from_bytes(value).encode().tolist()


@convert(str, Video, simple=False)
@convert(np.str_, Video, simple=False)
def _(value: Union[str, np.str_]) -> bytes:
    if data := read_external_value(value, Video):
        return data.tolist()
    raise ConversionError()


@convert(bytes, Video, simple=False)
@convert(np.bytes_, Video, simple=False)
def _(value: Union[bytes, np.bytes_]) -> bytes:
    return Video.from_bytes(value).encode().tolist()


@convert(str, Mesh, simple=False)
@convert(np.str_, Mesh, simple=False)
def _(value: Union[str, np.str_]) -> bytes:
    if data := read_external_value(value, Mesh):
        return data.tolist()
    raise ConversionError()


@convert(bytes, Mesh, simple=False)
@convert(np.bytes_, Mesh, simple=False)
def _(value: Union[bytes, np.bytes_]) -> bytes:
    return value


# this should not be necessary
@convert(trimesh.Trimesh, Mesh, simple=False)  # type: ignore
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
@convert(np.str_, Image, simple=True)
@convert(str, Audio, simple=True)
@convert(np.str_, Audio, simple=True)
@convert(str, Video, simple=True)
@convert(np.str_, Video, simple=True)
@convert(str, Mesh, simple=True)
@convert(np.str_, Mesh, simple=True)
def _(value: Union[str, np.str_]) -> str:
    return str(value)


@convert(bytes, Image, simple=True)
@convert(np.bytes_, Image, simple=True)
@convert(bytes, Audio, simple=True)
@convert(np.bytes_, Audio, simple=True)
@convert(bytes, Video, simple=True)
@convert(np.bytes_, Video, simple=True)
@convert(bytes, Mesh, simple=True)
@convert(np.bytes_, Mesh, simple=True)
def _(_: Union[bytes, np.bytes_]) -> str:
    return "<bytes>"


# this should not be necessary
@convert(trimesh.Trimesh, Mesh, simple=True)  # type: ignore
def _(_: trimesh.Trimesh) -> str:
    return "<object>"


def read_external_value(
    path_or_url: Optional[str],
    column_type: Type[FileBasedColumnType],
    target_format: Optional[str] = None,
    workdir: PathType = ".",
) -> Optional[np.void]:
    """
    Read a new external value and cache it or get it from the cache if already
    cached.
    """
    if not path_or_url:
        return None
    cache_key = f"external:{path_or_url},{get_column_type_name(column_type)}"
    if target_format is not None:
        cache_key += f"/{target_format}"
    try:
        value = np.void(external_data_cache[cache_key])
        return value
    except KeyError:
        ...

    value = _decode_external_value(path_or_url, column_type, target_format, workdir)
    external_data_cache[cache_key] = value.tolist()
    return value


def prepare_path_or_url(path_or_url: PathOrUrlType, workdir: PathType) -> str:
    """
    For a relative path, prefix it with the `workdir`.
    For an absolute path or an URL, do nothing.
    """
    path_or_url_str = str(path_or_url)
    if validators.url(path_or_url_str):  # type: ignore
        return path_or_url_str
    return os.path.join(workdir, path_or_url_str)


def _decode_external_value(
    path_or_url: PathOrUrlType,
    column_type: Type[FileBasedColumnType],
    target_format: Optional[str] = None,
    workdir: PathType = ".",
) -> np.void:
    """
    Decode an external value as expected by the rest of the backend.
    """

    path_or_url = prepare_path_or_url(path_or_url, workdir)
    if column_type is Audio:
        file = audio.prepare_input_file(path_or_url, reusable=True)
        # `file` is a filepath of type `str` or an URL downloaded as `io.BytesIO`.
        input_format, input_codec = audio.get_format_codec(file)
        if not isinstance(file, str):
            file.seek(0)
        if target_format is None:
            # Try to send data as is.
            if input_format in ("flac", "mp3", "wav") or input_codec in (
                "aac",
                "libvorbis",
                "vorbis",
            ):
                # Format is directly supported by the browser.
                if isinstance(file, str):
                    with open(file, "rb") as f:
                        return np.void(f.read())
                return np.void(file.read())
            # Convert all other formats/codecs to flac.
            output_format, output_codec = "flac", "flac"
        else:
            output_format, output_codec = Audio.get_format_codec(target_format)
        if output_format == input_format and output_codec == input_codec:
            # Nothing to transcode
            if isinstance(file, str):
                with open(file, "rb") as f:
                    return np.void(f.read())
            return np.void(file.read())
        buffer = io.BytesIO()
        audio.transcode_audio(file, buffer, output_format, output_codec)
        return np.void(buffer.getvalue())

    if column_type is Image:
        with as_file(path_or_url) as file:
            kind = filetype.guess(file)
            if kind is not None and kind.mime.split("/")[1] in (
                "apng",
                "avif",
                "gif",
                "jpeg",
                "png",
                "webp",
                "bmp",
                "x-icon",
            ):
                return np.void(file.read())
            # `image/tiff`s become blank in frontend, so convert them too.
            return Image.from_file(file).encode(target_format)

    data_obj = column_type.from_file(path_or_url)
    return data_obj.encode(target_format)
