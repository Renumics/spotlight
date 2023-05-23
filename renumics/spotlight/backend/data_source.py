"""provides access to different data sources (h5, pandas, etc.)"""

import dataclasses
import hashlib
import io
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Type, Optional, List, Dict, Any, cast

import pandas as pd
import numpy as np
from pydantic.dataclasses import dataclass

from renumics.spotlight.io import audio
from renumics.spotlight.typing import PathOrURLType, PathType, is_iterable
from renumics.spotlight.dataset import prepare_path_or_url
from renumics.spotlight.dataset.exceptions import (
    ColumnExistsError,
    ColumnNotExistsError,
)
from renumics.spotlight.dtypes import Audio
from renumics.spotlight.dtypes.typing import (
    ColumnType,
    ColumnTypeMapping,
    FileBasedColumnType,
    get_column_type_name,
)
from .cache import Cache
from .exceptions import DatasetNotEditable, GenerationIDMismatch, NoRowFound

cache = Cache("external-data")


@dataclasses.dataclass
class Attrs:
    """
    Column attributes relevant for Spotlight.
    """

    # pylint: disable=too-many-instance-attributes

    type_name: str
    type: Type[ColumnType]
    order: Optional[int]
    hidden: bool
    optional: bool
    description: Optional[str]
    tags: List[str]
    editable: bool
    categories: Optional[Dict[str, int]]
    x_label: Optional[str]
    y_label: Optional[str]
    embedding_length: Optional[int]
    has_lookup: bool
    is_external: Optional[bool]


@dataclasses.dataclass
class Column(Attrs):
    """
    Column with raw values.
    """

    name: str
    values: np.ndarray
    references: Optional[np.ndarray]


@dataclass
class CellsUpdate:
    """
    A dataset's cell update.
    """

    value: Any
    author: str
    edited_at: str


class DataSource(ABC):
    """abstract base class for different data sources"""

    @abstractmethod
    def __init__(self, source: Any, dtype: Optional[ColumnTypeMapping]):
        """
        Create Data Source from matching source and dtype mapping.
        """

    @property
    @abstractmethod
    def column_names(self) -> List[str]:
        """
        Dataset's available column names.
        """

    @property
    def df(self) -> Optional[pd.DataFrame]:
        """
        Get the source data as a pandas dataframe if possible
        """
        return None

    @abstractmethod
    def __len__(self) -> int:
        """
        Get the table's length.
        """

    @abstractmethod
    def get_generation_id(self) -> int:
        """
        Get the table's generation ID.
        """

    def check_generation_id(self, generation_id: int) -> None:
        """
        Check if table's generation ID matches to the given one.
        """
        if self.get_generation_id() != generation_id:
            raise GenerationIDMismatch()

    @abstractmethod
    def get_uid(self) -> str:
        """
        Get the table's unique ID.
        """

    @abstractmethod
    def get_name(self) -> str:
        """
        Get the table's human-readable name.
        """

    @abstractmethod
    def get_columns(self, column_names: Optional[List[str]] = None) -> List[Column]:
        """
        Get table's columns by names.
        """

    def get_internal_columns(self) -> List[Column]:
        """
        Get internal columns if there are any.
        """
        return []

    @abstractmethod
    def get_column(self, column_name: str, indices: Optional[List[int]]) -> Column:
        """
        return a column with data
        """

    @abstractmethod
    def get_cell_data(self, column_name: str, row_index: int) -> Any:
        """
        return the value of a single cell
        """

    def get_waveform(self, column_name: str, row_index: int) -> Optional[np.ndarray]:
        """
        return the waveform of an audio cell
        """
        blob = self.get_cell_data(column_name, row_index)
        if blob is None:
            return None
        value_hash = hashlib.blake2b(blob.tolist()).hexdigest()
        cache_key = f"waveform-v2:{value_hash}"
        try:
            waveform = cache[cache_key]
            return waveform
        except KeyError:
            ...
        waveform = audio.get_waveform(io.BytesIO(blob))
        cache[cache_key] = waveform
        return waveform

    def replace_cells(
        self, column_name: str, indices: List[int], value: Any
    ) -> CellsUpdate:
        """
        replace multiple cell's value
        """
        raise DatasetNotEditable()

    def delete_column(self, name: str) -> None:
        """
        remove a column from the table
        """
        raise DatasetNotEditable()

    def delete_row(self, index: int) -> None:
        """
        remove a row from the table
        """
        raise DatasetNotEditable()

    def duplicate_row(self, index: int) -> int:
        """
        duplicate a row in the table
        """
        raise DatasetNotEditable()

    def append_column(self, name: str, dtype_name: str) -> Column:
        """
        add a column to the table
        """
        raise DatasetNotEditable()

    def _assert_index_exists(self, index: int) -> None:
        if index < -len(self) or index >= len(self):
            raise NoRowFound(index)

    def _assert_indices_exist(self, indices: List[int]) -> None:
        indices_array = np.array(indices)
        if ((indices_array < -len(self)) | (indices_array >= len(self))).any():
            raise NoRowFound()

    def _assert_column_exists(self, column_name: str) -> None:
        if column_name not in self.column_names:
            raise ColumnNotExistsError(
                f"Column '{column_name}' doesn't exist in the dataset."
            )

    def _assert_column_not_exists(self, column_name: str) -> None:
        if column_name in self.column_names:
            raise ColumnExistsError(
                f"Column '{column_name}' already exists in the dataset."
            )


