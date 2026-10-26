from collections.abc import Callable

from .data_source import DataSource
from .registry import add_datasource


def datasource(
    source: str | type,
) -> Callable[[type[DataSource]], type[DataSource]]:
    """
    Decorator to add a data source.
    See `add_datasource`
    """

    def func(klass: type[DataSource]) -> type[DataSource]:
        add_datasource(source, klass)
        return klass

    return func
