"""provides access to different data sources (h5, pandas, etc.)"""

import dataclasses
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Optional, Union

import numpy as np
import pandas as pd

from renumics.spotlight.backend.exceptions import GenerationIDMismatch, NoRowFound
from renumics.spotlight.dataset.exceptions import (
    ColumnExistsError,
    ColumnNotExistsError,
)
from renumics.spotlight.dtypes import DTypeMap


@dataclasses.dataclass
class ColumnMetadata:
    """
    Extra column infos.
    """

    nullable: bool
    editable: bool
    hidden: bool = False
    description: Optional[str] = None
    tags: List[str] = dataclasses.field(default_factory=list)
    computed: bool = False


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
    @abstractmethod
    def intermediate_dtypes(self) -> DTypeMap:
        """
        The dtypes of intermediate values. Values for all columns must be filled.
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

    @property
    @abstractmethod
    def semantic_dtypes(self) -> DTypeMap:
        """
        Semantic dtypes for viewer. Some values may be not present.
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
    def get_column_values(
        self,
        column_name: str,
        indices: Union[List[int], np.ndarray, slice] = slice(None),
    ) -> Iterable:
        """
        Get normalized values of a column.
        """

    @abstractmethod
    def get_column_metadata(self, column_name: str) -> ColumnMetadata:
        """
        Get extra info of a column.
        """

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
