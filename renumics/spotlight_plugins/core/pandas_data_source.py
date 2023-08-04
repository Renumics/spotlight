"""
access pandas DataFrame table data
"""
from typing import Any, List, Union, cast

import numpy as np
import pandas as pd

from renumics.spotlight.dtypes.typing import (
    ColumnTypeMapping,
)
from renumics.spotlight.io.pandas import (
    infer_dtype,
    prepare_hugging_face_dict,
    stringify_columns,
    try_literal_eval,
)
from renumics.spotlight.data_source import (
    datasource,
    ColumnMetadata,
    DataSource,
)
from renumics.spotlight.backend.exceptions import (
    DatasetColumnsNotUnique,
)
from renumics.spotlight.typing import PathType, is_pathtype
from renumics.spotlight.dataset.exceptions import ColumnNotExistsError


@datasource(pd.DataFrame)
@datasource(".csv")
class PandasDataSource(DataSource):
    """
    access pandas DataFrame table data
    """

    _generation_id: int
    _uid: str
    _df: pd.DataFrame

    def __init__(self, source: Union[PathType, pd.DataFrame]):
        if is_pathtype(source):
            df = pd.read_csv(source)
        else:
            df = cast(pd.DataFrame, source)

        if not df.columns.is_unique:
            raise DatasetColumnsNotUnique()
        self._generation_id = 0
        self._uid = str(id(df))
        self._df = df.convert_dtypes()

    @property
    def column_names(self) -> List[str]:
        return stringify_columns(self._df)

    @property
    def df(self) -> pd.DataFrame:
        """
        Get **a copy** of the served `DataFrame`.
        """
        return self._df.copy()

    def __len__(self) -> int:
        return len(self._df)

    def guess_dtypes(self) -> ColumnTypeMapping:
        dtype_map = {
            str(column_name): infer_dtype(self.df[column_name])
            for column_name in self.df
        }
        return dtype_map

    def get_generation_id(self) -> int:
        return self._generation_id

    def get_uid(self) -> str:
        return self._uid

    def get_name(self) -> str:
        return "pd.DataFrame"

    def get_column_values(self, column_name: str) -> np.ndarray:
        column_index = self._parse_column_index(column_name)
        column = self._df[column_index]
        if pd.api.types.is_bool_dtype(column):
            values = column.to_numpy()
            na_mask = column.isna()
            values[na_mask] = None
            return values
        if pd.api.types.is_integer_dtype(column):
            values = column.to_numpy()
            na_mask = column.isna()
            values[na_mask] = None
            return values
        if pd.api.types.is_float_dtype(column):
            values = column.to_numpy()
            na_mask = column.isna()
            values[na_mask] = None
            return values
        if pd.api.types.is_datetime64_any_dtype(column):
            return column.dt.tz_localize(None).to_numpy()
        if pd.api.types.is_categorical_dtype(column):
            return column.cat.codes
        if pd.api.types.is_string_dtype(column):
            values = column.to_numpy()
            na_mask = column.isna()
            values[na_mask] = None
            return values
        if pd.api.types.is_object_dtype(column):
            column = column.mask(column.isna(), None)
            str_mask = column.map(type) == str
            column[str_mask] = column[str_mask].apply(try_literal_eval)
            dict_mask = column.map(type) == dict
            column[dict_mask] = column[dict_mask].apply(prepare_hugging_face_dict)
            return column.to_numpy()
        try:
            return column.astype(str).to_numpy()
        except (TypeError, ValueError):
            raise TypeError(
                f"`pandas` column with dtype {column.dtype} is not supported."
            )

    def get_column_metadata(self, _: str) -> ColumnMetadata:
        return ColumnMetadata(nullable=True, editable=True)

    def get_cell_value(self, column_name: str, row_index: int) -> Any:
        """
        Return the value of a single cell, warn if not possible.
        """
        # TODO: do this right
        return self.get_column_values(column_name)[row_index]

    def _parse_column_index(self, column_name: str) -> Any:
        column_names = self.column_names
        try:
            loc = self._df.columns.get_loc(column_name)
        except KeyError:
            ...
        else:
            if isinstance(self._df.columns, pd.MultiIndex):
                return self._df.columns[loc][0]
            return self._df.columns[loc]
        try:
            index = column_names.index(column_name)
        except ValueError as e:
            raise ColumnNotExistsError(
                f"Column '{column_name}' doesn't exist in the dataset."
            ) from e
        return self._df.columns[index]
