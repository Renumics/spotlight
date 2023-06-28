from threading import Thread

import os
import sys
import secrets
import multiprocessing
import subprocess
import multiprocessing.connection
from typing import Optional
from pandas import DataFrame

from renumics.spotlight.backend import create_datasource
from renumics.spotlight.logging import logger

from renumics.spotlight.backend.data_source import DataSource

class Server():
    process: Optional[subprocess.Popen]
    connection: multiprocessing.connection.Connection
    _datasource: Optional[DataSource]
    host: str
    port: int
    _connection_thread: Thread
    _connection_authkey: str
    _connection_listener: multiprocessing.connection.Listener

    def __init__(self, datasource=None, host="127.0.0.1", port=8000):
        self._datasource = datasource
        self.host = host
        self.port = port
        self.process = None

        # TODO: launch a fresh python process with Popen 
        #       to prevent problems with unprotected entrypoints in user scripts
        #self.process = multiprocessing.Process(target=_server_entrypoint, args=(server_connection,))

        self._connection_authkey = secrets.token_hex(16)
        self._connection_listener = multiprocessing.connection.Listener(('127.0.0.1', 0), authkey=self._connection_authkey.encode())

        self._connection_thread = Thread(target=self._handle_connections, daemon=True)
        self._connection_thread.start()

    def start(self):
        """
        Start the server process, if it is not running already
        """
        # TODO: setup and pass port if port is 0

        if not self.process:
            env = { 
               **os.environ.copy(),
               "CONNECTION_PORT": str(self._connection_listener.address[1]),
               "CONNECTION_AUTHKEY": self._connection_authkey,
            }
            self.process = subprocess.Popen([sys.executable, "-m", "uvicorn", 
                                             "renumics.spotlight.next.app:SpotlightApp",
                                             "--host", self.host,
                                             "--port", str(self.port), 
                                             "--reload",
                                             "--log-level", "debug",
                                             "--http", "httptools",
                                             "--ws", "websockets",
                                             "--timeout-graceful-shutdown", str(5),
                                             "--factory"
                                             ], env=env)

    def stop(self):
        """
        Stop the server process if it is running
        """
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(3)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

        self._connection_thread.join(0.1)

    @property
    def running(self):
        """
        Is the server process running?
        """
        return self.process is not None

    @property
    def datasource(self):
        return self._datasource

    @datasource.setter
    def datasource(self, datasource: DataSource):
        self._datasource = datasource
        self.send({"kind": "datasource", "data": datasource})

    def _handle_message(self, message):
        try:
            kind = message["kind"]
        except KeyError:
            logger.error(f"Malformed message from client process:\n\t{message}")
            return

        if kind == "startup":
            self.send({"kind": "datasource", "data": self.datasource})
            return

        logger.warning(f"Unknown message from client process:\n\t{message}")

    def send(self, message):
        # TODO: queue messages when no connection is available

        if self.connection:
            self.connection.send(message)

    def _handle_connections(self):
        while True:
            self.connection = self._connection_listener.accept()
            while True:
                try:
                    msg = self.connection.recv()
                except EOFError:
                    break
                self._handle_message(msg)

def show(df: DataFrame):
    # create datasource
    datasource = create_datasource(df)

    # setup server process
    server = Server(datasource)
    server.start()

    return server
