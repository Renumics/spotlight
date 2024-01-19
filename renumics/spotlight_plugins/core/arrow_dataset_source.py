from typing import List, Union

import numpy as np

import renumics.spotlight.dtypes as spotlight_dtypes
from renumics.spotlight.data_source import DataSource
from renumics.spotlight.data_source.decorator import datasource
from renumics.spotlight.data_source.data_source import ColumnMetadata


@datasource(int)
class ArrowDatasetSource(DataSource):
    def __init__(self, source: int):
        self._dataset = source
        self._intermediate_dtypes: spotlight_dtypes.DTypeMap = {}
        self._semantic_dtypes: spotlight_dtypes.DTypeMap = {}

    @property
    def column_names(self) -> List[str]:
        return []

    @property
    def intermediate_dtypes(self) -> spotlight_dtypes.DTypeMap:
        return self._intermediate_dtypes

    def __len__(self) -> int:
        return 0

    @property
    def semantic_dtypes(self) -> spotlight_dtypes.DTypeMap:
        return self._semantic_dtypes

    def get_generation_id(self) -> int:
        return 0

    def get_uid(self) -> str:
        return ""

    def get_name(self) -> str:
        return "Arrow Dataset"

    def get_column_values(
        self,
        column_name: str,
        indices: Union[List[int], np.ndarray, slice] = slice(None),
    ) -> np.ndarray:
        return np.ndarray([])

    def get_column_metadata(self, _: str) -> ColumnMetadata:
        return ColumnMetadata(nullable=True, editable=False)
