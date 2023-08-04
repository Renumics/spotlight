from typing import Dict, Union, Type, Any
from pathlib import Path

from renumics.spotlight.typing import is_pathtype
from .data_source import DataSource
from .exceptions import InvalidDataSource

data_sources: Dict[Union[str, Type], Type[DataSource]] = {}


def add_datasource(source: Union[str, Type], klass: Type[DataSource]) -> None:
    """
    Add a datasource for the given file extension or type
    """
    data_sources[source] = klass


def create_datasource(source: Any) -> DataSource:
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

    return data_source(source)
