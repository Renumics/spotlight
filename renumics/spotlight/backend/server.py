"""
Setup for Spotlight server and browser.
"""

import os
import threading
import time
import socket
from pathlib import Path
from typing import Iterable, Union, cast
from urllib.parse import unquote, urlsplit

import requests
import uvicorn
from loguru import logger
from typing_extensions import Literal

from renumics.spotlight.typing import PathType
from .app import SpotlightApp, create_app


class Timeout(Exception):
    """
    Spotlight not started in time.
    """


class Server(uvicorn.Server):
    """
    Our custom Uvicorn server.
    """

    @property
    def app(self) -> SpotlightApp:
        """
        The server's app object
        """
        return cast(SpotlightApp, self.config.app)

    def run_in_thread(self) -> threading.Thread:
        """
        Run Uvicorn in separate thread.
        """
        sock = socket.socket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.config.host, self.config.port))
        self.config.port = sock.getsockname()[1]

        thread = threading.Thread(
            target=self.run, kwargs={"sockets": [sock]}, daemon=True
        )
        thread.start()

        # Wait 2 seconds for server to start.
        for _ in range(20):
            if self.started:
                return thread
            if not thread.is_alive():
                break
            time.sleep(0.1)

        raise Timeout("Spotlight not started in time.")


def download_table(
    url: str,
    supported_extensions: Iterable[str],
    workdir: PathType = ".",
    timeout: int = 30,
) -> str:
    """
    Download a table file with one of the supported extensions form the given
    URL and save it to the `workdir` with the original name.
    If a file with original name already exists, add numeric suffix to its name.

    Returns:
        Path to the downloaded table file.
    """
    filename = unquote(urlsplit(url).path).split("/")[-1]
    if not filename:
        raise ValueError("Cannot parse file name from the given URL.")
    if not any(filename.endswith(ext) for ext in supported_extensions):
        raise ValueError(
            "Invalid file extension parsed from the given URL.\n"
            "Supported are: " + ", ".join(supported_extensions)
        )
    table_folder = Path(workdir)
    # If a file exists at the given path, `FileExistsError` will be raised.
    table_folder.mkdir(parents=True, exist_ok=True)

    logger.info(f"Downloading '{url}'.")
    response = requests.get(url, timeout=timeout)
    if not response.ok:
        raise ValueError("Given URL could not be reached.")

    table_path = table_folder / filename
    stem = table_path.stem
    idx = 1
    while table_path.is_file():
        table_path = table_path.with_name(stem + f"({idx})").with_suffix(
            table_path.suffix
        )
        idx += 1
    with table_path.open("wb") as f:
        f.write(response.content)
    return str(table_path)


def create_server(
    host: str = "localhost",
    port: Union[int, str] = "auto",
    log_level: Union[
        int, Literal["trace", "debug", "info", "warning", "error", "critical"]
    ] = "critical",
) -> Server:
    """
    Prepare Renumics Spotlight server for launching.
    """

    app = create_app()

    if port == "auto":
        port_number = 0
    else:
        port_number = int(port)

    config = uvicorn.Config(
        app,
        host=host,
        port=port_number,
        log_level=log_level,
        http="httptools",
        ws="wsproto",
        workers=4,
        reload=os.environ.get("SPOTLIGHT_DEV") == "true",
    )
    server = Server(config)
    return server
