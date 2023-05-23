"""
    This module provides all backend code.
    Based on FastAPI
"""

import os
from pathlib import Path
from typing import Any, Type, Union, Optional, Dict, Callable

import pandas as pd

from ..dtypes.typing import ColumnTypeMapping
from ..typing import is_pathtype

from .data_source import DataSource
from .exceptions import InvalidDataSource

data_sources: Dict[Union[str, Type], Type[DataSource]] = {}


def add_datasource(source: Union[str, Type], klass: Type[DataSource]) -> None:
    """
    Add a datasource for the given file extension or type
    """
    data_sources[source] = klass


def datasource(
    source: Union[str, Type]
) -> Callable[[Type[DataSource]], Type[DataSource]]:
    """
    Decorator to add a data source.
    See `add_datasource`
    """

    def func(klass: Type[DataSource]) -> Type[DataSource]:
        add_datasource(source, klass)
        return klass

    return func


def create_datasource(
    source: Union[pd.DataFrame, os.PathLike, str],
    dtype: Optional[ColumnTypeMapping] = None,
) -> DataSource:
    """
    open the specified data source
    """

    key: Any = None
    if is_pathtype(source):
        key = Path(source).suffix
    else:
        key = type(source)

    try:
        data_source = data_sources[key]
    except KeyError as e:
        raise InvalidDataSource() from e

    return data_source(source, dtype)
