"""
Manage data analyzers available for spotlights automatic dataset analysis.
"""

from typing import Set

from .typing import DataAnalyzer

registered_analyzers: Set[DataAnalyzer] = set()


def register_analyzer(analyzer: DataAnalyzer) -> None:
    """
    Register a data analyzer
    """
    registered_analyzers.add(analyzer)


def unregister_analyzer(analyzer: DataAnalyzer) -> None:
    """
    Unregister a data analyzer
    """
    registered_analyzers.remove(analyzer)
