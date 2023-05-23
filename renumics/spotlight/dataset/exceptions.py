"""
This module provides exceptions for Spotlight dataset.
"""


class DatasetException(Exception):
    """
    Base dataset exception.
    """


class ClosedDatasetError(DatasetException):
    """
    Dataset is closed.
    """


class ReadOnlyDatasetError(DatasetException):
    """
    Dataset is read-only.
    """


class InconsistentDatasetError(DatasetException):
    """
    Dataset is inconsistent.
    """


class InvalidRowError(DatasetException):
    """
    Row does not match dataset.
    """


class InvalidModeError(DatasetException):
    """
    Invalid dataset open mode.
    """


class InvalidAttributeError(DatasetException):
    """
    Invalid column attribute.
    """


class ColumnExistsError(DatasetException):
    """
    Dataset column already exists.
    """


class ColumnNotExistsError(DatasetException):
    """
    Dataset column does not exist.
    """


class InvalidColumnNameError(DatasetException):
    """
    Invalid dataset column name.
    """


class InvalidDTypeError(DatasetException):
    """
    Value does not match dataset column type.
    """


class InvalidShapeError(DatasetException):
    """
    Value does not match dataset column shape.
    """


class InvalidValueError(DatasetException):
    """
    Value is not allowed in the column.
    """


class InvalidIndexError(DatasetException, IndexError):
    """
    Invalid index.
    """


class DatasetColumnsNotUnique(DatasetException):
    """
    Dataset's columns are not unique.
    """
