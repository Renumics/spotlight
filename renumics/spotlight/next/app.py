from concurrent.futures import CancelledError, Future
from threading import Thread
from typing import Any, List, Literal, Optional
from fastapi import FastAPI
from pathlib import Path

from pydantic.dataclasses import dataclass

from renumics.spotlight.backend.data_source import DataSource
from renumics.spotlight.dtypes.typing import ColumnTypeMapping
from renumics.spotlight.backend.tasks.task_manager import TaskManager
from renumics.spotlight.backend.websockets import Message, WebsocketManager
from renumics.spotlight.layout.nodes import Layout
from renumics.spotlight.backend.config import Config
from renumics.spotlight.typing import PathType
from renumics.spotlight.analysis.typing import DataIssue
from renumics.spotlight.logging import logger

from renumics.spotlight.analysis import find_issues

from .uvicorn_worker import worker


@dataclass
class IssuesUpdatedMessage(Message):
    """
    Notify about updated issues.
    """

    type: Literal["issuesUpdated"] = "issuesUpdated"
    data: Any = None


class SpotlightApp(FastAPI):
    _receiver_thread: Thread
    _data_source: Optional[DataSource]

    dtype: Optional[ColumnTypeMapping]
    task_manager: TaskManager
    websocket_manager: Optional[WebsocketManager]
    layout: Optional[Layout]
    config: Config
    username: str
    filebrowsing_allowed: bool

    # dev
    project_root: PathType
    vite_url: Optional[str]

    # data issues
    issues: Optional[List[DataIssue]] = []
    _custom_issues: List[DataIssue] = []
    analyze_issues: bool = True

    def __init__(self):
        super().__init__()
        self.dtype = None
        self.task_manager = TaskManager()
        self.websocket_manager = None
        self.config = Config()
        self.layout = None
        self.project_root = Path.cwd()
        self.vite_url = None
        self.username = ""
        self.filebrowsing_allowed = False
        self.analyze_issues = True
        self.issues = None
        self._custom_issues = []

        self.data_source = None

        @self.on_event("startup")
        def _():
            self._receiver_thread = Thread(target=self._receive)
            self._receiver_thread.start()
            self.connection.send({"kind": "startup"})

        @self.get("/")
        def _():
            return "Hello World"

    @property
    def connection(self):
        assert worker
        return worker.connection

    def _handle_message(self, message):
        kind = message.get("kind")

        if kind is None:
            logger.error(f"Malformed message from client process:\n\t{message}")
            return
        if kind == "datasource":
            try:
                data_source = message["data"]
                assert isinstance(data_source, DataSource)
                self.data_source = data_source
            except KeyError:
                logger.error(f"Malformed message from client process:\n\t{message}")
            return
        logger.warning(f"Unknown message from client process:\n\t{message}")

    def _receive(self):
        while True:
            self._handle_message(self.connection.recv())

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
