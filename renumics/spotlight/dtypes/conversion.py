"""
DType Conversion

None: None
bool: bool, np.bool_
int: int, np.integer
float: float, np.floating
str: str, np.str_
datetime: datetime, np.datetime64
Category: int, np.integer
Array-like: List[Union[float, int], ...], np.ndarray[dtype=fiu]
binary: bytes, np.bytes_
paths: str, np.str_
"""

from abc import ABCMeta
import ast
from collections import defaultdict
from dataclasses import dataclass
import io
import os
from inspect import signature
from typing import (
    Callable,
    List,
    TypeVar,
    Union,
    Type,
    Optional,
    Dict,
    get_args,
    get_origin,
    cast,
)
import datetime
from filetype import filetype

import numpy as np
import trimesh
import validators

from renumics.spotlight.typing import PathOrUrlType, PathType
from renumics.spotlight.cache import external_data_cache
from renumics.spotlight.io import audio
from renumics.spotlight.io.file import as_file

from renumics.spotlight.dtypes.exceptions import InvalidFile

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
    None,
    bool,
    np.bool_,
    int,
    np.integer,
    float,
    np.floating,
    str,
    np.str_,
    datetime.datetime,
    np.datetime64,
    list,
    np.ndarray,
    bytes,
    np.bytes_,
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
    converter: Union[Converter[N], ConverterWithoutOptions[N]],
    simple: Optional[bool] = None,
) -> None:
    """
    register a converter from NormalizedType to ColumnType
    """

    parameter_count = len(signature(converter).parameters)
    if parameter_count == 2:
        converter_with_options = cast(Converter[N], converter)
    else:

        def converter_with_options(value: N, _: DTypeOptions, /) -> ConvertedValue:
            return cast(Converter[N], converter)(value)  # type: ignore

    if simple is None:
        _simple_converters_table[from_type][to_type].append(converter_with_options)  # type: ignore
        _converters_table[from_type][to_type].append(converter_with_options)  # type: ignore
    elif simple:
        _simple_converters_table[from_type][to_type].append(converter_with_options)  # type: ignore
    else:
        _converters_table[from_type][to_type].append(converter_with_options)  # type: ignore


def convert(to_type: Type[ColumnType], simple: Optional[bool] = None) -> Callable:
    """
    Decorator for simplified registration of converters
    """

    def _decorate(
        func: Union[Converter[N], ConverterWithoutOptions[N]]
    ) -> Union[Converter[N], ConverterWithoutOptions[N]]:
        value_annotation = next(iter(func.__annotations__.values()))

        if origin := get_origin(value_annotation):
            assert origin == Union
            from_types = get_args(value_annotation)
            for from_type in from_types:
                register_converter(from_type, to_type, func, simple)
        else:
            from_type = value_annotation
            if from_type is None:
                from_type = type(None)
            assert type(from_type) in (type, ABCMeta)
            register_converter(from_type, to_type, func, simple)  # type: ignore

        return func

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
        if value is None:
            return None
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


@convert(datetime.datetime)
def _(value: datetime.datetime) -> datetime.datetime:
    return value


@convert(datetime.datetime)
def _(value: Union[str, np.str_]) -> Optional[datetime.datetime]:
    if value == "":
        return None
    return datetime.datetime.fromisoformat(value)


@convert(datetime.datetime)  # type: ignore
def _(value: np.datetime64) -> datetime.datetime:
    return value.tolist()


@convert(Category)
def _(value: Union[str, np.str_], options: DTypeOptions) -> int:
    if not options.categories:
        return -1
    return options.categories[value]


@convert(Category)
def _(_: None) -> int:
    return -1


@convert(Category)
def _(value: int) -> int:
    return value


@convert(Window)
def _(_: None) -> np.ndarray:
    return np.full((2,), np.nan, dtype=np.float64)


@convert(Window)
def _(value: list) -> np.ndarray:
    return np.array(value, dtype=np.float64)


@convert(Window)
def _(value: np.ndarray) -> np.ndarray:
    return value.astype(np.float64)


