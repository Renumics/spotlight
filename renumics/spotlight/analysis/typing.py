"""
Shared types for data analysis
"""

from typing import Callable, Iterable, List, Literal, Optional

from pydantic.dataclasses import dataclass

from renumics.spotlight.data_store import DataStore

Severity = Literal["low", "medium", "high"]


@dataclass
class DataIssue:
    """
    An Issue affecting multiple rows of the dataset
    """

    title: str
    rows: List[int]
    severity: Severity = "medium"
    columns: Optional[List[str]] = None
    description: str = ""


DataAnalyzer = Callable[[DataStore, List[str]], Iterable[DataIssue]]
