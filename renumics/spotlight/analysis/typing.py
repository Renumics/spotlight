"""
Shared types for data analysis
"""

from collections.abc import Callable, Iterable
from typing import Literal, TypeAlias

from pydantic.dataclasses import dataclass

from renumics.spotlight.data_store import DataStore

Severity: TypeAlias = Literal["low", "medium", "high"]


@dataclass
class DataIssue:
    """
    An Issue affecting multiple rows of the dataset
    """

    title: str
    rows: list[int]
    severity: Severity = "medium"
    columns: list[str] | None = None
    description: str = ""


DataAnalyzer: TypeAlias = Callable[[DataStore, list[str]], Iterable[DataIssue]]
