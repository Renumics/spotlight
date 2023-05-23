"""
Exceptions to be raised from backend.
"""

from typing import Any, Optional, Type
from fastapi import status

from renumics.spotlight.dtypes.typing import ColumnType
from renumics.spotlight.typing import IndexType, PathOrURLType, PathType


class Problem(Exception):
    """
    Base API exception.
    """

    def __init__(self, title: str, detail: str, status_code: int = 500) -> None:
        self.title = title
        self.detail = detail
        self.status_code = status_code

    def __str__(self) -> str:
        return f"{self.title}: {self.detail}"


class InvalidPath(Problem):
    """The supported path is outside the project root or points to an incompatible file"""

    def __init__(self, path: PathType) -> None:
        super().__init__(
            "Invalid path", f"Path {path} is not valid.", status.HTTP_403_FORBIDDEN
        )


class InvalidDataSource(Problem):
    """The data source can't be opened"""

    def __init__(self) -> None:
        super().__init__(
            "Invalid data source",
            "Can't open supplied data source.",
            status.HTTP_403_FORBIDDEN,
        )


class NoTableFileFound(Problem):
    """raised when the table file could not be found"""

    def __init__(self, path: PathType) -> None:
        super().__init__(
            "Dataset file not found",
            f"File {path} does not exist.",
            status.HTTP_404_NOT_FOUND,
        )


class CouldNotOpenTableFile(Problem):
    """raised when the table file could not be found"""

    def __init__(self, path: PathType) -> None:
        super().__init__(
            "Could not open dataset",
            f"File {path} could not be opened.",
            status.HTTP_403_FORBIDDEN,
        )


class NoRowFound(Problem):
    """raised when a row can't be found in the dataset"""

    def __init__(self, index: Optional[IndexType] = None) -> None:
        if index is None:
            detail = "One of the requested rows does not exist."
        else:
            detail = f"Row {index} does not exist in the dataset."
        super().__init__("Row not found", detail, status.HTTP_404_NOT_FOUND)


class InvalidCategory(Problem):
    """An invalid Category was passed."""

    def __init__(self) -> None:
        super().__init__(
            "Invalid category",
            "Given category is not defined.",
            status.HTTP_403_FORBIDDEN,
        )


class ColumnNotEditable(Problem):
    """Column is not editable"""

    def __init__(self, name: str) -> None:
        super().__init__(
            "Column not editable",
            f"Column '{name}' is not editable.",
            status.HTTP_403_FORBIDDEN,
        )


class InvalidExternalData(Problem):
    """External data is not readable"""

    def __init__(self, value: PathOrURLType) -> None:
        super().__init__(
            "Invalid external data",
            f"Failed to read external data '{value}'.",
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class GenerationIDMismatch(Problem):
    """
    Generation ID does not match to the expected.
    """

    def __init__(self) -> None:
        super().__init__(
            "Dataset out of sync",
            "Dataset is out of sync. Refresh the browser.",
            status.HTTP_409_CONFLICT,
        )


class ConversionFailed(Problem):
    """
    Value cannot be converted to the desired dtype.
    """

    def __init__(self, dtype: Type[ColumnType], value: Any) -> None:
        self.dtype = dtype
        self.value = value
        super().__init__(
            "Type conversion failed",
            f"Value of type {type(value)} cannot be converted to type {dtype}.",
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class DatasetNotEditable(Problem):
    """The dataset is not editable"""

    def __init__(self) -> None:
        super().__init__(
            "Dataset not editable",
            "The dataset is not editable.",
            status.HTTP_403_FORBIDDEN,
        )


class DatasetColumnsNotUnique(Problem):
    """Dataset's columns are not unique"""

    def __init__(self) -> None:
        super().__init__(
            "Dataset columns not unique",
            "Dataset's columns are not unique.",
            status.HTTP_403_FORBIDDEN,
        )
