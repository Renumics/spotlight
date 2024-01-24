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
from openai import OpenAI
from pydantic import BaseModel
from typing_extensions import Literal

from renumics.spotlight.data_store import DataStore
from .exceptions import GenerationIDMismatch, Problem
from .tasks import TaskManager, TaskCancelled
from .tasks.reduction import compute_umap, compute_pca

openai_client = OpenAI()

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

### Input:
Generate a SQL query that answers the question `{question}`.
This query will run on a database whose schema is represented in this string:
CREATE TABLE df (
  time INTERVAL, -- Session time when the lap time was set (end of lap)
  driver VARCHAR, -- Name of the driver as a 3 letter code
  drivernumber VARCHAR, -- Driver identifier
  laptime INTERVAL, -- The recorded lap time is the time the driver needed to complete this lap
  lapnumber DOUBLE, -- the number of the current lap starting with 0 for the first lap
  stint DOUBLE, -- Stint number
  pitouttime INTERVAL, -- Session time when the car exited the pit
  pittntime INTERVAL, -- Session time when the car entered the pit
  sector1time INTERVAL, -- Recorded sector 1 time in nanoseconds
  sector2time INTERVAL, -- Recorded sector 2 time in nanoseconds
  sector3time INTERVAL, -- Recorded sector 3 time in nanoseconds
  sector1sessiontime INTERVAL, -- Session time when the sector 1 time was set (end of sector 1)
  sector2sessiontime INTERVAL, -- Session time when the sector 2 time was set (end of sector 2)
  sector3sessiontime INTERVAL, -- Session time when the sector 3 time was set (end of sector 3)
  speedi1 DOUBLE, -- Speedtrap sector 1 in km/h
  speedi2 DOUBLE, -- Speedtrap sector 2 in km/h
  speedfl DOUBLE, -- Speedtrap finish line in km/h
  speedst DOUBLE, -- Speedtrap on the longest straight in km/h
  ispersonalbest BOOLEAN, -- Flag that indicates whether this lap is the official personal best lap of a driver of all times.
  compound VARCHAR, -- Tyres compound name
  tyrelife DOUBLE, -- Tyre life in laps
  freshtyre BOOLEAN, -- Flag that indicates whether the tyres were fresh at the start of the lap
  team VARCHAR, -- Name of team the driver is driving for
  lapstarttime INTERVAL, -- Session time at the start of the lap
  lapstartdate TIMESTAMP_NS, -- Timestamp at the start of the lap
  trackstatus VARCHAR, -- A string that contains track status numbers for all track status that occurred during this lap
  position DOUBLE -- Position of the car at the end of the lap
  deleted BOOLEAN -- Indicates that a lap was deleted by the stewards, for example because of a track limits violation.
  deletedreason VARCHAR -- Gives the reason for a lap time .
  isaccurate BOOLEAN -- Indicates that the lap start and end time are synced correctly with other lapsdeletion
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

    completion = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": sql_prompt_race.format(question=data.message)}],
        stream=False,
    )

    response = completion.choices[0].message.content
    if response is None:
        print("no response")
        response = ""
    print(response)

    sql_statement = response[:response.find("```")]

    print(sql_statement)

    try:
        df: pd.DataFrame = data_source.sql(sql_statement)
    except:
        df = pd.DataFrame()

    table_summary_prompt = """
    You are an assistant for question-answering tasks. Use the provided sql query result to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
    Question: {question}
    Query Result: {query_result}
    Answer:"""

    print(table_summary_prompt.format(question=data.message, query_result=df.to_markdown()))

    # await connection.send_async(Message(type="chat.response", data={"chat_id": data.chat_id, "message": response}))
    # await connection.send_async(Message(type="chat.response", data={"chat_id": data.chat_id, "message": ""}))

    prompt = table_summary_prompt.format(question=data.message, query_result=df.to_markdown())

    completion = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    for chunk in completion:
        print(chunk.choices[0].delta)
        content = chunk.choices[0].delta.content
        if content:
            await connection.send_async(
                Message(
                    type="chat.response",
                    data={"chat_id": data.chat_id, "message": chunk.choices[0].delta.content},
                )
            )
    await connection.send_async(
        Message(
            type="chat.response",
            data={"chat_id": data.chat_id, "message": ""},
        )
    )


    # res = data_source.sql("SELECT team from f1_laps LIMIT 5")

#     async with httpx.AsyncClient(
#         base_url="http://127.0.0.1:11434/api/", timeout=None
#     ) as ollama_client:
#         res = await ollama_client.post("generate", json={
#             "model": "sqlcoder:15b",
#             "stream": False,
#             "prompt": sql_prompt_race.format(question=data.message)
#         })
#
#         response = res.json()["response"]
#         sql_statement = response[:response.find("```")]
#
#         print(f"sql recieved: {sql_statement}")
#
#         try:
#             df: pd.DataFrame = data_source.sql(sql_statement)
#         except:
#             df = pd.DataFrame()
#
#         # await connection.send_async(Message(type="chat.response", data={"chat_id": data.chat_id, "message": df.to_markdown()}))
#         # await connection.send_async(Message(type="chat.response", data={"chat_id": data.chat_id, "message": ""}))
#
#         table_summary_prompt = """
# You are an assistant for question-answering tasks. Use the provided sql query result to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
# Question: {question}
# Query Result: {query_result}
# Answer:"""
#
#         print(table_summary_prompt.format(question=data.message, query_result=df.to_markdown()))
#
#         async with ollama_client.stream(
#             "POST",
#             "chat",
#             json={
#                 "model": "openhermes2",
#                 "stream": True,
#                 "messages": [{"role": "user", "content": table_summary_prompt.format(question=data.message, query_result=df.to_markdown())}]
#             },
#             timeout=None,
#         ) as stream:
#             async for chunk in stream.aiter_text():
#                 try:
#                     response = json.loads(chunk)
#                 except json.JSONDecodeError:
#                     break
#                 llm_response = response["message"]["content"]
#
#                 await connection.send_async(
#                     Message(
#                         type="chat.response",
#                         data={"chat_id": data.chat_id, "message": llm_response},
#                     )
#                 )
