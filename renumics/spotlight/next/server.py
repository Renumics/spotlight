import threading
import queue
import socket
import atexit
from concurrent.futures import Future

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
from renumics.spotlight.settings import settings

from renumics.spotlight.develop.vite import Vite

class Server():
    _host: str
    _port: int
    _requested_port: int

    _vite: Optional[Vite]

    process: Optional[subprocess.Popen]

    connection: Optional[multiprocessing.connection.Connection]
    _connection_message_queue: queue.Queue
    _connection_thread: threading.Thread
    _connection_thread_online: threading.Event
    _connection_authkey: str
    _connection_listener: multiprocessing.connection.Listener

    _datasource: Optional[DataSource]
    _layout: Optional[Layout]

    connected_frontends: int
    _all_frontends_disconnected: threading.Event
    _any_frontend_connected: threading.Event

    _datasource_up_to_date: threading.Event

    def __init__(self, host="127.0.0.1", port=8000) -> None:
        self._layout = None

        self._vite = None

        self._host = host
        self._requested_port = port
        self._port = self._requested_port
        self.process = None

        self.connected_frontends = 0
        self._any_frontend_connected = threading.Event()
        self._all_frontends_disconnected = threading.Event()

        self._datasource_up_to_date = threading.Event()

        self.connection = None
        self._connection_message_queue = queue.Queue()
        self._connection_authkey = secrets.token_hex(16)
        self._connection_listener = multiprocessing.connection.Listener(('127.0.0.1', 0), authkey=self._connection_authkey.encode())
        self._connection_thread_online = threading.Event()
        self._connection_thread = threading.Thread(target=self._handle_connections, daemon=True)

        atexit.register(self.stop)

    def __del__(self) -> None:
        atexit.unregister(self.stop)

    def start(self):
        """
        Start the server process, if it is not running already
        """
        if self.process:
            return
        
        # launch connection thread
        self._connection_thread = threading.Thread(target=self._handle_connections, daemon=True)
        self._connection_thread.start()
        self._connection_thread_online.wait()
        env = { 
           **os.environ.copy(),
           "CONNECTION_PORT": str(self._connection_listener.address[1]),
           "CONNECTION_AUTHKEY": self._connection_authkey,
        }

        # start vite in dev mode
        if settings.dev:
            self._vite = Vite()
            self._vite.start()
            env["VITE_URL"]  = self._vite.url

        # automatic port selection
        if self._requested_port == 0:
            sock = socket.socket()
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self._host, self._port))
            self._port = sock.getsockname()[1]

        # start uvicorn
        self.process = subprocess.Popen([sys.executable, "-m", "uvicorn", 
                                         "renumics.spotlight.next.app:SpotlightApp",
                                         "--host", self._host,
                                         "--port", str(self._port), 
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
        if not self.process:
            return 

        if self._vite:
            self._vite.stop()

        self.process.terminate()
        try:
            self.process.wait(3)
        except subprocess.TimeoutExpired:
            self.process.kill()
        self.process = None

        self._connection_thread.join(0.1)
        self._connection_thread_online.clear()

        self._port = self._requested_port

    @property
    def running(self):
        """
        Is the server process running?
        """
        return self.process is not None

    @property
    def port(self):
        """
        The server's tcp port
        """
        return self._port

    @property
    def datasource(self):
        # request datasource from app
        self.send({"kind": "get_datasource"})
        # wait for datasource update
        self._datasource_up_to_date.wait()
        self._datasource_up_to_date.clear()
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

    def set_analyze_issues(self, value: bool):
        self.send({"kind": "set_analyze", "data": value})

    def set_project_root(self, value: PathType):
        self.send({"kind": "set_project_root", "data": value})

    def set_filebrowsing_allowed(self, value: bool):
        self.send({"kind": "set_filebrowsing_allowed", "data": value})

    def refresh_frontends(self):
        self.send({"kind": "refresh_frontends"})
    
        
    def _handle_message(self, message):
        try:
            kind = message["kind"]
        except KeyError:
            logger.error(f"Malformed message from client process:\n\t{message}")
            return

        if kind == "startup":
            self.send({"kind": "set_datasource", "data": self._datasource})
        elif kind == "frontend_connected":
            self.connected_frontends = message["data"]
            self._all_frontends_disconnected.clear()
            self._any_frontend_connected.set()
        elif kind == "frontend_disconnected":
            self.connected_frontends = message["data"]
            if self.connected_frontends == 0:
                self._any_frontend_connected.clear()
                self._all_frontends_disconnected.set()
        elif kind == "datasource":
            self._datasource = message["data"]
            self._datasource_up_to_date.set()
        else:
            logger.warning(f"Unknown message from client process:\n\t{message}")

    def send(self, message, queue=False):
        if self.connection:
            self.connection.send(message)
        elif queue: 
            self._connection_message_queue.put(message)

    def _handle_connections(self):
        self._connection_thread_online.set()
        while True:
            self.connection = self._connection_listener.accept()

            # send messages from queue
            while True: 
                try:
                    message = self._connection_message_queue.get(block=False)
                except queue.Empty:
                    break
                else:
                    self.connection.send(message)
                    self._connection_message_queue.task_done()

            while True:
                try:
                    msg = self.connection.recv()
                except EOFError:
                    self.connection = None
                    break
                self._handle_message(msg)

    def wait_for_frontend_disconnect(self, grace_period=5):
        """
        Wait for all frontends to disconnect
        """
        
        while True:
            self._all_frontends_disconnected.wait()
            if not self._any_frontend_connected.wait(timeout=grace_period):
                return
