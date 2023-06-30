import threading

import os
import sys
import secrets
import multiprocessing
import subprocess
import multiprocessing.connection
from typing import List, Optional
from pandas import DataFrame

from renumics.spotlight.backend import create_datasource
from renumics.spotlight.logging import logger

from renumics.spotlight.backend.data_source import DataSource

from renumics.spotlight.typing import PathType

from renumics.spotlight.analysis.typing import DataIssue

from renumics.spotlight.layout.nodes import Layout

class Server():
    host: str
    port: int

    process: Optional[subprocess.Popen]
    connection: Optional[multiprocessing.connection.Connection]
    _connection_thread: threading.Thread
    _connection_authkey: str
    _connection_listener: multiprocessing.connection.Listener

    _datasource: Optional[DataSource]
    _layout: Optional[Layout]

    connected_frontends: int
    _all_frontends_disconnected: threading.Event
    _any_frontend_connected: threading.Event

    def __init__(self, datasource=None, host="127.0.0.1", port=8000):
        self._datasource = datasource
        self._layout = None

        self.host = host
        self.port = port
        self.process = None

        self.connected_frontends = 0
        self._any_frontend_connected = threading.Event()
        self._all_frontends_disconnected = threading.Event()

        self.connection = None
        self._connection_authkey = secrets.token_hex(16)
        self._connection_listener = multiprocessing.connection.Listener(('127.0.0.1', 0), authkey=self._connection_authkey.encode())

        self._connection_thread = threading.Thread(target=self._handle_connections, daemon=True)
        self._connection_thread.start()
        # TODO: wait for connection thread to listen

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
    def datasource(self, datasource: Optional[DataSource]):
        self._datasource = datasource
        self.send({"kind": "set_datasource", "data": datasource})

    @property
    def layout(self):
        return self._layout

    @layout.setter
    def layout(self, value):
        self._layout = value
        self.send({"kind": "set_layout", "data": value})

    def set_custom_issues(self, issues: List[DataIssue]):
        self.send({"kind": "set_custom_issues", "data": issues})

    # TODO: pass this stuff as a combined configuration object?
    def set_analyze_issues(self, value: bool):
        self.send({"kind": "set_analyze", "data": value})

    def set_project_root(self, value: PathType):
        self.send({"kind": "set_project_root", "data": value})

    def set_filebrowsing_allowed(self, value: bool):
        self.send({"kind": "set_filebrowsing_allowed", "data": value})

    def _handle_message(self, message):
        try:
            kind = message["kind"]
        except KeyError:
            logger.error(f"Malformed message from client process:\n\t{message}")
            return

        if kind == "startup":
            self.send({"kind": "set_datasource", "data": self.datasource})
            return

        if kind == "frontend_connected":
            self.connected_frontends = message["data"]
            self._all_frontends_disconnected.clear()
            self._any_frontend_connected.set()
            return

        if kind == "frontend_disconnected":
            self.connected_frontends = message["data"]
            if self.connected_frontends == 0:
                self._any_frontend_connected.clear()
                self._all_frontends_disconnected.set()
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

    def wait_for_frontend_disconnect(self, grace_period=5):
        """
        Wait for all frontends to disconnect
        """
        
        while True:
            print("waiting")
            self._all_frontends_disconnected.wait()
            print("grace_period")
            if not self._any_frontend_connected.wait(timeout=grace_period):
                return



def show(df: DataFrame):
    # create datasource
    datasource = create_datasource(df)

    # setup server process
    server = Server(datasource)
    server.start()

    return server
