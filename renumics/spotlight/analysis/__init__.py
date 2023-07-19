"""
Dataset Analysis
"""

import importlib
import pkgutil
from typing import List

from renumics.spotlight.backend import DataSource
from renumics.spotlight.dtypes.typing import ColumnTypeMapping
from renumics.spotlight.logging import logger

from .typing import DataIssue
from .registry import registered_analyzers
from . import analyzers as analyzers_namespace

# import all modules in .analyzers
for module_info in pkgutil.iter_modules(analyzers_namespace.__path__):
    importlib.import_module(analyzers_namespace.__name__ + "." + module_info.name)


def find_issues(data_source: DataSource, dtypes: ColumnTypeMapping) -> List[DataIssue]:
    """
    Find dataset issues in the data source
    """

    logger.info("Analysis started.")

    issues: List[DataIssue] = []
    for analyze in registered_analyzers:
        issues.extend(analyze(data_source, dtypes))

    logger.info("Analysis done.")

    return issues
