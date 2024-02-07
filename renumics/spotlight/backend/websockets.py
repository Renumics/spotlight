"""
This module provides interfaces for websockets.
"""

import asyncio
from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    Optional,
    Set,
    Tuple,
    Type,
    cast,
)

import numpy as np
import orjson
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger
from pydantic import BaseModel
from typing_extensions import Literal

from renumics.spotlight.data_store import DataStore

from .exceptions import GenerationIDMismatch, Problem
from .tasks import TaskCancelled, TaskManager
from .tasks.reduction import compute_pca, compute_umap


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


class TaskData(BaseModel):
    task: str
    widget_id: str
    task_id: str
    generation_id: Optional[int]
    args: Any


class UnknownMessageType(Exception):
    """
    Websocket message type is unknown.
    """


class SerializationError(Exception):
    """
    Failed to serialize the WS message
    """


PayloadType = Type[BaseModel]
MessageHandler = Callable[[Any, "WebsocketConnection"], Coroutine[Any, Any, Any]]
MessageHandlerSpec = Tuple[PayloadType, MessageHandler]
MESSAGE_HANDLERS: Dict[str, MessageHandlerSpec] = {}


def register_message_handler(
    message_type: str, handler_spec: MessageHandlerSpec
) -> None:
    MESSAGE_HANDLERS[message_type] = handler_spec


def message_handler(
    message_type: str, payload_type: Type[BaseModel]
) -> Callable[[MessageHandler], MessageHandler]:
    def decorator(handler: MessageHandler) -> MessageHandler:
        register_message_handler(message_type, (payload_type, handler))
        return handler

    return decorator


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
            json_text = orjson.dumps(
                message.model_dump(), option=orjson.OPT_SERIALIZE_NUMPY
            ).decode()
        except TypeError as e:
            raise SerializationError(str(e))
        try:
            await self.websocket.send_text(json_text)
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
                    raw_message = await self.websocket.receive_text()
                    message = Message(**orjson.loads(raw_message))
                except UnknownMessageType as e:
                    logger.warning(str(e))
                else:
                    logger.info(f"WS message with type {message.type} received.")
                    if handler_spec := MESSAGE_HANDLERS.get(message.type):
                        payload_type, handler = handler_spec
                        asyncio.create_task(handler(payload_type(**message.data), self))
                    else:
                        logger.error(f"Unknown message received: {message.type}")
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


TASK_FUNCS = {"umap": compute_umap, "pca": compute_pca}


@message_handler("task", TaskData)
async def _(data: TaskData, connection: WebsocketConnection) -> None:
    data_store: Optional[DataStore] = connection.websocket.app.data_store
    if data_store is None:
        return None

    if data.generation_id:
        try:
            data_store.check_generation_id(data.generation_id)
        except GenerationIDMismatch:
            return

    try:
        task_func = TASK_FUNCS[data.task]
        result = await connection.task_manager.run_async(
            task_func,  # type: ignore
            args=(data_store,),
            kwargs=data.args,
            name=data.widget_id,
            tag=id(connection),
        )
        points = cast(np.ndarray, result[0])
        valid_indices = cast(np.ndarray, result[1])
    except TaskCancelled:
        pass
    except Problem as e:
        logger.exception(e)
        msg = Message(
            type="task.error",
            data={
                "task_id": data.task_id,
                "error": {
                    "type": type(e).__name__,
                    "title": e.title,
                    "detail": e.detail,
                },
            },
        )
        await connection.send_async(msg)
    except Exception as e:
        logger.exception(e)
        msg = Message(
            type="task.error",
            data={
                "task_id": data.task_id,
                "error": {
                    "type": type(e).__name__,
                    "title": type(e).__name__,
                    "detail": type(e).__doc__,
                },
            },
        )
        await connection.send_async(msg)
    else:
        msg = Message(
            type="task.result",
            data={
                "task_id": data.task_id,
                "result": {"points": points, "indices": valid_indices},
            },
        )
        try:
            await connection.send_async(msg)
        except SerializationError as e:
            error_msg = Message(
                type="task.error",
                data={
                    "task_id": data.task_id,
                    "error": {
                        "type": type(e).__name__,
                        "title": "Serialization Error",
                        "detail": str(e),
                    },
                },
            )
            await connection.send_async(error_msg)