@convert(Window)
def _(value: Union[str, np.str_]) -> np.ndarray:
    try:
        obj = ast.literal_eval(value)
        array = np.array(obj, dtype=np.float64)
        if array.shape != (2,):
            raise ValueError
        return array
    except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
        raise ConversionError("Cannot interpret string as a window")


@convert(Embedding, simple=False)
def _(value: list) -> np.ndarray:
    return np.array(value, dtype=np.float64)


@convert(Embedding, simple=False)
def _(value: np.ndarray) -> np.ndarray:
    return value.astype(np.float64)


@convert(Embedding, simple=False)
def _(value: Union[str, np.str_]) -> np.ndarray:
    try:
        obj = ast.literal_eval(value)
        array = np.array(obj, dtype=np.float64)
        if array.ndim != 1 or array.size == 0:
            raise ValueError
        return array
    except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
        raise ConversionError("Cannot interpret string as an embedding")


@convert(Sequence1D, simple=False)
def _(value: Union[np.ndarray, list], _: DTypeOptions) -> np.ndarray:
    return Sequence1D(value).encode()


@convert(Sequence1D, simple=False)
def _(value: Union[str, np.str_]) -> np.ndarray:
    try:
        obj = ast.literal_eval(value)
        return Sequence1D(obj).encode()
    except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
        raise ConversionError("Cannot interpret string as a 1D sequence")


@convert(Image, simple=False)
def _(value: Union[str, np.str_]) -> bytes:
    try:
        if data := read_external_value(value, Image):
            return data.tolist()
    except InvalidFile:
        raise ConversionError()
    raise ConversionError()


@convert(Image, simple=False)
def _(value: Union[bytes, np.bytes_]) -> bytes:
    return Image.from_bytes(value).encode().tolist()


@convert(Image, simple=False)
def _(value: np.ndarray) -> bytes:
    return Image(value).encode().tolist()


@convert(Audio, simple=False)
def _(value: Union[str, np.str_]) -> bytes:
    try:
        if data := read_external_value(value, Audio):
            return data.tolist()
    except InvalidFile:
        raise ConversionError()
    raise ConversionError()


@convert(Audio, simple=False)
def _(value: Union[bytes, np.bytes_]) -> bytes:
    return Audio.from_bytes(value).encode().tolist()


@convert(Video, simple=False)
def _(value: Union[str, np.str_]) -> bytes:
    try:
        if data := read_external_value(value, Video):
            return data.tolist()
    except InvalidFile:
        raise ConversionError()
    raise ConversionError()


@convert(Video, simple=False)
def _(value: Union[bytes, np.bytes_]) -> bytes:
    return Video.from_bytes(value).encode().tolist()


@convert(Mesh, simple=False)
def _(value: Union[str, np.str_]) -> bytes:
    try:
        if data := read_external_value(value, Mesh):
            return data.tolist()
    except InvalidFile:
        raise ConversionError()
    raise ConversionError()


@convert(Mesh, simple=False)
def _(value: Union[bytes, np.bytes_]) -> bytes:
    return value


# this should not be necessary
@convert(Mesh, simple=False)  # type: ignore
def _(value: trimesh.Trimesh) -> bytes:
    return Mesh.from_trimesh(value).encode().tolist()


@convert(Embedding, simple=True)
@convert(Sequence1D, simple=True)
def _(_: Union[np.ndarray, list, str, np.str_]) -> str:
    return "[...]"


@convert(Image, simple=True)
def _(_: np.ndarray) -> str:
    return "[...]"


@convert(Image, simple=True)
@convert(Audio, simple=True)
@convert(Video, simple=True)
@convert(Mesh, simple=True)
def _(value: Union[str, np.str_]) -> str:
    return str(value)


@convert(Image, simple=True)
@convert(Audio, simple=True)
@convert(Video, simple=True)
@convert(Mesh, simple=True)
def _(_: Union[bytes, np.bytes_]) -> str:
    return "<bytes>"


# this should not be necessary
@convert(Mesh, simple=True)  # type: ignore
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
