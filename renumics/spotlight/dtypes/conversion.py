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
import inspect
import io
import os
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
)
import datetime
from filetype import filetype

import numpy as np
import trimesh
import PIL.Image
import validators
from renumics.spotlight import dtypes

from renumics.spotlight.typing import PathOrUrlType, PathType
from renumics.spotlight.cache import external_data_cache
from renumics.spotlight.io import audio
from renumics.spotlight.io.file import as_file
from renumics.spotlight.media.exceptions import InvalidFile
from renumics.spotlight.backend.exceptions import Problem
from renumics.spotlight.dtypes import (
    CategoryDType,
    DType,
    audio_dtype,
    image_dtype,
    mesh_dtype,
    video_dtype,
)
from renumics.spotlight.media import Sequence1D, Image, Audio, Video, Mesh


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


class ConversionError(Exception):
    """
    Conversion Error
    raise in Converter on errors or invalid input data
    """

    def __init__(self, reason: Optional[str] = None):
        self.reason = reason


class ConversionFailed(Problem):
    """
    Type Conversion failed
    """

    def __init__(
        self,
        value: NormalizedValue,
        dtype: DType,
        reason: Optional[str] = None,
    ) -> None:
        super().__init__(
            title="Conversion failed",
            detail=inspect.cleandoc(
                f"""
               Failed to convert value of type {type(value)} to dtype {dtype}.
               {"" if reason is None else reason}
            """
            ),
            status_code=422,
        )


class NoConverterAvailable(Problem):
    """
    No matching converter could be applied
    """

    def __init__(self, value: NormalizedValue, dtype: DType) -> None:
        msg = f"No Converter for {type(value)} -> {dtype}"
        super().__init__(title="No matching converter", detail=msg, status_code=422)


N = TypeVar("N", bound=NormalizedValue)

Converter = Callable[[N, DType], ConvertedValue]
_converters_table: Dict[
    Type[NormalizedValue], Dict[str, List[Converter]]
] = defaultdict(lambda: defaultdict(list))
_simple_converters_table: Dict[
    Type[NormalizedValue], Dict[str, List[Converter]]
] = defaultdict(lambda: defaultdict(list))


def register_converter(
    from_type: Type[N],
    to_type: str,
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


def convert(to_type: str, simple: Optional[bool] = None) -> Callable:
    """
    Decorator for simplified registration of converters
    """

    def _decorate(func: Converter[N]) -> Converter[N]:
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
    value: NormalizedValue, dtype: DType, simple: bool = False, check: bool = True
) -> ConvertedValue:
    """
    Convert normalized type from data source to internal Spotlight DType
    """

    registered_converters = (
        _simple_converters_table[type(value)][dtype.name]
        if simple
        else _converters_table[type(value)][dtype.name]
    )

    last_conversion_error: Optional[ConversionError] = None

    for converter in registered_converters:
        try:
            return converter(value, dtype)
        except ConversionError as e:
            last_conversion_error = e

    try:
        if value is None:
            return None
        if dtypes.is_bool_dtype(dtype):
            return bool(value)  # type: ignore
        if dtypes.is_int_dtype(dtype):
            return int(value)  # type: ignore
        if dtypes.is_float_dtype(dtype):
            return float(value)  # type: ignore
        if dtypes.is_str_dtype(dtype):
            str_value = str(value)
            if simple and len(str_value) > 100:
                return str_value[:97] + "..."
            return str_value
        if dtypes.is_array_dtype(dtype):
            if simple:
                return "[...]"
            if isinstance(value, list):
                return np.array(value)
            if isinstance(value, np.ndarray):
                return value

    except (TypeError, ValueError) as e:
        if check:
            raise ConversionFailed(value, dtype) from e
        else:
            return None

    if check:
        if last_conversion_error:
            raise ConversionFailed(value, dtype, last_conversion_error.reason)
        else:
            raise NoConverterAvailable(value, dtype)

    return None


@convert("datetime")
def _(value: datetime.datetime, _: DType) -> datetime.datetime:
    return value


@convert("datetime")
def _(value: Union[str, np.str_], _: DType) -> Optional[datetime.datetime]:
    if value == "":
        return None
    return datetime.datetime.fromisoformat(value)


@convert("datetime")
def _(value: np.datetime64, _: DType) -> Optional[datetime.datetime]:
    return value.tolist()


@convert("Category")
def _(value: Union[str, np.str_], dtype: CategoryDType) -> int:
    categories = dtype.categories
    if not categories:
        return -1
    return categories[value]


@convert("Category")
def _(_: None, _dtype: CategoryDType) -> int:
    return -1


@convert("Category")
def _(
    value: Union[
        int,
        np.int8,
        np.int16,
        np.int32,
        np.int64,
        np.uint8,
        np.uint16,
        np.uint32,
        np.uint64,
    ],
    _: CategoryDType,
) -> int:
    return int(value)


@convert("Window")
def _(value: list, _: DType) -> np.ndarray:
    return np.array(value, dtype=np.float64)


@convert("Window")
def _(value: np.ndarray, _: DType) -> np.ndarray:
    return value.astype(np.float64)


@convert("Window")
def _(value: Union[str, np.str_], _: DType) -> np.ndarray:
    try:
        obj = ast.literal_eval(value)
        array = np.array(obj, dtype=np.float64)
        if array.shape != (2,):
            raise ValueError
        return array
    except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
        raise ConversionError("Cannot interpret string as a window")


@convert("Embedding", simple=False)
def _(value: list, _: DType) -> np.ndarray:
    return np.array(value, dtype=np.float64)


