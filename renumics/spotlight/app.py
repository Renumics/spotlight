"""
Spotlight wsgi application
"""

import asyncio
import mimetypes
import multiprocessing.connection
import os
import re
import time
import uuid
from concurrent.futures import CancelledError, Future
from pathlib import Path
from threading import Thread
from typing import Any, Dict, List, Literal, Optional, Union, cast

import pandas as pd
from fastapi import Cookie, FastAPI, Request, status
from fastapi.datastructures import Headers
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from httpx import URL, AsyncClient
from typing_extensions import Annotated

from renumics.spotlight import dtypes as spotlight_dtypes
from renumics.spotlight import layouts
from renumics.spotlight.analysis import find_issues
from renumics.spotlight.analysis.typing import DataIssue
from renumics.spotlight.app_config import AppConfig
from renumics.spotlight.backend.apis import plugins as plugin_api
from renumics.spotlight.backend.apis import websocket
from renumics.spotlight.backend.config import Config
from renumics.spotlight.backend.exceptions import Problem
from renumics.spotlight.backend.middlewares.timing import add_timing_middleware
from renumics.spotlight.backend.tasks.task_manager import TaskManager
from renumics.spotlight.backend.websockets import (
    Message,
    RefreshMessage,
    ResetLayoutMessage,
    WebsocketManager,
)
from renumics.spotlight.data_source import DataSource, create_datasource
from renumics.spotlight.data_store import DataStore
from renumics.spotlight.develop.project import get_project_info
from renumics.spotlight.embeddings import create_embedders, run_embedders
from renumics.spotlight.layout.nodes import Layout
from renumics.spotlight.logging import logger
from renumics.spotlight.plugin_loader import load_plugins
from renumics.spotlight.reporting import (
    emit_exception_event,
    emit_exit_event,
    emit_startup_event,
)
from renumics.spotlight.settings import settings
from renumics.spotlight.typing import PathType

CURRENT_LAYOUT_KEY = "layout.current"


# explicitly set mimetypes for broken python setups
mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("image/svg+xml", ".svg")


class UncachedStaticFiles(StaticFiles):
    """
    FastAPI StaticFiles but without caching
    """

    def is_not_modified(
        self, response_headers: Headers, request_headers: Headers
    ) -> bool:
        """
        Never Cache
        """
        return False


class IssuesUpdatedMessage(Message):
    """
    Notify about updated issues.
    """

    type: Literal["issuesUpdated"] = "issuesUpdated"
    data: Any = None


class ColumnsUpdatedMessage(Message):
    """
    Notify about updated embeddings.
    """

    type: Literal["columnsUpdated"] = "columnsUpdated"
    data: List[str]


