"""
Spotlight Application Config
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union, Any


from renumics.spotlight.layout.nodes import Layout
from renumics.spotlight.analysis.typing import DataIssue
from renumics.spotlight.dtypes import DTypeMap


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
    analyze: Optional[Union[bool, List[str]]] = None
    custom_issues: Optional[List[DataIssue]] = None

    # frontend
    layout: Optional[Layout] = None
    filebrowsing_allowed: Optional[bool] = None
