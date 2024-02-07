"""
Helper for conversion between H5 dataset and `pandas.DataFrame`.
"""

import os.path
import statistics
from typing import Any, Optional, Sequence, Union

import filetype
import numpy as np
import pandas as pd
import PIL.Image
import trimesh

from renumics.spotlight import dtypes
from renumics.spotlight.io import prepare_hugging_face_dict, try_literal_eval
from renumics.spotlight.media import Audio, Embedding, Image, Mesh, Sequence1D, Video
from renumics.spotlight.typing import is_iterable, is_pathtype

from .exceptions import InvalidDTypeError


def create_typed_series(
    dtype: dtypes.DType, values: Optional[Union[Sequence, np.ndarray]] = None
) -> pd.Series:
    if dtypes.is_category_dtype(dtype):
        if values is None or len(values) == 0:
            return pd.Series(
                dtype=pd.CategoricalDtype(
                    [] if not dtype.categories else list(dtype.categories.keys())
                )
            )
        if dtype.inverted_categories is None:
            return pd.Series([None] * len(values), dtype=pd.CategoricalDtype())
        return pd.Series(
            [dtype.inverted_categories.get(code) for code in values],
            dtype=pd.CategoricalDtype(),
        )
    if dtypes.is_bool_dtype(dtype):
        pandas_dtype = "boolean"
    elif dtypes.is_int_dtype(dtype):
        pandas_dtype = "Int64"
    elif dtypes.is_float_dtype(dtype):
        pandas_dtype = "float"
    elif dtypes.is_str_dtype(dtype):
        pandas_dtype = "string"
    elif dtypes.is_datetime_dtype(dtype):
        pandas_dtype = "datetime64[ns]"
    else:
        pandas_dtype = "object"
    return pd.Series([] if values is None else values, dtype=pandas_dtype)


def prepare_column(column: pd.Series, dtype: dtypes.DType) -> pd.Series:
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

    if dtypes.is_category_dtype(dtype):
        # We only support string/`NA` categories, but `pandas` can more, so
        # force categories to be strings (does not affect `NA`s).
        return to_categorical(column, str_categories=True)

    if dtypes.is_datetime_dtype(dtype):
        # `errors="coerce"` will produce `NaT`s instead of fail.
        return pd.to_datetime(column, errors="coerce")

    if dtypes.is_str_dtype(dtype):
        # Allow `NA`s, convert all other elements to strings.
        return column.astype(str).mask(column.isna(), None)  # type: ignore

    if dtypes.is_bool_dtype(dtype):
        return column.astype(bool)

    if dtypes.is_int_dtype(dtype):
        return column.astype(int)

    if dtypes.is_float_dtype(dtype):
        return column.astype(float)

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

        if dtypes.is_filebased_dtype(dtype):
            dict_mask = column.map(type) == dict
            column[dict_mask] = column[dict_mask].apply(prepare_hugging_face_dict)

    return column.mask(na_mask, None)  # type: ignore


def infer_dtype(column: pd.Series) -> dtypes.DType:
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

    Raises:
        ValueError: If dtype cannot be inferred automatically.
    """

    if pd.api.types.is_bool_dtype(column):
        return dtypes.bool_dtype
    if pd.api.types.is_categorical_dtype(column):
        return dtypes.CategoryDType(
            {category: code for code, category in enumerate(column.cat.categories)}
        )
    if pd.api.types.is_integer_dtype(column):
        return dtypes.int_dtype
    if pd.api.types.is_float_dtype(column):
        return dtypes.float_dtype
    if pd.api.types.is_datetime64_any_dtype(column):
        return dtypes.datetime_dtype

    column = column.copy()
    str_mask = is_string_mask(column)
    column[str_mask] = column[str_mask].replace("", None)

    column = column[~column.isna()]
    if len(column) == 0:
        return dtypes.str_dtype

    column_head = column.iloc[:10]
    head_dtypes = column_head.apply(infer_value_dtype).to_list()  # type: ignore
    dtype_mode = statistics.mode(head_dtypes)

    if dtype_mode is None:
        return dtypes.str_dtype
    if dtype_mode in [dtypes.window_dtype, dtypes.embedding_dtype]:
        column = column.astype(object)
        str_mask = is_string_mask(column)
        x = column[str_mask].apply(try_literal_eval)
        column[str_mask] = x
        dict_mask = column.map(type) == dict
        column[dict_mask] = column[dict_mask].apply(prepare_hugging_face_dict)
        try:
            np.asarray(column.to_list(), dtype=float)
        except (TypeError, ValueError):
            return dtypes.sequence_1d_dtype
        return dtype_mode
    return dtype_mode


def infer_value_dtype(value: Any) -> Optional[dtypes.DType]:
    """
    Infer dtype for value
    """
    if isinstance(value, Embedding):
        return dtypes.embedding_dtype
    if isinstance(value, Sequence1D):
        return dtypes.sequence_1d_dtype
    if isinstance(value, Image):
        return dtypes.image_dtype
    if isinstance(value, Audio):
        return dtypes.audio_dtype
    if isinstance(value, Video):
        return dtypes.video_dtype
    if isinstance(value, Mesh):
        return dtypes.mesh_dtype
    if isinstance(value, PIL.Image.Image):
        return dtypes.image_dtype
    if isinstance(value, trimesh.Trimesh):
        return dtypes.mesh_dtype
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
                return dtypes.image_dtype
            if mime_group == "audio":
                return dtypes.audio_dtype
            if mime_group == "video":
                return dtypes.video_dtype
        return None
    if is_iterable(value):
        try:
            value = np.asarray(value, dtype=float)
        except (TypeError, ValueError):
            pass
        else:
            return infer_array_dtype(value)
    return None


def infer_array_dtype(value: np.ndarray) -> dtypes.DType:
    """
    Infer dtype of a numpy array
    """
    if value.ndim == 3:
        if value.shape[-1] in (1, 3, 4):
            return dtypes.image_dtype
    elif value.ndim == 2:
        if value.shape[0] == 2 or value.shape[1] == 2:
            return dtypes.sequence_1d_dtype
    elif value.ndim == 1:
        if len(value) == 2:
            return dtypes.window_dtype
        return dtypes.embedding_dtype
    return dtypes.array_dtype


def infer_dtypes(df: pd.DataFrame, dtype: Optional[dtypes.DTypeMap]) -> dtypes.DTypeMap:
    """
    Check column types from the given `dtype` and complete it with auto inferred
    column types for the given `pandas.DataFrame`.
    """
    inferred_dtype = dtype or {}
    for column_index in df:
        if column_index not in inferred_dtype:
            try:
                column_type = infer_dtype(df[column_index])
            except InvalidDTypeError:
                column_type = dtypes.str_dtype
            inferred_dtype[str(column_index)] = column_type
    return inferred_dtype


def is_string_mask(column: pd.Series) -> pd.Series:
    """
    Return mask of column's elements of type string.
    """
    if len(column) == 0:
        return pd.Series([], dtype=bool)
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