class SpotlightApp(FastAPI):
    """
    Spotlight wsgi application
    """

    # lifecycle
    _loop: asyncio.AbstractEventLoop

    # connection
    _connection: multiprocessing.connection.Connection
    _receiver_thread: Thread

    # datasource
    _dataset: Optional[Union[PathType, pd.DataFrame]]
    _user_dtypes: spotlight_dtypes.DTypeMap
    _data_source: Optional[DataSource]
    _data_store: Optional[DataStore]

    task_manager: TaskManager
    websocket_manager: Optional[WebsocketManager]
    _layout: Layout
    config: Config
    username: str
    filebrowsing_allowed: bool

    # dev
    project_root: PathType
    vite_url: Optional[str]

    # data issues
    issues: Optional[List[DataIssue]] = []
    _custom_issues: List[DataIssue] = []
    analyze_columns: Union[List[str], bool]

    # embedding
    embed_columns: Union[List[str], bool]

    def __init__(self) -> None:
        super().__init__()
        self.task_manager = TaskManager()
        self.websocket_manager = None
        self.config = Config()
        self._layout = layouts.default()
        self.project_root = Path.cwd()
        self.vite_url = None
        self.username = ""
        self.filebrowsing_allowed = False
        self.analyze_columns = False
        self.issues = None
        self._custom_issues = []
        self.embed_columns = False

        self._dataset = None
        self._user_dtypes = {}
        self._data_source = None
        self._data_store = None

        @self.on_event("startup")
        def _() -> None:
            port = int(os.environ["CONNECTION_PORT"])
            authkey = os.environ["CONNECTION_AUTHKEY"]

            self._loop = asyncio.get_running_loop()

            for _ in range(10):
                try:
                    self._connection = multiprocessing.connection.Client(
                        ("127.0.0.1", port), authkey=authkey.encode()
                    )
                except ConnectionRefusedError:
                    time.sleep(0.1)
                else:
                    break
            else:
                raise RuntimeError("Failed to connect to parent process")

            self._receiver_thread = Thread(target=self._receive, daemon=True)
            self._receiver_thread.start()
            self._connection.send({"kind": "startup"})

            def handle_ws_connect(active_connections: int) -> None:
                self._connection.send(
                    {"kind": "frontend_connected", "data": active_connections}
                )

            def handle_ws_disconnect(active_connections: int) -> None:
                self._connection.send(
                    {"kind": "frontend_disconnected", "data": active_connections}
                )

            self.websocket_manager = WebsocketManager(asyncio.get_running_loop())
            self.websocket_manager.add_connect_callback(handle_ws_connect)
            self.websocket_manager.add_disconnect_callback(handle_ws_disconnect)

            self.vite_url = os.environ.get("VITE_URL")

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
            # Mount frontend files as uncached,
            # so that we always get the new frontend after updating spotlight.
            # NOTE: we might not need this if we added a version hash
            # to our built js files
            self.mount(
                "/static",
                UncachedStaticFiles(packages=["renumics.spotlight.backend"]),
                name="assets",
            )
        except AssertionError:
            logger.warning("Frontend module is missing. No frontend will be served.")

        templates = Jinja2Templates(
            directory=Path(__file__).parent / "backend" / "templates"
        )

        async def _reverse_proxy(request: Request) -> Response:
            http_server = AsyncClient(base_url=request.app.vite_url)
            url = URL(path=request.url.path, query=request.url.query.encode("utf-8"))

            # URL-encoding is not accepted by vite. Use unencoded path instead.

            url._uri_reference = url._uri_reference._replace(path=request.url.path)

            body = await request.body()

            rp_req = http_server.build_request(
                request.method,
                url,
                headers=request.headers.raw,
                content=body,
            )

            rp_resp = await http_server.send(rp_req, stream=False)

            return Response(
                content=rp_resp.content,
                status_code=rp_resp.status_code,
                headers=rp_resp.headers,
            )

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
                "browser_id",
                browser_id or str(uuid.uuid4()),
                samesite="none",
                secure=True,
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

            # Reverse proxy routes for webworker loading in dev mode
            self.add_route("/src/{path:path}", _reverse_proxy, ["POST", "GET"])
            self.add_route(
                "/node_modules/.vite/dist/client/{path:path}",
                _reverse_proxy,
                ["POST", "GET"],
            )
            self.add_route(
                "/node_modules/.vite/deps/{path:path}", _reverse_proxy, ["POST", "GET"]
            )
            self.add_route(
                "/node_modules/.pnpm/{path:path}", _reverse_proxy, ["POST", "GET"]
            )

    def update(self, config: AppConfig) -> None:
        """
        Update application config.
        """
        try:
            if config.project_root is not None:
                self.project_root = config.project_root
            if config.dtypes is not None:
                self._user_dtypes = config.dtypes
            if config.analyze is not None:
                self.analyze_columns = config.analyze
            if config.custom_issues is not None:
                self.custom_issues = config.custom_issues
            if config.embed is not None:
                self.embed_columns = config.embed
            if config.dataset is not None:
                self._dataset = config.dataset
                self._data_source = create_datasource(self._dataset)
            if config.layout is not None:
                self._layout = config.layout or layouts.default()
            if config.filebrowsing_allowed is not None:
                self.filebrowsing_allowed = config.filebrowsing_allowed

            if config.dtypes is not None or config.dataset is not None:
                data_source = self._data_source
                assert data_source is not None
                self._data_store = DataStore(data_source, self._user_dtypes)
                self._broadcast(RefreshMessage())
                self._update_issues()
                self._update_embeddings()
            if config.layout is not None:
                if self._data_store is not None:
                    dataset_uid = self._data_store.uid
                    future = asyncio.run_coroutine_threadsafe(
                        self.config.remove_all(CURRENT_LAYOUT_KEY, dataset=dataset_uid),
                        self._loop,
                    )
                    future.result()
                self._broadcast(ResetLayoutMessage())

            for plugin in load_plugins():
                plugin.update(self, config)
        except Exception as e:
            self._connection.send({"kind": "update_complete", "error": e})
            logger.exception(e)

        self._connection.send({"kind": "update_complete"})

    def _handle_message(self, message: Any) -> None:
        kind = message.get("kind")
        data = message.get("data")

        if kind is None:
            logger.error(f"Malformed message from client process:\n\t{message}")
        elif kind == "update":
            self.update(data)
        elif kind == "get_df":
            df = self._data_source.df if self._data_source else None
            self._connection.send({"kind": "df", "data": df})
        elif kind == "refresh_frontends":
            self._broadcast(RefreshMessage())
        else:
            logger.warning(f"Unknown message from client process:\n\t{message}")

    def _receive(self) -> None:
        while True:
            try:
                self._handle_message(self._connection.recv())
            except EOFError:
                # the master process closed the connection
                # just stop receiving
                return

    @property
    def data_store(self) -> Optional[DataStore]:
        """
        Current data store.
        """
        return self._data_store

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

    @property
    def layout(self) -> Layout:
        """
        Frontend layout
        """
        return self._layout

    async def get_current_layout_dict(self, user_id: str) -> Optional[Dict]:
        """
        Get the user's current layout (as dict)
        """

        if not self._data_store:
            return None

        dataset_uid = self._data_store.uid
        layout = await self.config.get(
            CURRENT_LAYOUT_KEY, dataset=dataset_uid, user=user_id
        ) or self.layout.model_dump(by_alias=True)
        return cast(Optional[Dict], layout)

    def _update_issues(self) -> None:
        """
        Update issues and notify client about.
        """

        # early out for [] and False
        if not self.analyze_columns:
            self.issues = []
            self._broadcast(IssuesUpdatedMessage())
            return

        self.issues = None
        self._broadcast(IssuesUpdatedMessage())
        if self._data_store is None:
            return

        if self.analyze_columns is True:
            columns = self._data_store.column_names
        else:
            columns = self.analyze_columns

        task = self.task_manager.create_task(
            find_issues, (self._data_store, columns), name="update_issues"
        )

        def _on_issues_ready(future: Future) -> None:
            try:
                self.issues = future.result()
            except CancelledError:
                return
            self._broadcast(IssuesUpdatedMessage())

        task.future.add_done_callback(_on_issues_ready)

    def _update_embeddings(self) -> None:
        """
        Update embeddings, update them in the data store and notify client about.
        """
        if not self.embed_columns:
            return

        if self._data_store is None:
            return

        logger.info("Embedding started.")

        if self.embed_columns is True:
            embed_columns = self._data_store.column_names
        else:
            embed_columns = [
                column
                for column in self.embed_columns
                if column in self._data_store.column_names
            ]

        embedders = create_embedders(self._data_store, embed_columns)

        self._data_store.embeddings = {column: None for column in embedders}

        task = self.task_manager.create_task(
            run_embedders, (embedders,), name="update_embeddings"
        )

        def _on_embeddings_ready(future: Future) -> None:
            if self._data_store is None:
                return
            try:
                self._data_store.embeddings = future.result()
            except CancelledError:
                return
            logger.info("Embedding done.")
            self._broadcast(ColumnsUpdatedMessage(data=list(embedders.keys())))

        task.future.add_done_callback(_on_embeddings_ready)

    def _broadcast(self, message: Message) -> None:
        """
        Broadcast a message to all connected clients via websocket
        """
        if self.websocket_manager:
            self.websocket_manager.broadcast(message)
