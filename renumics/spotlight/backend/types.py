"""
Types used in backend
"""

from concurrent.futures import CancelledError, Future
from pathlib import Path
from typing import Any, Optional, List
from typing_extensions import Literal
from fastapi import FastAPI
from pydantic.dataclasses import dataclass

from renumics.spotlight.analysis import find_issues, DataIssue
from renumics.spotlight.backend.data_source import DataSource
from renumics.spotlight.backend.tasks.task_manager import TaskManager
from renumics.spotlight.backend.websockets import Message, WebsocketManager
from renumics.spotlight.layout.nodes import Layout
from renumics.spotlight.backend.config import Config
from renumics.spotlight.typing import PathType
from renumics.spotlight.dtypes.typing import ColumnTypeMapping


@dataclass
class IssuesUpdatedMessage(Message):
    """
    Notify about updated issues.
    """

    type: Literal["issuesUpdated"] = "issuesUpdated"
    data: Any = None


class SpotlightApp(FastAPI):
    """
    Custom FastAPI Application class
    Provides typing support for our custom app attributes
    """

    # pylint: disable=too-many-instance-attributes

    _data_source: Optional[DataSource]
    dtype: Optional[ColumnTypeMapping]
    task_manager: TaskManager
    websocket_manager: Optional[WebsocketManager]
    layout: Optional[Layout]
    config: Config
    project_root: PathType
    vite_url: Optional[str]
    username: str
    filebrowsing_allowed: bool
    analyze_issues: bool = True
    issues: Optional[List[DataIssue]] = []
    _custom_issues: List[DataIssue] = []

    def __init__(self) -> None:
        super().__init__()
        self._data_source = None
        self.dtype = None
        self.task_manager = TaskManager()
        self.websocket_manager = None
        self.config = Config()
        self.layout = None
        self.project_root = Path.cwd()
        self.vite_url = None
        self.username = ""
        self.filebrowsing_allowed = False
        self.analyze_issues = False
        self.issues = None
        self._custom_issues = []

    @property
    def data_source(self) -> Optional[DataSource]:
        """
        Current data source.
        """
        return self._data_source

    @data_source.setter
    def data_source(self, new_data_source: Optional[DataSource]) -> None:
        self._data_source = new_data_source
        self._update_issues()

    @property
    def custom_issues(self) -> List[DataIssue]:
        """
        User supplied `DataIssue`s
        """
        return self._custom_issues

    @custom_issues.setter
    def custom_issues(self, issues: List[DataIssue]) -> None:
        self._custom_issues = issues
        self._broadcast(IssuesUpdatedMessage())

    def _update_issues(self) -> None:
        """
        Update issues and notify client about.
        """
        # pylint: disable=global-statement

        if not self.analyze_issues:
            self.issues = []
            self._broadcast(IssuesUpdatedMessage())
            return

        table: Optional[DataSource] = self.data_source
        self.issues = None
        self._broadcast(IssuesUpdatedMessage())
        if table is None:
            return
        task = self.task_manager.create_task(
            find_issues, (table, table.dtype), name="update_issues"
        )

        def _on_issues_ready(future: Future) -> None:
            try:
                self.issues = future.result()
            except CancelledError:
                return
            self._broadcast(IssuesUpdatedMessage())

        task.future.add_done_callback(_on_issues_ready)

    def _broadcast(self, message: Message) -> None:
        """
        Broadcast a message to all connected clients via websocket
        """
        if self.websocket_manager:
            self.websocket_manager.broadcast(message)
