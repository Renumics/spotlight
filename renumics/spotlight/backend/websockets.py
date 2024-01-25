"""
This module provides interfaces for websockets.
"""

import asyncio
from typing import (
    Any,
    Coroutine,
    Dict,
    Optional,
    Set,
    Callable,
    Tuple,
    Type,
    cast,
)

import numpy as np
import orjson
import pandas as pd
from fastapi import WebSocket, WebSocketDisconnect
from loguru import logger
from openai import AsyncOpenAI
from pydantic import BaseModel
from typing_extensions import Literal

from renumics.spotlight.data_store import DataStore
from .exceptions import GenerationIDMismatch, Problem
from .tasks import TaskManager, TaskCancelled
from .tasks.reduction import compute_umap, compute_pca

openai_client = AsyncOpenAI()


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


class ChatData(BaseModel):
    chat_id: str
    message: str


sql_prompt_race = """
### Instructions:
Your task is to convert a question into a SQL query, given a Postgres database schema.
Adhere to these rules:
- **Deliberately go through the question and database schema word by word** to appropriately answer the question
- **Use Table Aliases** to prevent ambiguity. For example, `SELECT table1.col1, table2.col1 FROM table1 JOIN table2 ON table1.id = table2.id`.
- When creating a ratio, always cast the numerator as float
- ALWAYS include the index column as row_number, when selecting from the df table. For example, `SELECT df.index as row_number ...`

### Input:
Generate a SQL query that answers the question `{question}`.
This query will run on a database whose schema is represented in this string:
CREATE TABLE df (
    index INTEGER, -- the index of the row in the original dataset
    time INTERVAL, -- absolute session time when the lap time was set (end of lap)
    driver_number VARCHAR, -- Driver identifier
    driver VARCHAR, -- 3 letter code of the driver
    driver_name VARCHAR, -- Full name of the driver
    lap_time INTERVAL, -- The recorded lap time is the time the driver needed to complete this lap
    lap_time_seconds FLOAT, -- The recorded lap time is the time the driver needed to complete this lap in seconds
    lap_number INTEGER, -- the number of the current lap where the highest number is the last lap in the race
    stint DOUBLE, -- stint number
    pit_out_time INTERVAL, -- Session time when the car exited the pit
    pit_in_time INTERVAL, -- Session time when the car entered the pit
    sector1_time INTERVAL, -- Recorded sector 1 time
    sector1_time_seconds FLOAT, -- Recorded sector 1 time in seconds
    sector2_time, -- Recorded sector 2 time
    sector2_time_seconds, -- Recorded sector 2 time in seconds
    sector3_time, -- Recorded sector 3 time
    sector3_time_seconds, -- Recorded sector 3 time in seconds
    sector1_session_time INTERVAL, -- Session time when the sector 1 time was set (end of sector 1)
    sector2_session_time INTERVAL, -- Session time when the sector 2 time was set (end of sector 2)
    sector3_session_time INTERVAL, -- Session time when the sector 3 time was set (end of sector 3)
    speed_i1 DOUBLE, -- measured speed at Speedtrap sector 1 in km/h
    speed_i2 DOUBLE, -- measured speed at Speedtrap sector 2 in km/h
    speed_f_l DOUBLE, -- measured speed at Speedtrap finish line in km/h
    speed_s_t DOUBLE, -- measured speed at Speedtrap on the longest straight in km/h
    is_personal_best BOOLEAN, -- Flag that indicates whether this lap is the official personal best lap of a driver of all times.
    compound VARCHAR, -- Tyres compound name
    tyre_life DOUBLE, -- Tyre age in laps
    fresh_tyre BOOLEAN, -- Flag that indicates whether the tyres were fresh at the start of the lap
    team VARCHAR, -- Name of the team the driver is driving for
    lap_start_time INTERVAL, -- Session time at the start of the lap
    lap_start_date TIMESTAMP_NS, -- Timestamp at the start of the lap
    track_status VARCHAR, -- A string that contains track status numbers for all track status that occurred during this lap
    position -- Position of the car at the end of the lap
    deleted -- Indicates that a lap was deleted by the stewards, for example because of a track limits violation.
    deleted_reason VARCHAR -- Gives the reason for a lap time
    is_accurate BOOLEAN -- Indicates that the lap start and end time are synced correctly with other lapsdeletion
    event VARCHAR -- Name of the event
);



### Response:
Based on your instructions, here is the SQL query I have generated to answer the question `{question}`
```sql
"""


