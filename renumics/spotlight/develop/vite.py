"""Manage vitejs dev server for local (plugin) development"""

import socket
import subprocess
from typing import Optional

import requests
from requests.adapters import HTTPAdapter, Retry

from .project import get_project_info


def find_free_port() -> int:
    """find a free tcp port"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("", 0))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return sock.getsockname()[1] or 0


def wait_for(url: str) -> None:
    """
    Wait for url to become available
    """

    session = requests.Session()
    retries = Retry(total=100, backoff_factor=0.1)
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.head(url, timeout=30)


class Vite:
    """
    Vite Development Server
    """

    process: Optional[subprocess.Popen]
    port: Optional[int]

    def __init__(self) -> None:
        self.port = None
        self.pid = None

    @property
    def running(self) -> bool:
        """
        Is the server running atm?
        """
        return self.port is not None

    @property
    def url(self) -> str:
        """
        The base url of the vite dev server
        """
        return f"http://localhost:{self.port}"

    def start(self) -> int:
        """
        Launch vite on random port.
        """

        if self.port:
            return self.port

        cwd = get_project_info().root or "."

        self.port = find_free_port()
        self.process = subprocess.Popen(
            ["pnpm", "exec", "vite", "--port", str(self.port)], cwd=cwd
        )
        # wait for vite to start (upto 30 seconds)
        wait_for(self.url)

        return self.port

    def stop(self) -> None:
        """
        Stop running instance of vite.
        """

        if not self.process:
            return

        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()

        self.process = None
        self.port = None
