"""provides access to different data sources (h5, pandas, etc.)"""

import dataclasses
import hashlib
import io
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Type, Any, Union, cast

import pandas as pd
import numpy as np
from pydantic.dataclasses import dataclass

from renumics.spotlight.io import audio
from renumics.spotlight.typing import is_iterable
from renumics.spotlight.dataset.exceptions import (
    ColumnExistsError,
    ColumnNotExistsError,
)
from renumics.spotlight.dtypes.typing import (
    ColumnType,
    ColumnTypeMapping,
)
from renumics.spotlight.dtypes.conversion import ConvertedValue, NormalizedValue
from renumics.spotlight.cache import external_data_cache
from .exceptions import GenerationIDMismatch, NoRowFound


@dataclasses.dataclass
class ColumnMetadata:
    """
    Extra column infos.
    """

    nullable: bool
    editable: bool
    description: Optional[str] = None
    tags: List[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class Attrs:
    """
    Column attributes relevant for Spotlight.
    """

    type: Type[ColumnType]
    order: Optional[int]
    hidden: bool
    optional: bool
    description: Optional[str]
    tags: List[str]
    editable: bool

    # data type specific fields
    categories: Optional[Dict[str, int]]
    x_label: Optional[str]
    y_label: Optional[str]
    embedding_length: Optional[int]


@dataclasses.dataclass
class Column(Attrs):
    """
    Column with raw values.
    """

    name: str
    values: Union[np.ndarray, List[ConvertedValue]]


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
    def __init__(self, source: Any):
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
    def guess_dtypes(self) -> ColumnTypeMapping:
        """
        Guess data source's dtypes.
        """

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
    def get_column_values(self, column_name: str) -> np.ndarray:
        """
        Get normalized values of a column.
        """

    @abstractmethod
    def get_column_metadata(self, column_name: str) -> ColumnMetadata:
        """
        Get extra info of a column.
        """

    @abstractmethod
    def get_cell_value(self, column_name: str, row_index: int) -> NormalizedValue:
        """
        Get normalized value of a single cell.
        """

    def get_waveform(self, column_name: str, row_index: int) -> Optional[np.ndarray]:
        """
        return the waveform of an audio cell
        """
        # TODO: move out of datasource
        # blob = self.get_cell_value(column_name, row_index, Audio)
        blob = None
        if blob is None:
            return None
        if isinstance(blob, np.void):
            blob = blob.tolist()
        value_hash = hashlib.blake2b(blob).hexdigest()
        cache_key = f"waveform-v2:{value_hash}"
        try:
            waveform = external_data_cache[cache_key]
            return waveform
        except KeyError:
            ...
        waveform = audio.get_waveform(io.BytesIO(blob))
        external_data_cache[cache_key] = waveform
        return waveform

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

    if not is_iterable(values):
        return _sanitize_value(values)
    if isinstance(values, list):
        return [sanitize_values(x) for x in values]
    # At the moment, `values` should be a `numpy` array.
    values = cast(np.ndarray, values)
    if issubclass(values.dtype.type, np.inexact):
        return np.where(np.isfinite(values), values, np.array(None)).tolist()
    return values.tolist()
