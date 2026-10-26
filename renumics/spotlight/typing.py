"""
Common types and type guards.
"""

import os
from collections.abc import Iterable
from typing import IO, Any, TypeAlias, TypeGuard

import numpy as np

BoolType: TypeAlias = bool | np.bool_
IntType: TypeAlias = int | np.integer
FloatType: TypeAlias = float | np.floating
NumberType: TypeAlias = IntType | FloatType

PathType: TypeAlias = str | os.PathLike
PathOrUrlType: TypeAlias = str | os.PathLike
FileType: TypeAlias = PathOrUrlType | IO

IndexType: TypeAlias = int | np.integer
Indices1dType: TypeAlias = (
    slice | list[int] | list[np.integer] | list[bool] | list[np.bool_] | np.ndarray
)


def is_bool(x: Any) -> TypeGuard[bool | np.bool_]:
    """
    Check whether `x` is boolean.
    """
    return isinstance(x, (bool, np.bool_))


def is_integer(x: Any) -> TypeGuard[int | np.integer]:
    """
    Check whether `x` is integer.
    """
    return isinstance(x, (int, np.integer))


def is_iterable(x: Any) -> TypeGuard[Iterable]:
    """
    Check whether `x` is iterable. Strings and bytes are considered as
    non-iterable.
    """
    if isinstance(x, (str, bytes)):
        return False
    try:
        iter(x)
    except TypeError:
        return False
    return True


def is_pathtype(x: Any) -> TypeGuard[PathType]:
    """
    Check wether `x` is any PathType.
    """
    if isinstance(x, (str, os.PathLike)):
        return True
    return False
