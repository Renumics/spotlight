"""
Shared types for data analysis
"""

from typing import Callable, Iterable, List, Union, Literal

from pydantic import BaseModel  # pylint: disable=no-name-in-module

from renumics.spotlight.backend.data_source import DataSource
from renumics.spotlight.dtypes.typing import ColumnTypeMapping


class DataIssue(BaseModel):
    """
    A Problem affecting multiple rows of the dataset
    """

    # pylint: disable=too-few-public-methods
    severity: Union[Literal["warning"], Literal["error"]]
    description: str
    rows: List[int]


DataAnalyzer = Callable[[DataSource, ColumnTypeMapping], Iterable[DataIssue]]
