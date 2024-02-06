"""
Dataset Analysis
"""

import importlib
import pkgutil
from typing import List

from renumics.spotlight.data_store import DataStore
from renumics.spotlight.logging import logger

from . import analyzers as analyzers_namespace
from .registry import registered_analyzers
from .typing import DataIssue

# import all modules in .analyzers
for module_info in pkgutil.iter_modules(analyzers_namespace.__path__):
    importlib.import_module(analyzers_namespace.__name__ + "." + module_info.name)


def find_issues(data_store: DataStore, columns: List[str]) -> List[DataIssue]:
    """
    Find dataset issues in the data source
    """

    logger.info("Analysis started.")

    issues: List[DataIssue] = []
    for analyze in registered_analyzers:
        issues.extend(analyze(data_store, columns))

    logger.info("Analysis done.")

    return issues
