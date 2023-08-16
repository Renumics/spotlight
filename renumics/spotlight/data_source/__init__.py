"""
Spotlight Datasources fetch and normalize data.

Register a new datasource for a file extension or python class
through add_datasource or the @datasource decorator.
"""


from .data_source import DataSource, ColumnMetadata
from .registry import create_datasource, add_datasource
from .decorator import datasource

__all__ = [
    "DataSource",
    "ColumnMetadata",
    "datasource",
    "create_datasource",
    "add_datasource",
]
