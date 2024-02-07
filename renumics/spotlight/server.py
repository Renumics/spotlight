"""
Local proxy object for the spotlight server process
"""

import atexit
import multiprocessing
import multiprocessing.connection
import os
import platform
import secrets
import signal
import socket
import subprocess
import sys
import threading
from queue import Empty, Queue
from typing import Any, Optional

import pandas as pd

from renumics.spotlight.app_config import AppConfig
from renumics.spotlight.develop.vite import Vite
from renumics.spotlight.logging import logger
from renumics.spotlight.settings import settings


class Server:
    """
    Local proxy object for the spotlight server process
    """

    _host: str
    _port: int
    _requested_port: int

    _vite: Optional[Vite]

    process: Optional[subprocess.Popen]

    _startup_event: threading.Event
    _update_complete_event: threading.Event
    _update_error: Optional[Exception]

    connection: Optional[multiprocessing.connection.Connection]
    _connection_message_queue: Queue
    _connection_thread: threading.Thread
    _connection_thread_online: threading.Event
    _connection_authkey: str
    _connection_listener: multiprocessing.connection.Listener

    _df_receive_queue: Queue

    connected_frontends: int
    _all_frontends_disconnected: threading.Event
    _any_frontend_connected: threading.Event

    def __init__(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        self._vite = None

        self._app_config = AppConfig()

        self._host = host
        self._requested_port = port
        self._port = self._requested_port
        self.process = None

        self.connected_frontends = 0
        self._any_frontend_connected = threading.Event()
        self._all_frontends_disconnected = threading.Event()

        self.connection = None
        self._connection_message_queue = Queue()
        self._connection_authkey = secrets.token_hex(16)
        self._connection_listener = multiprocessing.connection.Listener(
            ("127.0.0.1", 0), authkey=self._connection_authkey.encode()
        )

        self._startup_event = threading.Event()
        self._update_complete_event = threading.Event()

        self._connection_thread_online = threading.Event()
        self._connection_thread = threading.Thread(
            target=self._handle_connections, daemon=True
        )

        self._df_receive_queue = Queue()

        atexit.register(self.stop)

    def __del__(self) -> None:
        self.stop()
        atexit.unregister(self.stop)

    def start(self, config: AppConfig) -> None:
        """
        Start the server process, if it is not running already
        """
        if self.process:
            return

        self._app_config = config

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

        sock = socket.socket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self._host, self._port))
        self._port = sock.getsockname()[1]

        command = [
            sys.executable,
            "-m",
            "uvicorn",
            "renumics.spotlight.app:SpotlightApp",
            "--host",
            self._host,
            "--log-level",
            "critical",
            "--http",
            "httptools",
            "--ws",
            "websockets",
            "--timeout-graceful-shutdown",
            str(2),
            "--factory",
        ]
        if platform.system() == "Windows":
            command += ["--port", str(self._port)]
            sock.close()
        else:
            command += ["--fd", str(sock.fileno())]

        if settings.dev:
            command.append("--reload")

        # start uvicorn
        self.process = subprocess.Popen(
            command,
            env=env,
            pass_fds=() if platform.system() == "Windows" else (sock.fileno(),),
            creationflags=(
                subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore
                if platform.system() == "Windows"
                else 0
            ),
            stdout=None if settings.verbose else subprocess.DEVNULL,
            stderr=None if settings.verbose else subprocess.DEVNULL,
        )
        if platform.system() != "Windows":
            sock.close()
        self._wait_for_update()

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
            if platform.system() == "Windows":
                self.process.send_signal(signal.CTRL_C_EVENT)  # type: ignore
                try:
                    self.process.wait(1)
                except subprocess.TimeoutExpired:
                    self.process.send_signal(signal.CTRL_BREAK_EVENT)  # type: ignore
            else:
                self.process.kill()
        self.process.wait(1)
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

    def update(self, config: AppConfig) -> None:
        """
        Update app config
        """
        self._update(config)
        self._wait_for_update()

    def _update(self, config: AppConfig) -> None:
        self._app_config = config
        self.send({"kind": "update", "data": config})

    def _wait_for_update(self) -> None:
        self._update_complete_event.wait(timeout=120)
        self._update_complete_event.clear()
        err = self._update_error
        self._update_error = None
        if err:
            raise err

    def get_df(self) -> Optional[pd.DataFrame]:
        """
        Request and return the current DafaFrame from the server process (if possible)
        """
        self.send({"kind": "get_df"})
        return self._df_receive_queue.get(block=True)

    def _handle_message(self, message: Any) -> None:
        try:
            kind = message["kind"]
        except KeyError:
            logger.error(f"Malformed message from client process:\n\t{message}")
            return

        if kind == "startup":
            self._startup_event.set()
            self._update(self._app_config)
        elif kind == "update_complete":
            self._update_error = message.get("error")
            self._update_complete_event.set()
        elif kind == "frontend_connected":
            self.connected_frontends = message["data"]
            self._all_frontends_disconnected.clear()
            self._any_frontend_connected.set()
        elif kind == "frontend_disconnected":
            self.connected_frontends = message["data"]
            if self.connected_frontends == 0:
                self._any_frontend_connected.clear()
                self._all_frontends_disconnected.set()
        elif kind == "df":
            self._df_receive_queue.put(message["data"])
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

    def refresh_frontends(self) -> None:
        """
        Refresh all connected frontends
        """
        self.send({"kind": "refresh_frontends"})

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

    def wait_for_frontend_disconnect(self, grace_period: float = 5) -> None:
        """
        Wait for all frontends to disconnect
        """

        while True:
            self._all_frontends_disconnected.wait()
            if not self._any_frontend_connected.wait(timeout=grace_period):
                return
