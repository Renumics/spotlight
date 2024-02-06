"""
Spotlight Application Config
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional, Union

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
    dtypes: Optional[DTypeMap] = None
    project_root: Optional[Path] = None

    # data analysis
    analyze: Optional[Union[List[str], bool]] = None
    custom_issues: Optional[List[DataIssue]] = None

    # embedding
    embed: Optional[Union[List[str], bool]] = None

    # frontend
    layout: Optional[Layout] = None
    filebrowsing_allowed: Optional[bool] = None
