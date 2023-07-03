"""
Local proxy object for the spotlight server process
"""

import threading
from queue import Queue, Empty
import socket
import atexit

import os
import sys
import secrets
import multiprocessing
import multiprocessing.connection
import subprocess
from typing import List, Optional, Any

from renumics.spotlight.logging import logger
from renumics.spotlight.backend.data_source import DataSource
from renumics.spotlight.typing import PathType
from renumics.spotlight.analysis.typing import DataIssue
from renumics.spotlight.layout.nodes import Layout
from renumics.spotlight.settings import settings

from renumics.spotlight.develop.vite import Vite


class Server:
    """
    Local proxy object for the spotlight server process
    """

    # pylint: disable=too-many-instance-attributes

    _host: str
    _port: int
    _requested_port: int

    _vite: Optional[Vite]

    process: Optional[subprocess.Popen]

    _startup_event: threading.Event

    connection: Optional[multiprocessing.connection.Connection]
    _connection_message_queue: Queue
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

    def __init__(self, host: str = "127.0.0.1", port: int = 8000) -> None:
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
        self._connection_message_queue = Queue()
        self._connection_authkey = secrets.token_hex(16)
        self._connection_listener = multiprocessing.connection.Listener(
            ("127.0.0.1", 0), authkey=self._connection_authkey.encode()
        )

        self._startup_event = threading.Event()
        self._connection_thread_online = threading.Event()
        self._connection_thread = threading.Thread(
            target=self._handle_connections, daemon=True
        )

        atexit.register(self.stop)

    def __del__(self) -> None:
        atexit.unregister(self.stop)

    def start(self) -> None:
        """
        Start the server process, if it is not running already
        """
        if self.process:
            return

        # launch connection thread
        self._connection_thread = threading.Thread(
            target=self._handle_connections, daemon=True
        )
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
            env["VITE_URL"] = self._vite.url

        # automatic port selection
        if self._requested_port == 0:
            sock = socket.socket()
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self._host, self._port))
            self._port = sock.getsockname()[1]

        # start uvicorn
        # pylint: disable=consider-using-with
        self.process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "renumics.spotlight.app:SpotlightApp",
                "--host",
                self._host,
                "--port",
                str(self._port),
                "--reload",
                "--log-level",
                "debug",
                "--http",
                "httptools",
                "--ws",
                "websockets",
                "--timeout-graceful-shutdown",
                str(5),
                "--factory",
            ],
            env=env,
        )

    def stop(self) -> None:
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

        self._startup_event.clear()

    @property
    def running(self) -> bool:
        """
        Is the server process running?
        """
        return self.process is not None

    @property
    def port(self) -> int:
        """
        The server's tcp port
        """
        return self._port

    @property
    def datasource(self) -> Optional[DataSource]:
        """
        The current datasource
        """
        # request datasource from app
        self.send({"kind": "get_datasource"})
        # wait for datasource update
        self._datasource_up_to_date.wait()
        self._datasource_up_to_date.clear()
        return self._datasource

    @datasource.setter
    def datasource(self, datasource: Optional[DataSource]) -> None:
        self._datasource = datasource
        self.send({"kind": "set_datasource", "data": datasource})

    @property
    def layout(self) -> Optional[Layout]:
        """
        The configured fronted layout
        """
        return self._layout

    @layout.setter
    def layout(self, value: Layout) -> None:
        self._layout = value
        self.send({"kind": "set_layout", "data": value})

    def set_custom_issues(self, issues: List[DataIssue]) -> None:
        """
        Set the user supplied issues on the server
        """
        self.send({"kind": "set_custom_issues", "data": issues})

    def set_analyze_issues(self, value: bool) -> None:
        """
        Enable automatic issue analysis
        """
        self.send({"kind": "set_analyze", "data": value})

    def set_project_root(self, value: PathType) -> None:
        """
        Set the project root
        """
        self.send({"kind": "set_project_root", "data": value})

    def set_filebrowsing_allowed(self, value: bool) -> None:
        """
        (Dis)allow filebrowsing
        """
        self.send({"kind": "set_filebrowsing_allowed", "data": value})

    def refresh_frontends(self) -> None:
        """
        Refresh all connected frontends
        """
        self.send({"kind": "refresh_frontends"})

    def _handle_message(self, message: Any) -> None:
        try:
            kind = message["kind"]
        except KeyError:
            logger.error(f"Malformed message from client process:\n\t{message}")
            return

        if kind == "startup":
            self.send({"kind": "set_datasource", "data": self._datasource})
            self._startup_event.set()
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

    def send(self, message: Any, queue: bool = False) -> None:
        """
        Send a messge to the server process
        """
        if self.connection:
            self.connection.send(message)
        elif queue:
            self._connection_message_queue.put(message)

    def _handle_connections(self) -> None:
        self._connection_thread_online.set()
        while True:
            self.connection = self._connection_listener.accept()

            # send messages from queue
            while True:
                try:
                    message = self._connection_message_queue.get(block=False)
                except Empty:
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

    def wait_for_startup(self) -> None:
        """
        Wait for server to startup
        """
        self._startup_event.wait()

    def wait_for_frontend_disconnect(self, grace_period: float = 5) -> None:
        """
        Wait for all frontends to disconnect
        """

        while True:
            self._all_frontends_disconnected.wait()
            if not self._any_frontend_connected.wait(timeout=grace_period):
                return
