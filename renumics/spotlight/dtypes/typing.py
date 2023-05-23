"""
Spotlight data types' typing.
"""

from datetime import datetime
from typing import Any, Dict, Union, Type

import numpy as np
from typing_extensions import TypeGuard, get_args

from . import Audio, Category, Embedding, Image, Mesh, Sequence1D, Video, Window
from .exceptions import NotADType


ColumnType = Union[
    bool,
    int,
    float,
    str,
    datetime,
    Category,
    Window,
    np.ndarray,
    Audio,
    Embedding,
    Image,
    Mesh,
    Sequence1D,
    Video,
]
ScalarColumnType = Union[bool, int, float, str, datetime, Category]
FileBasedColumnType = Union[Audio, Image, Mesh, Video]
ArrayBasedColumnType = Union[Embedding, Image, Sequence1D]

ColumnTypeMapping = Dict[str, Type[ColumnType]]


COLUMN_TYPES_BY_NAME: Dict[str, Type[ColumnType]] = {
    column_type.__name__: column_type
    for column_type in get_args(ColumnType)
    if column_type is not np.ndarray
}
COLUMN_TYPES_BY_NAME["array"] = np.ndarray
NAME_BY_COLUMN_TYPE: Dict[Type[ColumnType], str] = {
    v: k for k, v in COLUMN_TYPES_BY_NAME.items()
}


def get_column_type_name(column_type: Type[ColumnType]) -> str:
    """
    Get name of a column type as string.
    """
    try:
        return NAME_BY_COLUMN_TYPE[column_type]
    except KeyError as e:
        raise NotADType(f"Unknown column type: {column_type}.") from e


def get_column_type(x: str) -> Type[ColumnType]:
    """
    Get column type by its name.
    """
    try:
        return COLUMN_TYPES_BY_NAME[x]
    except KeyError as e:
        raise NotADType(f"Unknown column type: {x}.") from e


def is_column_type(x: Any) -> TypeGuard[Type[ColumnType]]:
    """
    Check whether `x` is a Spotlight data type class.
    """
    return x in get_args(ColumnType)


def is_scalar_column_type(x: Any) -> TypeGuard[Type[ScalarColumnType]]:
    """
    Check whether `x` is a scalar Spotlight data type class.
    """
    return x in get_args(ScalarColumnType)


def is_file_based_column_type(x: Any) -> TypeGuard[Type[FileBasedColumnType]]:
    """
    Check whether `x` is a Spotlight column type class whose instances
    can be read from/saved into a file.
    """
    return x in get_args(FileBasedColumnType)


def is_array_based_column_type(x: Any) -> TypeGuard[Type[ArrayBasedColumnType]]:
    """
    Check whether `x` is a Spotlight column type class which can be instantiated
    from a single array-like argument.
    """
    return x in get_args(ArrayBasedColumnType)
