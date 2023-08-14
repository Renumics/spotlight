"""
This module provides interfaces for websockets.
"""

import asyncio
import functools
import orjson
from typing import Any, List, Optional, Set, Callable

import numpy as np
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger
from pydantic import BaseModel
from typing_extensions import Literal

from renumics.spotlight.data_store import DataStore

from .tasks import TaskManager, TaskCancelled
from .tasks.reduction import compute_umap, compute_pca
from .exceptions import GenerationIDMismatch


class Message(BaseModel):
    """
    Common websocket message model.
    """

    type: str
    data: Any


class RefreshMessage(Message):
    """
    Refresh message model
    """

    type: Literal["refresh"] = "refresh"
    data: Any = None


class ResetLayoutMessage(Message):
    """
    Reset layout message model
    """

    type: Literal["resetLayout"] = "resetLayout"
    data: Any = None


class ReductionMessage(Message):
    """
    Common data reduction message model.
    """

    widget_id: str
    uid: str
    generation_id: int


class ReductionRequestData(BaseModel):
    """
    Base data reduction request payload.
    """

    indices: List[int]
    columns: List[str]


class UMapRequestData(ReductionRequestData):
    """
    U-Map request payload.
    """

    n_neighbors: int
    metric: str
    min_dist: float


class PCARequestData(ReductionRequestData):
    """
    PCA request payload.
    """

    normalization: str


class UMapRequest(ReductionMessage):
    """
    U-Map request model.
    """

    data: UMapRequestData


class PCARequest(ReductionMessage):
    """
    PCA request model.
    """

    data: PCARequestData


class ReductionResponseData(BaseModel):
    """
    Data reduction response payload.
    """

    indices: List[int]
    points: np.ndarray

    class Config:
        arbitrary_types_allowed = True


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
    json_message = orjson.loads(raw_message)
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
            message_data = message.dict()
            await self.websocket.send_text(
                orjson.dumps(message_data, option=orjson.OPT_SERIALIZE_NUMPY).decode()
            )
        except WebSocketDisconnect:
            self._on_disconnect()
        except RuntimeError:
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
    data_store: Optional[DataStore] = connection.websocket.app.data_store
    if data_store is None:
        return None
    try:
        data_store.check_generation_id(request.generation_id)
    except GenerationIDMismatch:
        return

    try:
        points, valid_indices = await connection.task_manager.run_async(
            compute_umap,
            (
                data_store,
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
            data=ReductionResponseData(indices=valid_indices, points=points),
        )
        await connection.send_async(response)


@handle_message.register
async def _(request: PCARequest, connection: "WebsocketConnection") -> None:
    data_store: Optional[DataStore] = connection.websocket.app.data_store
    if data_store is None:
        return None
    try:
        data_store.check_generation_id(request.generation_id)
    except GenerationIDMismatch:
        return

    try:
        points, valid_indices = await connection.task_manager.run_async(
            compute_pca,
            (
                data_store,
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
            data=ReductionResponseData(indices=valid_indices, points=points),
        )
        await connection.send_async(response)