@message_handler("chat", ChatData)
async def _(data: ChatData, connection: WebsocketConnection) -> None:
    data_store: Optional[DataStore] = connection.websocket.app.data_store
    if not data_store:
        print("no datastore")
        return

    data_source = data_store.data_source
    if not hasattr(data_source, "sql"):
        print("no sql method")
        print(data_source.__class__)
        return

    try:
        text2sql_completion = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": sql_prompt_race.format(question=data.message),
                }
            ],
            stream=False,
        )

        response = text2sql_completion.choices[0].message.content
        if response is None:
            print("no response")
            response = ""
        print(response)

        sql_statement = response[: response.find("```")]

        print(sql_statement)

        await connection.send_async(
            Message(
                type="chat.response",
                data={
                    "chat_id": data.chat_id,
                    "message": {
                        "role": "context",
                        "content_type": "text/sql",
                        "content": sql_statement,
                        "done": True,
                    },
                },
            )
        )

        full_df: pd.DataFrame = data_source.sql(sql_statement)

        rows = len(full_df.axes[0])
        cols = len(full_df.axes[1])

        if rows * cols > 100:
            df = full_df.head(10)
        else:
            df = full_df

        result_md = df.to_markdown()

        await connection.send_async(
            Message(
                type="chat.response",
                data={
                    "chat_id": data.chat_id,
                    "message": {
                        "role": "context",
                        "content_type": "text/markdown",
                        "content": result_md,
                        "done": True,
                    },
                },
            )
        )

        table_summary_prompt = """
        You are an assistant for question-answering tasks. Use the provided sql query and query result to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
        Question: {question}

        SQL Query: {query}

        Query Result: {query_result}

        Answer:"""

        prompt = table_summary_prompt.format(
            question=data.message, query=sql_statement, query_result=result_md
        )

        completion = await openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )

        async for chunk in completion:
            content = chunk.choices[0].delta.content
            if content:
                await connection.send_async(
                    Message(
                        type="chat.response",
                        data={
                            "chat_id": data.chat_id,
                            "role": "assistant",
                            "message": {
                                "role": "assistant",
                                "content_type": "text/plain",
                                "content": content,
                                "done": False,
                            },
                        },
                    )
                )

        await connection.send_async(
            Message(
                type="chat.response",
                data={
                    "chat_id": data.chat_id,
                    "role": "assistant",
                    "message": {
                        "role": "assistant",
                        "content_type": "text/plain",
                        "content": "",
                        "done": True,
                    },
                },
            )
        )

        if "row_number" in full_df:
            await connection.send_async(
                Message(
                    type="chat.response",
                    data={
                        "chat_id": data.chat_id,
                        "role": "assistant",
                        "message": {
                            "role": "assistant",
                            "content_type": "rows",
                            "content": orjson.dumps(
                                full_df["row_number"].tolist()
                            ).decode(),
                            "done": True,
                        },
                    },
                )
            )

        await connection.send_async(
            Message(
                type="chat.response",
                data={"chat_id": data.chat_id, "done": True},
            )
        )

    except Exception as e:
        logger.exception(e)
        msg = Message(
            type="chat.error",
            data={
                "chat_id": data.chat_id,
                "error": {
                    "type": type(e).__name__,
                    "title": type(e).__name__,
                    "detail": str(e),
                },
            },
        )
        await connection.send_async(msg)