def _sanitize_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if isinstance(value, (bool, int, float, str, bytes)):
        return value
    try:
        # Assume `value` is a `numpy` object.
        return value.tolist()
    except AttributeError:
        # Try to send `value` as is.
        return value


def sanitize_values(values: Any) -> Any:
    """
    sanitize values for serialization
    e.g. replace inf, -inf and NaN in float data
    """
    # pylint: disable=too-many-return-statements

    if not is_iterable(values):
        return _sanitize_value(values)
    if isinstance(values, list):
        return [sanitize_values(x) for x in values]
    # At the moment, `values` should be a `numpy` array.
    values = cast(np.ndarray, values)
    if issubclass(values.dtype.type, np.inexact):
        return np.where(np.isfinite(values), values, np.array(None)).tolist()
    return values.tolist()


def idx_column(row_count: int) -> Column:
    """create a column containing the index"""
    return Column(
        type_name="int",
        type=int,
        order=None,
        description=None,
        tags=[],
        categories=None,
        x_label=None,
        y_label=None,
        embedding_length=None,
        has_lookup=False,
        is_external=False,
        references=None,
        name="__idx__",
        hidden=True,
        editable=False,
        optional=False,
        values=np.array(range(row_count)),
    )


def last_edited_at_column(row_count: int, value: datetime) -> Column:
    """create a column containing a constant datetime"""
    return Column(
        type_name="datetime",
        type=datetime,
        order=None,
        description=None,
        tags=[],
        categories=None,
        x_label=None,
        y_label=None,
        embedding_length=None,
        has_lookup=False,
        is_external=False,
        references=None,
        name="__last_edited_at__",
        hidden=True,
        editable=False,
        optional=False,
        values=np.array(row_count * [value]),
    )


def last_edited_by_column(row_count: int, value: str) -> Column:
    """create a column containing a constant username"""
    return Column(
        type_name="str",
        type=str,
        order=None,
        description=None,
        tags=[],
        categories=None,
        x_label=None,
        y_label=None,
        embedding_length=None,
        has_lookup=False,
        is_external=False,
        references=None,
        name="__last_edited_by__",
        hidden=True,
        editable=False,
        optional=False,
        values=np.array(row_count * [value]),
    )


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
        value = np.void(cache[cache_key])
        return value
    except KeyError:
        ...
    value = _decode_external_value(path_or_url, column_type, target_format, workdir)
    cache[cache_key] = value.tolist()
    return value


def _decode_external_value(
    path_or_url: PathOrURLType,
    column_type: Type[FileBasedColumnType],
    target_format: Optional[str] = None,
    workdir: PathType = ".",
) -> np.void:
    """
    Decode an external value as expected by the rest of the backend.
    """
    # pylint: disable=too-many-return-statements
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
    data_class = column_type.from_file(path_or_url)
    return data_class.encode(target_format)
