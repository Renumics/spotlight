"""
A decorator for data analysis functions
"""

from .typing import DataAnalyzer
from .registry import register_analyzer


def data_analyzer(func: DataAnalyzer) -> DataAnalyzer:
    """
    register a data analysis function
    """
    register_analyzer(func)
    return func
