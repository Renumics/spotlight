"""
This module provides interfaces for websockets.
"""

import asyncio
import dataclasses
import functools
import json
from typing import Any, List, Set, Callable

from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger
from pydantic.dataclasses import dataclass
from typing_extensions import Literal
from wsproto.utilities import LocalProtocolError

from .data_source import sanitize_values, DataSource
from .tasks import TaskManager, TaskCancelled
from .tasks.reduction import compute_umap, compute_pca
from .exceptions import GenerationIDMismatch


@dataclass
class Message:
    """
    Common websocket message model.
    """

    type: str
    data: Any


@dataclass
class RefreshMessage(Message):
    """
    Refresh message model
    """

    type: Literal["refresh"] = "refresh"
    data: Any = None


@dataclass
class ReductionMessage(Message):
    """
    Common data reduction message model.
    """

    widget_id: str
    uid: str
    generation_id: int


@dataclass
class ReductionRequestData:
    """
    Base data reduction request payload.
    """

    indices: List[int]
    columns: List[str]


@dataclass
class UMapRequestData(ReductionRequestData):
    """
    U-Map request payload.
    """

    n_neighbors: int
    metric: str
    min_dist: float


@dataclass
class PCARequestData(ReductionRequestData):
    """
    PCA request payload.
    """

    normalization: str


@dataclass
class UMapRequest(ReductionMessage):
    """
    U-Map request model.
    """

    data: UMapRequestData


@dataclass
class PCARequest(ReductionMessage):
    """
    PCA request model.
    """

    data: PCARequestData


@dataclass
class ReductionResponseData:
    """
    Data reduction response payload.
    """

    indices: List[int]
    points: List[List[float]]


@dataclass
class ReductionResponse(ReductionMessage):
    """
    Data reduction response model.
    """

    data: ReductionResponseData


MESSAGE_BY_TYPE = {
    "umap": UMapRequest,
    "umap_result": ReductionResponse,
    "pca": PCARequest,
    "pca_result": ReductionResponse,
    "refresh": RefreshMessage,
}


class UnknownMessageType(Exception):
    """
    Websocket message type is unknown.
    """


def parse_message(raw_message: str) -> Message:
    """
    Parse a websocket message from a raw text.
    """
    json_message = json.loads(raw_message)
    message_type = json_message["type"]
    message_class = MESSAGE_BY_TYPE.get(message_type)
    if message_class is None:
        raise UnknownMessageType(f"Message type {message_type} is unknown.")
    return message_class(**json_message)


@functools.singledispatch
async def handle_message(request: Message, connection: "WebsocketConnection") -> None:
    """
    Handle incoming messages.

    New message types should be registered by decorating with `@handle_message.register`.
    """

    raise NotImplementedError


class WebsocketConnection:
    """
    Wraps websocket and dispatches messages to message handlers.
    """

    websocket: WebSocket
    manager: "WebsocketManager"

    def __init__(self, websocket: WebSocket, manager: "WebsocketManager") -> None:
        self.websocket = websocket
        self.manager = manager

    async def send_async(self, message: Message) -> None:
        """
        Send a message async.
        """
        try:
            await self.websocket.send_json(dataclasses.asdict(message))
        except WebSocketDisconnect:
            self._on_disconnect()
        except LocalProtocolError:
            # connection already disconnected
            pass

    def send(self, message: Message) -> None:
        """
        Send a message without async.
        """
        self.manager.loop.create_task(self.send_async(message))

    def _on_disconnect(self) -> None:
        self.manager.on_disconnect(self)
        self.task_manager.cancel(tag=id(self))

    async def listen(self) -> None:
        """
        Wait for websocket connection and handle incoming messages.
        """
        await self.websocket.accept()
        self.manager.on_connect(self)
        try:
            while True:
                try:
                    message = parse_message(await self.websocket.receive_text())
                except UnknownMessageType as e:
                    logger.warning(str(e))
                else:
                    logger.info(f"WS message with type {message.type} received.")
                    asyncio.create_task(handle_message(message, self))
        except WebSocketDisconnect:
            self._on_disconnect()

    @property
    def task_manager(self) -> TaskManager:
        """
        The app's task manager
        """
        return self.websocket.app.task_manager


