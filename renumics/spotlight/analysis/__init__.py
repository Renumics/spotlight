"""
Dataset Analysis
"""

from typing import List

from renumics.spotlight.backend import DataSource
from renumics.spotlight.dtypes.typing import ColumnTypeMapping

from .typing import DataIssue
from .registry import registered_analyzers

# import the actual analyzers to let them register themselves
from . import outliers
from . import images


def find_issues(data_source: DataSource, dtypes: ColumnTypeMapping) -> List[DataIssue]:
    """
    Find dataset issues in the data source
    """

    issues: List[DataIssue] = []
    for analyze in registered_analyzers:
        issues.extend(analyze(data_source, dtypes))

    return issues