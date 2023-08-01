"""
access pandas DataFrame table data
"""
from datetime import datetime
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union, Type, cast

import numpy as np
import pandas as pd
import trimesh

from renumics.spotlight.dtypes import (
    Audio,
    Category,
    Embedding,
    Image,
    Mesh,
    Sequence1D,
    Video,
    Window,
)
from renumics.spotlight.dtypes.exceptions import InvalidFile, NotADType
from renumics.spotlight.dtypes.typing import (
    ColumnType,
    ColumnTypeMapping,
    is_array_based_column_type,
    is_file_based_column_type,
    is_scalar_column_type,
)
from renumics.spotlight.io.pandas import (
    infer_dtype,
    is_empty,
    prepare_column,
    prepare_hugging_face_dict,
    stringify_columns,
    to_categorical,
    try_literal_eval,
)
from renumics.spotlight.backend import datasource
from renumics.spotlight.backend.data_source import (
    Column,
    DataSource,
)
from renumics.spotlight.backend.exceptions import (
    ConversionFailed,
    DatasetColumnsNotUnique,
)
from renumics.spotlight.typing import PathType, is_pathtype
from renumics.spotlight.dataset.exceptions import ColumnNotExistsError

from renumics.spotlight.dtypes.conversion import read_external_value


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
        self._df = df.copy()

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

    def get_generation_id(self) -> int:
        return self._generation_id

    def get_uid(self) -> str:
        return self._uid

    def get_name(self) -> str:
        return "pd.DataFrame"

    def get_column(
        self,
        column_name: str,
        dtype: Type[ColumnType],
        indices: Optional[List[int]] = None,
        simple: bool = False,
    ) -> Column:
        column_index = self._parse_column_index(column_name)

        column = self._df[column_index]
        if indices is not None:
            column = column.iloc[indices]
        column = prepare_column(column, dtype)

        categories = None
        embedding_length = None

        if dtype is Category:
            # `NaN` category is listed neither in `pandas`, not in our format.
            categories = {
                category: i for i, category in enumerate(column.cat.categories)
            }
            column = column.cat.codes
            values = column.to_numpy()
        elif dtype is datetime:
            # We expect datetimes as ISO strings; empty strings instead of `NaT`s.
            column = column.dt.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
            column = column.mask(column.isna(), "")
            values = column.to_numpy()
        elif dtype is str:
            # Replace `NA`s with empty strings.
            column = column.mask(column.isna(), "")
            values = column.to_numpy()
            if simple:
                values = np.array(
                    [
                        value[:97] + "..." if len(value) > 100 else value
                        for value in values
                    ]
                )
        elif is_scalar_column_type(dtype):
            values = column.to_numpy()
        elif dtype is Window:
            # Replace all `NA` values with `[NaN, NaN]`.
            na_mask = column.isna()
            column.iloc[na_mask] = pd.Series(
                [[float("nan"), float("nan")]] * na_mask.sum()
            )
            # This will fail, if arrays in column cells aren't aligned.
            try:
                values = np.asarray(column.to_list(), dtype=float)
            except ValueError as e:
                raise ValueError(
                    f"For the window column '{column_name}', column cells "
                    f"should be sequences of shape (2,) or `NA`s, but "
                    f"unaligned sequences received."
                ) from e
            if values.ndim != 2 or values.shape[1] != 2:
                raise ValueError(
                    f"For the window column '{column_name}', column cells "
                    f"should be sequences of shape (2,) or `NA`s, but "
                    f"sequences of shape {values.shape[1:]} received."
                )
        elif dtype is Embedding:
            na_mask = column.isna()
            # This will fail, if arrays in column cells aren't aligned.
            try:
                embeddings = np.asarray(column[~na_mask].to_list(), dtype=float)
            except ValueError as e:
                raise ValueError(
                    f"For the embedding column '{column_name}', column cells "
                    f"should be sequences of the same shape (n,) or `NA`s, but "
                    f"unaligned sequences received."
                ) from e
            if embeddings.ndim != 2 or embeddings.shape[1] == 0:
                raise ValueError(
                    f"For the embedding column '{column_name}', column cells "
                    f"should be sequences of the same shape (n,) or `NA`s, but "
                    f"sequences of shape {embeddings.shape[1:]} received."
                )

            values = np.empty(len(column), dtype=object)

            if simple:
                values[~na_mask] = "[...]"
            else:
                values[np.where(~na_mask)[0]] = list(embeddings)

            embedding_length = embeddings.shape[1]

        elif dtype is Sequence1D:
            na_mask = column.isna()
            values = np.empty(len(column), dtype=object)
            values[~na_mask] = "[...]"
        elif dtype is np.ndarray:
            na_mask = column.isna()
            values = np.empty(len(column), dtype=object)
            values[~na_mask] = "[...]"
        elif is_file_based_column_type(dtype):
            # Strings are paths or URLs, let them inplace. Replace
            # non-strings with "<in-memory>".
            na_mask = column.isna()
            column = column.mask(~(column.map(type) == str), "<in-memory>")
            values = column.to_numpy(dtype=object)
            values[na_mask] = None
        else:
            raise NotADType()

        return Column(
            type=dtype,
            order=None,
            hidden=column_name.startswith("_"),
            optional=True,
            description=None,
            tags=[],
            editable=dtype in (bool, int, float, str, Category, Window),
            categories=categories,
            x_label=None,
            y_label=None,
            embedding_length=embedding_length,
            name=column_name,
            values=values,
        )

    def get_cell_data(
        self, column_name: str, row_index: int, dtype: Type[ColumnType]
    ) -> Any:
        """
        Return the value of a single cell, warn if not possible.
        """

        self._assert_index_exists(row_index)

        column_index = self._parse_column_index(column_name)

        raw_value = self._df.iloc[row_index, self._df.columns.get_loc(column_index)]

        if dtype is Category:
            if pd.isna(raw_value):
                return -1
            categories = self._get_column_categories(column_index, as_string=True)
            return categories.get(raw_value, -1)
        if dtype is datetime:
            value = pd.to_datetime(raw_value).to_numpy("datetime64[us]").tolist()
            # `tolist()` returns `None` for all `NaT`s, `datetime` otherwise.
            if value is None:
                return ""
            return value.isoformat()
        if dtype is str:
            if pd.isna(raw_value):
                return ""
            return str(raw_value)
        if is_scalar_column_type(dtype):
            # `dtype` is `bool`, `int` or `float`.
            dtype = cast(Type[Union[bool, int, float]], dtype)
            try:
                return dtype(raw_value)
            except (TypeError, ValueError) as e:
                raise ConversionFailed(dtype, raw_value) from e
        if dtype is np.ndarray:
            if isinstance(raw_value, str):
                raw_value = try_literal_eval(raw_value)
            if is_empty(raw_value):
                return None
            return np.asarray(raw_value)
        if dtype is Window:
            if isinstance(raw_value, str):
                raw_value = try_literal_eval(raw_value)
            if is_empty(raw_value):
                return np.full(2, np.nan)
            try:
                value = np.asarray(raw_value, dtype=float)
            except (TypeError, ValueError) as e:
                raise ConversionFailed(dtype, raw_value) from e
            if value.ndim != 1 or len(value) != 2:
                raise ValueError(
                    f"Window column cells should be sequences of shape (2,), "
                    f"but a sequence of shape {value.shape} received for the "
                    f"column '{column_name}'."
                )
        if is_empty(raw_value):
            return None
        if isinstance(raw_value, str):
            raw_value = try_literal_eval(raw_value)
        if is_file_based_column_type(dtype) and isinstance(raw_value, dict):
            raw_value = prepare_hugging_face_dict(raw_value)
        if isinstance(raw_value, trimesh.Trimesh) and dtype is Mesh:
            value = Mesh.from_trimesh(raw_value)
            return value.encode()
        if isinstance(raw_value, str) and is_file_based_column_type(dtype):
            try:
                return read_external_value(str(raw_value), dtype)
            except Exception as e:
                raise ConversionFailed(dtype, raw_value) from e
        if isinstance(raw_value, bytes) and dtype in (Audio, Image, Video):
            try:
                value = dtype.from_bytes(raw_value)  # type: ignore
            except Exception as e:
                raise ConversionFailed(dtype, raw_value) from e
            return value.encode()
        if not isinstance(raw_value, dtype) and is_array_based_column_type(dtype):
            try:
                value = dtype(raw_value)
            except (InvalidFile, TypeError, ValueError) as e:
                raise ConversionFailed(dtype, raw_value) from e
            return value.encode()
        if isinstance(raw_value, dtype):
            return raw_value.encode()
        raise ConversionFailed(dtype, raw_value)

    def _get_default_value(self, dtype: Type[ColumnType]) -> Any:
        if dtype is int:
            return 0
        if dtype is bool:
            return False
        if dtype is str:
            return ""
        if dtype is Window:
            return [float("nan"), float("nan")]
        # `dtype` is `float`, `datetime`, `np.ndarray`, or a custom data type.
        return np.nan

    @lru_cache(maxsize=128)
    def _get_column_categories(
        self, column_index: Any, as_string: bool = False
    ) -> Dict[str, int]:
        """
        Get categories of a categorical column.

        If `as_string` is True, convert the categories to their string
        representation.

        At the moment, there is no way to add a new category in Spotlight, so we
        rely on the previously cached ones.
        """
        column = self._df[column_index]
        column = to_categorical(column, str_categories=as_string)
        return {category: i for i, category in enumerate(column.cat.categories)}
