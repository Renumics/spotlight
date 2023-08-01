"""
This module contains helpers for importing `pandas.DataFrame`s.
"""

import ast
import os.path
import statistics
from contextlib import suppress
from datetime import datetime
from typing import Any, Dict, List, Optional, Type

import PIL.Image
import filetype
import trimesh
import numpy as np
import pandas as pd

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
from renumics.spotlight.dtypes.exceptions import NotADType, UnsupportedDType
from renumics.spotlight.dtypes.typing import (
    COLUMN_TYPES_BY_NAME,
    ColumnType,
    ColumnTypeMapping,
    is_column_type,
    is_file_based_column_type,
    is_scalar_column_type,
)
from renumics.spotlight.typing import is_iterable, is_pathtype
from renumics.spotlight.dtypes.base import DType


def is_empty(value: Any) -> bool:
    """
    Check if value is `NA` or an empty string.
    """
    if is_iterable(value):
        # `pd.isna` with an iterable argument returns an iterable result. But
        # an iterable cannot be NA or empty string by default.
        return False
    return pd.isna(value) or value == ""


def try_literal_eval(x: str) -> Any:
    """
    Try to evaluate a literal expression, otherwise return value as is.
    """
    with suppress(Exception):
        return ast.literal_eval(x)
    return x


def stringify_columns(df: pd.DataFrame) -> List[str]:
    """
    Convert `pandas.DataFrame`'s column names to strings, no matter which index
    is used.
    """
    return [str(column_name) for column_name in df.columns]


def infer_dtype(column: pd.Series) -> Type[ColumnType]:
    """
    Get an equivalent Spotlight data type for a `pandas` column, if possible.

    At the moment, only scalar data types can be inferred.

    Nullable boolean and integer `pandas` dtypes have no equivalent Spotlight
    data type and will be read as strings.

    Float, string, and category data types are allowed to have `NaN`s.

    Args:
        column: A `pandas` column to infer dtype from.

    Returns:
        Inferred dtype.

    Reises:
        ValueError: If dtype cannot be inferred automatically.
    """

    if pd.api.types.is_bool_dtype(column) and not column.hasnans:
        return bool
    if pd.api.types.is_categorical_dtype(column):
        return Category
    if pd.api.types.is_integer_dtype(column) and not column.hasnans:
        return int
    if pd.api.types.is_float_dtype(column):
        return float
    if pd.api.types.is_datetime64_any_dtype(column):
        return datetime

    column = column.copy()
    str_mask = is_string_mask(column)
    column[str_mask] = column[str_mask].replace("", None)

    column = column[~column.isna()]
    if len(column) == 0:
        return str

    column_head = column.iloc[:10]
    head_dtypes = column_head.apply(infer_value_dtype).to_list()  # type: ignore
    dtype_mode = statistics.mode(head_dtypes)

    if dtype_mode is None:
        return str
    if issubclass(dtype_mode, (Window, Embedding)):
        str_mask = is_string_mask(column)
        column[str_mask] = column[str_mask].apply(try_literal_eval)
        dict_mask = column.map(type) == dict
        column[dict_mask] = column[dict_mask].apply(prepare_hugging_face_dict)
        try:
            np.asarray(column.to_list(), dtype=float)
        except (TypeError, ValueError):
            return Sequence1D
        return dtype_mode
    return dtype_mode


def infer_array_dtype(value: np.ndarray) -> Type[ColumnType]:
    """
    Infer dtype of a numpy array
    """
    if value.ndim == 3:
        if value.shape[-1] in (1, 3, 4):
            return Image
    elif value.ndim == 2:
        if value.shape[0] == 2 or value.shape[1] == 2:
            return Sequence1D
    elif value.ndim == 1:
        if len(value) == 2:
            return Window
        return Embedding
    return np.ndarray


