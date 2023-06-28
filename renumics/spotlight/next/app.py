import asyncio
import os

from concurrent.futures import CancelledError, Future
import re
from threading import Thread
import multiprocessing.connection
from typing import Annotated, Any, List, Literal, Optional, Union
import uuid
from fastapi import Cookie, FastAPI, Request, status
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

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

from renumics.spotlight.backend.apis import plugins as plugin_api
from renumics.spotlight.backend.apis import websocket
from renumics.spotlight.settings import settings

from renumics.spotlight.analysis import find_issues

from renumics.spotlight.reporting import emit_exception_event, emit_exit_event, emit_startup_event

from renumics.spotlight.backend.exceptions import Problem

from renumics.spotlight.plugin_loader import load_plugins

from renumics.spotlight.develop.project import get_project_info

from renumics.spotlight.backend.middlewares.timing import add_timing_middleware


@dataclass
class IssuesUpdatedMessage(Message):
    """
    Notify about updated issues.
    """

    type: Literal["issuesUpdated"] = "issuesUpdated"
    data: Any = None


class SpotlightApp(FastAPI):
    _connection: multiprocessing.connection.Connection
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
            port = int(os.environ["CONNECTION_PORT"])
            authkey = os.environ["CONNECTION_AUTHKEY"]
            self._connection = multiprocessing.connection.Client(('127.0.0.1', port), authkey=authkey.encode())
            self._receiver_thread = Thread(target=self._receive, daemon=True)
            self._receiver_thread.start()
            self._connection.send({"kind": "startup"})
            self.websocket_manager = WebsocketManager(asyncio.get_running_loop())
            emit_startup_event()

        @self.on_event("shutdown")
        def _() -> None:
            self._receiver_thread.join(0.1)
            self.task_manager.shutdown()
            emit_exit_event()

        self.include_router(websocket.router, prefix="/api")
        self.include_router(plugin_api.router, prefix="/api/plugins")

        @self.exception_handler(Exception)
        async def _(_: Request, e: Exception) -> JSONResponse:
            if settings.verbose:
                logger.exception(e)
            else:
                logger.info(e)
            emit_exception_event()
            class_name = type(e).__name__
            title = re.sub(r"([a-z])([A-Z])", r"\1 \2", class_name)
            return JSONResponse(
                {"title": title, "detail": str(e), "type": class_name},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        @self.exception_handler(Problem)
        async def _(_: Request, problem: Problem) -> JSONResponse:
            if settings.verbose:
                logger.exception(problem)
            else:
                logger.info(problem)
            return JSONResponse(
                {
                    "title": problem.title,
                    "detail": problem.detail,
                    "type": type(problem).__name__,
                },
                status_code=problem.status_code,
            )

        for plugin in load_plugins():
            plugin.activate(self)

        try:
            self.mount(
                "/static",
                StaticFiles(packages=["renumics.spotlight.backend"]),
                name="assets",
            )
        except AssertionError:
            logger.warning("Frontend module is missing. No frontend will be served.")


        templates = Jinja2Templates(directory=Path(__file__).parent.parent / "backend" / "templates")

        @self.get("/")
        def _(
            request: Request, browser_id: Annotated[Union[str, None], Cookie()] = None
        ) -> Any:
            response = templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "dev": settings.dev,
                    "dev_location": get_project_info().type,
                    "vite_url": request.app.vite_url,
                    "filebrowsing_allowed": request.app.filebrowsing_allowed,
                },
            )
            response.set_cookie(
                "browser_id", browser_id or str(uuid.uuid4()), samesite="none", secure=True
            )
            return response

        if settings.dev:
            logger.info("Running in dev mode")
            self.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
            add_timing_middleware(self)

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
            self._handle_message(self._connection.recv())

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
