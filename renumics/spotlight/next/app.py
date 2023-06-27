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

        @self.on_event("startup")
        def _():
            self._receiver_thread = Thread(target=self._receive)
            self._receiver_thread.start()

        @self.get("/")
        def _():
            return "Hello World"

    def _handle_message(self, message):
        kind = message.get("kind")


        if kind is None:
            logger.error(f"Malformed message from client process:\n\t{message}")
            return
        if kind == "datasource":
            try:
                assert isinstance(self.datasource, DataSource)
                self.datasource = message["data"]
            except KeyError:
                logger.error(f"Malformed message from client process:\n\t{message}")
            return

        logger.warning(f"Unknown message from client process:\n\t{message}")
        

    def _receive(self):
        if worker is None:
            # this should never happen
            # maybe fail really hard, if it does?
            return

        while True:
            self._handle_message(worker.connection.recv())