def infer_value_dtype(value: Any) -> Optional[Type[ColumnType]]:
    """
    Infer dtype for value
    """

    if isinstance(value, DType):
        return type(value)
    if isinstance(value, PIL.Image.Image):
        return Image
    if isinstance(value, trimesh.Trimesh):
        return Mesh
    if isinstance(value, np.ndarray):
        return infer_array_dtype(value)

    # When `pandas` reads a csv, arrays and lists are read as literal strings,
    # try to interpret them.
    value = try_literal_eval(value)
    if isinstance(value, dict):
        value = prepare_hugging_face_dict(value)
    if isinstance(value, bytes) or (is_pathtype(value) and os.path.isfile(value)):
        kind = filetype.guess(value)
        if kind is not None:
            mime_group = kind.mime.split("/")[0]
            if mime_group == "image":
                return Image
            if mime_group == "audio":
                return Audio
            if mime_group == "video":
                return Video
        return None
    if is_iterable(value):
        try:
            value = np.asarray(value, dtype=float)
        except (TypeError, ValueError):
            pass
        else:
            return infer_array_dtype(value)
    return None


def infer_dtypes(
    df: pd.DataFrame, dtype: Optional[ColumnTypeMapping]
) -> ColumnTypeMapping:
    """
    Check column types from the given `dtype` and complete it with auto inferred
    column types for the given `pandas.DataFrame`.
    """
    inferred_dtype = dtype or {}
    for column_name, column_type in inferred_dtype.items():
        if not is_column_type(column_type):
            raise NotADType(
                f"Given column type {column_type} for column '{column_name}' "
                f"is not a valid Spotlight column type."
            )
    for column_index in df:
        if column_index not in inferred_dtype:
            try:
                column_type = infer_dtype(df[column_index])
            except UnsupportedDType:
                column_type = str
            inferred_dtype[str(column_index)] = column_type
    return inferred_dtype


def is_string_mask(column: pd.Series) -> pd.Series:
    """
    Return mask of column's elements of type string.
    """
    return column.map(type) == str


def to_categorical(column: pd.Series, str_categories: bool = False) -> pd.Series:
    """
    Convert a `pandas` column to categorical dtype.

    Args:
        column: A `pandas` column.
        str_categories: Replace all categories with their string representations.

    Returns:
        categorical `pandas` column.
    """
    column = column.mask(column.isna(), None).astype("category")  # type: ignore
    if str_categories:
        return column.cat.rename_categories(column.cat.categories.astype(str))
    return column


def prepare_hugging_face_dict(x: Dict) -> Any:
    """
    Prepare HuggingFace format for files to be used in Spotlight.
    """
    if x.keys() != {"bytes", "path"}:
        return x
    blob = x["bytes"]
    if blob is not None:
        return blob
    return x["path"]


def prepare_column(column: pd.Series, dtype: Type[ColumnType]) -> pd.Series:
    """
    Convert a `pandas` column to the desired `dtype` and prepare some values,
    but still as `pandas` column.

    Args:
        column: A `pandas` column to prepare.
        dtype: Target data type.

    Returns:
        Prepared `pandas` column.

    Raises:
        TypeError: If `dtype` is not a Spotlight data type.
    """
    column = column.copy()

    if dtype is Category:
        # We only support string/`NA` categories, but `pandas` can more, so
        # force categories to be strings (does not affect `NA`s).
        return to_categorical(column, str_categories=True)

    if dtype is datetime:
        # `errors="coerce"` will produce `NaT`s instead of fail.
        return pd.to_datetime(column, errors="coerce")

    if dtype is str:
        # Allow `NA`s, convert all other elements to strings.
        return column.astype(str).mask(column.isna(), None)  # type: ignore

    if is_scalar_column_type(dtype):
        # `dtype` is `bool`, `int` or `float`.
        return column.astype(dtype)

    if not is_column_type(dtype):
        raise NotADType(
            "`dtype` should be one of Spotlight data types ("
            + ", ".join(COLUMN_TYPES_BY_NAME.keys())
            + f"), but {dtype} received."
        )

    # We explicitely don't want to change the original `DataFrame`.
    with pd.option_context("mode.chained_assignment", None):
        # We consider empty strings as `NA`s.
        str_mask = is_string_mask(column)
        column[str_mask] = column[str_mask].replace("", None)
        na_mask = column.isna()

        # When `pandas` reads a csv, arrays and lists are read as literal strings,
        # try to interpret them.
        str_mask = is_string_mask(column)
        column[str_mask] = column[str_mask].apply(try_literal_eval)

        if is_file_based_column_type(dtype):
            dict_mask = column.map(type) == dict
            column[dict_mask] = column[dict_mask].apply(prepare_hugging_face_dict)

    return column.mask(na_mask, None)  # type: ignore
