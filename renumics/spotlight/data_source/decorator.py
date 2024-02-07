from typing import Callable, Type, Union

from .data_source import DataSource
from .registry import add_datasource


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
