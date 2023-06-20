"""
Dataset Analysis
"""

from concurrent.futures import CancelledError, Future
from typing import Any, List, Optional

from pydantic.dataclasses import dataclass
from typing_extensions import Literal

# import the actual analyzers to let them register themselves
import renumics.spotlight.analysis.outliers
import renumics.spotlight.analysis.images
from renumics.spotlight.backend import DataSource

from renumics.spotlight.backend.types import SpotlightApp
from renumics.spotlight.backend.websockets import Message
from renumics.spotlight.dtypes.typing import ColumnTypeMapping

from .typing import DataIssue
from .registry import registered_analyzers


def find_issues(data_source: DataSource, dtypes: ColumnTypeMapping) -> List[DataIssue]:
    """
    Find dataset issues in the data source
    """

    issues: List[DataIssue] = []
    for analyze in registered_analyzers:
        issues.extend(analyze(data_source, dtypes))

    return issues


ISSUES: List[DataIssue] = []


@dataclass
class IssuesUpdatedMessage(Message):
    """
    Notify about updated issues.
    """

    type: Literal["issuesUpdated"] = "issuesUpdated"
    data: Any = None


def update_issues(app: SpotlightApp) -> None:
    """
    Update issues and notify client about.
    """
    # pylint: disable=global-statement
    table: Optional[DataSource] = app.data_source
    global ISSUES
    ISSUES = []
    websocket_manager = getattr(app, "websocket_manager", None)
    if websocket_manager:
        app.websocket_manager.broadcast(IssuesUpdatedMessage())
    if table is None:
        return
    task = app.task_manager.create_task(
        find_issues, (table, table.dtype), name="update_issues"
    )

    def _on_issues_ready(future: Future) -> None:
        global ISSUES
        try:
            ISSUES = future.result()
        except CancelledError:
            ...
        else:
            if websocket_manager:
                app.websocket_manager.broadcast(IssuesUpdatedMessage())

    task.future.add_done_callback(_on_issues_ready)
