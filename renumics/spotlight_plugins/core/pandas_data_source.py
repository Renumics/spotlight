"""
access pandas DataFrame table data
"""
from datetime import datetime
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union, Type, cast

import numpy as np
import pandas as pd
import trimesh
from loguru import logger

from renumics.spotlight.dtypes import Category, Embedding, Mesh, Window
from renumics.spotlight.dtypes.exceptions import InvalidFile, UnsupportedDType
from renumics.spotlight.dtypes.typing import (
    ColumnType,
    ColumnTypeMapping,
    get_column_type_name,
    is_array_based_column_type,
    is_file_based_column_type,
    is_scalar_column_type,
)
from renumics.spotlight.io.pandas import (
    infer_dtypes,
    is_empty,
    prepare_column,
    stringify_columns,
    to_categorical,
    try_literal_eval,
)
from renumics.spotlight.backend import datasource
from renumics.spotlight.backend.data_source import (
    Column,
    DataSource,
    read_external_value,
)
from renumics.spotlight.backend.exceptions import (
    ConversionFailed,
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
    _dtype: ColumnTypeMapping
    _inferred_dtype: ColumnTypeMapping

    def __init__(
        self,
        source: Union[PathType, pd.DataFrame],
        dtype: Optional[ColumnTypeMapping] = None,
    ):
        if is_pathtype(source):
            df = pd.read_csv(source)
        else:
            df = source

        if not df.columns.is_unique:
            raise DatasetColumnsNotUnique()
        self._generation_id = 0
        self._uid = str(id(df))
        self._df = df.copy()
        self._dtype = dtype.copy() if dtype else {}
        self._inferred_dtype = infer_dtypes(self._df, self._dtype)

    @property
    def column_names(self) -> List[str]:
        return stringify_columns(self._df)

    @property
    def df(self) -> pd.DataFrame:
        """
        Get **a copy** of the served `DataFrame`.
        """
        return self._df.copy()

    @property
    def dtype(self) -> Optional[ColumnTypeMapping]:
        """
        Get **a copy** of dict with the desired data types.
        """
        if self._dtype is None:
            return None
        return self._dtype.copy()

    def __len__(self) -> int:
        return len(self._df)

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

    def get_columns(self, column_names: Optional[List[str]] = None) -> List[Column]:
        if column_names is None:
            column_names = self.column_names
        columns = []
        for column_name in column_names:
            try:
                column = self.get_column(column_name, None)
            except Exception as e:  # pylint: disable=broad-except
                if column_name in self._dtype:
                    raise e
                logger.warning(
                    f"Column '{column_name}' not imported from "
                    f"`pandas.DataFrame` because of the following error:\n{e}"
                )
            else:
                columns.append(column)

        return columns

    def get_column(self, column_name: str, indices: Optional[List[int]]) -> Column:
        # pylint: disable=too-many-branches, too-many-statements
        column_index = self._parse_column_index(column_name)

        dtype = self._inferred_dtype[column_index]
        column = self._df[column_index]
        if indices is not None:
            column = column.iloc[indices]
        column = prepare_column(column, dtype)

        categories = None
        embedding_length = None
        references = None

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
            if na_mask.any():
                values = np.empty(len(column), dtype=object)
                values[np.where(~na_mask)[0]] = list(embeddings)
            else:
                values = embeddings
            embedding_length = embeddings.shape[1]
        else:
            # A reference column. `dtype` is one of `np.ndarray`, `Audio`,
            # `Image`, `Mesh`, `Sequence1D` or `Video`. Don't try to check or
            # convert values at the moment.
            na_mask = column.isna()
            references = na_mask.to_numpy()
            if is_file_based_column_type(dtype):
                # Strings are paths or URLs, let them inplace. Replace
                # non-strings with empty strings.
                column = column.mask(~(column.map(type) == str), "")
                values = column.to_numpy()
            else:
                values = np.full(len(column), "")
        return Column(
            type_name=get_column_type_name(dtype),
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
            has_lookup=False,
            is_external=False,
            name=column_name,
            values=values,
            references=references,
        )

    def get_cell_data(self, column_name: str, row_index: int) -> Any:
        """
        Return the value of a single cell, warn if not possible.
        """
        # pylint: disable=too-many-return-statements, too-many-branches
        self._assert_index_exists(row_index)

        column_index = self._parse_column_index(column_name)

        raw_value = self._df.iloc[row_index, self._df.columns.get_loc(column_index)]
        dtype = self._inferred_dtype[column_index]

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
        if isinstance(raw_value, trimesh.Trimesh) and dtype is Mesh:
            value = Mesh.from_trimesh(raw_value)
            return value.encode()
        if isinstance(raw_value, str) and is_file_based_column_type(dtype):
            try:
                return read_external_value(str(raw_value), dtype)
            except Exception as e:
                raise ConversionFailed(dtype, raw_value) from e
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
        dtype = self._inferred_dtype[column_index]
        if dtype is not Category:
            raise UnsupportedDType(
                f"Column categories exist for categorical columns only, but "
                f"column '{str(column_index)}' of type {dtype} received."
            )
        column = self._df[column_index]
        column = to_categorical(column, str_categories=as_string)
        return {category: i for i, category in enumerate(column.cat.categories)}
