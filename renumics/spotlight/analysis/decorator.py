"""
A decorator for data analysis functions
"""

from .registry import register_analyzer
from .typing import DataAnalyzer


def data_analyzer(func: DataAnalyzer) -> DataAnalyzer:
    """
    register a data analysis function
    """
    register_analyzer(func)
    return func
