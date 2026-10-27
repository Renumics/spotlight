"""
Spotlight Datasources fetch and normalize data.

Register a new datasource for a file extension or python class
through add_datasource or the @datasource decorator.
"""

from .data_source import ColumnMetadata, DataSource
from .decorator import datasource
from .registry import add_datasource, create_datasource

__all__ = [
    "ColumnMetadata",
    "DataSource",
    "add_datasource",
    "create_datasource",
    "datasource",
]
