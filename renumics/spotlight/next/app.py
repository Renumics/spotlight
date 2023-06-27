from threading import Thread
from typing import Optional
from fastapi import FastAPI

from renumics.spotlight.backend.data_source import DataSource
from .uvicorn_worker import worker

from renumics.spotlight.logging import logger

class SpotlightApp(FastAPI):
    _receiver_thread: Thread
    datasource: Optional[DataSource]

    def __init__(self):
        super().__init__()
        self.datasource = None

        @self.on_event("startup")
        def _():
            self._receiver_thread = Thread(target=self._receive)
            self._receiver_thread.start()
            print(self.connection)
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
                datasource = message["data"]
                assert isinstance(datasource, DataSource)
                self.datasource = datasource
            except KeyError:
                logger.error(f"Malformed message from client process:\n\t{message}")
            return

        logger.warning(f"Unknown message from client process:\n\t{message}")


    def _receive(self):
        while True:
            self._handle_message(self.connection.recv())