@convert("Embedding", simple=False)
def _(value: np.ndarray, _: DType) -> np.ndarray:
    return value.astype(np.float64)


@convert("Embedding", simple=False)
def _(value: Union[str, np.str_], _: DType) -> np.ndarray:
    try:
        obj = ast.literal_eval(value)
        array = np.array(obj, dtype=np.float64)
        if array.ndim != 1 or array.size == 0:
            raise ValueError
        return array
    except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
        raise ConversionError("Cannot interpret string as an embedding")


@convert("Sequence1D", simple=False)
def _(value: Union[np.ndarray, list], _: DType) -> np.ndarray:
    return Sequence1D(value).encode()


@convert("Sequence1D", simple=False)
def _(value: Union[str, np.str_], _: DType) -> np.ndarray:
    try:
        obj = ast.literal_eval(value)
        return Sequence1D(obj).encode()
    except (ValueError, TypeError, SyntaxError, MemoryError, RecursionError):
        raise ConversionError("Cannot interpret string as a 1D sequence")


@convert("Image", simple=False)
def _(value: Union[str, np.str_], _: DType) -> bytes:
    try:
        if data := read_external_value(value, image_dtype):
            return data.tolist()
    except InvalidFile:
        raise ConversionError()
    raise ConversionError()


@convert("Image", simple=False)
def _(value: Union[bytes, np.bytes_], _: DType) -> bytes:
    return Image.from_bytes(value).encode().tolist()


@convert("Image", simple=False)
def _(value: np.ndarray, _: DType) -> bytes:
    return Image(value).encode().tolist()


@convert("Image", simple=False)
def _(value: PIL.Image.Image, _: DType) -> bytes:
    buffer = io.BytesIO()
    value.save(buffer, format="PNG")
    return buffer.getvalue()


@convert("Audio", simple=False)
def _(value: Union[str, np.str_], _: DType) -> bytes:
    try:
        if data := read_external_value(value, audio_dtype):
            return data.tolist()
    except (InvalidFile, IndexError, ValueError):
        raise ConversionError()
    raise ConversionError()


@convert("Audio", simple=False)
def _(value: Union[bytes, np.bytes_], _: DType) -> bytes:
    return Audio.from_bytes(value).encode().tolist()


@convert("Video", simple=False)
def _(value: Union[str, np.str_], _: DType) -> bytes:
    try:
        if data := read_external_value(value, video_dtype):
            return data.tolist()
    except InvalidFile:
        raise ConversionError()
    raise ConversionError()


@convert("Video", simple=False)
def _(value: Union[bytes, np.bytes_], _: DType) -> bytes:
    return Video.from_bytes(value).encode().tolist()


@convert("Mesh", simple=False)
def _(value: Union[str, np.str_], _: DType) -> bytes:
    try:
        if data := read_external_value(value, mesh_dtype):
            return data.tolist()
    except InvalidFile:
        raise ConversionError()
    raise ConversionError()


@convert("Mesh", simple=False)
def _(value: Union[bytes, np.bytes_], _: DType) -> bytes:
    return value


# this should not be necessary
@convert("Mesh", simple=False)  # type: ignore
def _(value: trimesh.Trimesh, _: DType) -> bytes:
    return Mesh.from_trimesh(value).encode().tolist()


@convert("Embedding", simple=True)
@convert("Sequence1D", simple=True)
def _(_: Union[np.ndarray, list, str, np.str_], _dtype: DType) -> str:
    return "[...]"


@convert("Image", simple=True)
def _(_: np.ndarray, _dtype: DType) -> str:
    return "[...]"


@convert("Image", simple=True)
def _(_: PIL.Image.Image, _dtype: DType) -> str:
    return "<PIL.Image>"


@convert("Image", simple=True)
@convert("Audio", simple=True)
@convert("Video", simple=True)
@convert("Mesh", simple=True)
def _(value: Union[str, np.str_], _: DType) -> str:
    return str(value)


@convert("Image", simple=True)
@convert("Audio", simple=True)
@convert("Video", simple=True)
@convert("Mesh", simple=True)
def _(_: Union[bytes, np.bytes_], _dtype: DType) -> str:
    return "<bytes>"


# this should not be necessary
@convert("Mesh", simple=True)  # type: ignore
def _(_: trimesh.Trimesh, _dtype: DType) -> str:
    return "<Trimesh>"


def read_external_value(
    path_or_url: Optional[str],
    dtype: DType,
    target_format: Optional[str] = None,
    workdir: PathType = ".",
) -> Optional[np.void]:
    """
    Read a new external value and cache it or get it from the cache if already
    cached.
    """
    if not path_or_url:
        return None
    cache_key = f"external:{path_or_url},{dtype}"
    if target_format is not None:
        cache_key += f"/{target_format}"
    try:
        value = np.void(external_data_cache[cache_key])
        return value
    except KeyError:
        ...

    value = _decode_external_value(path_or_url, dtype, target_format, workdir)
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
    dtype: DType,
    target_format: Optional[str] = None,
    workdir: PathType = ".",
) -> np.void:
    """
    Decode an external value as expected by the rest of the backend.
    """

    path_or_url = prepare_path_or_url(path_or_url, workdir)
    if dtypes.is_audio_dtype(dtype):
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

    if dtypes.is_image_dtype(dtype):
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

    if dtypes.is_mesh_dtype(dtype):
        return Mesh.from_file(path_or_url).encode(target_format)
    if dtypes.is_video_dtype(dtype):
        return Video.from_file(path_or_url).encode(target_format)
    assert False
