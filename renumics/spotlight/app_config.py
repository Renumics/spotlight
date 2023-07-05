"""
Spotlight Application Config
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union

import pandas as pd

from renumics.spotlight.layout.nodes import Layout
from renumics.spotlight.analysis.typing import DataIssue
from renumics.spotlight.typing import PathType

from renumics.spotlight.dtypes.typing import ColumnTypeMapping


@dataclass(frozen=True)
class AppConfig:
    """
    Spotlight Application Config
    """

    # dataset
    dataset: Optional[Union[PathType, pd.DataFrame]] = None
    dtypes: Optional[ColumnTypeMapping] = None
    project_root: Optional[Path] = None

    # data analysis
    analyze: Optional[bool] = None
    custom_issues: Optional[List[DataIssue]] = None

    # frontend
    layout: Optional[Layout] = None
    filebrowsing_allowed: Optional[bool] = None
