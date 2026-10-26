"""
Spotlight Application Config
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from renumics.spotlight.analysis.typing import DataIssue
from renumics.spotlight.dtypes import DTypeMap
from renumics.spotlight.layout.nodes import Layout


@dataclass(frozen=True)
class AppConfig:
    """
    Spotlight Application Config
    """

    # dataset
    dataset: Any = None
    dtypes: DTypeMap | None = None
    project_root: Path | None = None

    # data analysis
    analyze: list[str] | bool | None = None
    custom_issues: list[DataIssue] | None = None

    # embedding
    embed: list[str] | bool | None = None

    # frontend
    layout: Layout | None = None
    filebrowsing_allowed: bool | None = None
