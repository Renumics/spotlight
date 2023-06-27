from threading import Thread

import multiprocessing
import multiprocessing.connection
from typing import Optional
from pandas import DataFrame

from renumics.spotlight.backend import create_datasource
from renumics.spotlight.logging import logger

from renumics.spotlight.backend.data_source import DataSource
from .gunicorn import StandaloneApplication

def _server_entrypoint(connection: multiprocessing.connection.Connection):
    application = StandaloneApplication("renumics.spotlight.next.app:SpotlightApp", connection, {"worker_class": "renumics.spotlight.next.uvicorn_worker.RestartableUvicornWorker", "reload": True, "bind": "localhost:8000", "reuse_port": True})
    application.run()


class Server():
    process: multiprocessing.Process
    connection: multiprocessing.connection.Connection
    _datasource: Optional[DataSource]

    def __init__(self, datasource=None):
        self._datasource = datasource
        self.connection, server_connection = multiprocessing.Pipe()
        self.process = multiprocessing.Process(target=_server_entrypoint, args=(server_connection,))
        self._receiver_thread = Thread(target=self._receive)
        self._receiver_thread.start()

    def start(self):
        self.process.start()

    def stop(self):
        self.process.kill()

    @property
    def datasource(self):
        return self._datasource

    @datasource.setter
    def datasource(self, datasource: DataSource):
        self._datasource = datasource
        self.connection.send({"kind": "datasource", "data": datasource})

    def _handle_message(self, message):
        try:
            kind = message["kind"]
        except KeyError:
            logger.error(f"Malformed message from client process:\n\t{message}")
            return

        if kind == "startup":
            self.connection.send({"kind": "datasource", "data": self.datasource})
            return

        logger.warning(f"Unknown message from client process:\n\t{message}")


    def _receive(self):
        while True:
            self._handle_message(self.connection.recv())

def show(df: DataFrame):
    # create datasource
    datasource = create_datasource(df)

    # setup server process
    server = Server(datasource)
    server.start()

    return server
