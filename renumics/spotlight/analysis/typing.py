"""
Shared types for data analysis
"""

from typing import Callable, Iterable, List, Literal, Optional

from pydantic import BaseModel

from renumics.spotlight.backend.data_source import DataSource
from renumics.spotlight.dtypes.typing import ColumnTypeMapping


class DataIssue(BaseModel):
    """
    An Issue affecting multiple rows of the dataset
    """

    severity: Literal["low", "medium", "high"] = "medium"
    title: str
    rows: List[int]
    columns: Optional[List[str]] = None
    description: str = ""


DataAnalyzer = Callable[[DataSource, ColumnTypeMapping], Iterable[DataIssue]]
