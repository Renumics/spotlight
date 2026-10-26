from pathlib import Path
from typing import Any

from renumics.spotlight.typing import is_pathtype

from .data_source import DataSource
from .exceptions import InvalidDataSource

data_sources: dict[str | type, type[DataSource]] = {}


def add_datasource(source: str | type, klass: type[DataSource]) -> None:
    """
    Add a datasource for the given file extension or type
    """
    data_sources[source] = klass


def create_datasource(source: Any) -> DataSource:
    """
    open the specified data source
    """

    keys: list[Any] = []
    if is_pathtype(source):
        path = Path(source)
        if path.exists():
            keys.append(path.suffix)
            keys.append(Path)

    keys.append(type(source))

    for key in keys:
        try:
            data_source = data_sources[key]
        except KeyError:
            continue
        try:
            return data_source(source)
        except InvalidDataSource:
            continue
    else:
        raise InvalidDataSource()