ConnectCallback = Callable[[int], None]


class WebsocketManager:
    """
    Manages websocket connections.
    """

    loop: asyncio.AbstractEventLoop
    connections: Set[WebsocketConnection]
    _disconnect_callbacks: Set[ConnectCallback]
    _connect_callbacks: Set[ConnectCallback]

    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self.loop = loop
        self.connections = set()
        self._disconnect_callbacks = set()
        self._connect_callbacks = set()

    def create_connection(self, websocket: WebSocket) -> WebsocketConnection:
        """
        Create a new websocket connection.
        """
        return WebsocketConnection(websocket, self)

    def broadcast(self, message: Message) -> None:
        """
        Send message to all connected clients.
        """
        for connection in self.connections:
            connection.send(message)

    def add_disconnect_callback(self, callback: ConnectCallback) -> None:
        """
        Add a listener that is notified after a connection terminates
        """
        self._disconnect_callbacks.add(callback)

    def remove_disconnect_callback(self, callback: ConnectCallback) -> None:
        """
        Remove the provided listener if possible
        """
        try:
            self._disconnect_callbacks.remove(callback)
        except KeyError:
            pass

    def add_connect_callback(self, callback: ConnectCallback) -> None:
        """
        Add a listener that is notified after a connection is initialized
        """
        self._connect_callbacks.add(callback)

    def remove_connect_callback(self, callback: ConnectCallback) -> None:
        """
        Remove the provided listener if possible
        """
        try:
            self._connect_callbacks.remove(callback)
        except KeyError:
            pass

    def on_connect(self, connection: WebsocketConnection) -> None:
        """
        Handle a new conection
        """
        self.connections.add(connection)
        for callback in self._connect_callbacks:
            callback(len(self.connections))

    def on_disconnect(self, connection: WebsocketConnection) -> None:
        """
        Handle the termination of an existing connection
        """
        self.connections.remove(connection)
        for callback in self._disconnect_callbacks:
            callback(len(self.connections))


@handle_message.register
async def _(request: UMapRequest, connection: "WebsocketConnection") -> None:
    table: DataSource = connection.websocket.app.data_source
    try:
        table.check_generation_id(request.generation_id)
    except GenerationIDMismatch:
        return

    try:
        points, valid_indices = await connection.task_manager.run_async(
            compute_umap,
            (
                table,
                request.data.columns,
                request.data.indices,
                request.data.n_neighbors,
                request.data.metric,
                request.data.min_dist,
            ),
            name=request.widget_id,
            tag=id(connection),
        )
    except TaskCancelled:
        ...
    else:
        response = ReductionResponse(
            type="umap_result",
            widget_id=request.widget_id,
            uid=request.uid,
            generation_id=request.generation_id,
            data=ReductionResponseData(
                indices=valid_indices, points=sanitize_values(points)
            ),
        )
        await connection.send_async(response)


@handle_message.register
async def _(request: PCARequest, connection: "WebsocketConnection") -> None:
    table: DataSource = connection.websocket.app.data_source
    try:
        table.check_generation_id(request.generation_id)
    except GenerationIDMismatch:
        return

    try:
        points, valid_indices = await connection.task_manager.run_async(
            compute_pca,
            (
                table,
                request.data.columns,
                request.data.indices,
                request.data.normalization,
            ),
            name=request.widget_id,
            tag=id(connection),
        )
    except TaskCancelled:
        ...
    else:
        response = ReductionResponse(
            type="pca_result",
            widget_id=request.widget_id,
            uid=request.uid,
            generation_id=request.generation_id,
            data=ReductionResponseData(
                indices=valid_indices, points=sanitize_values(points)
            ),
        )
        await connection.send_async(response)
