"""
This module allows user to start Spotlight from a python script/notebook.

Example:
    >>> import time
    >>> from renumics import spotlight
    >>> with spotlight.Dataset("docs/example.h5", "w") as dataset:
    ...     pass  # Create empty dataset
    >>> spotlight.viewers()
    []
    >>> spotlight.show("docs/example.h5", "127.0.0.1", port=5001, no_browser=True, wait=False)
    Spotlight running on http://127.0.0.1:5001/
    http://127.0.0.1:5001/
    >>> spotlight.viewers()
    [http://127.0.0.1:5001/]
    >>> spotlight.close()
    >>> spotlight.viewers()
    []

Example:
    >>> import time
    >>> from renumics import spotlight
    >>> with spotlight.Dataset("docs/example.h5", "w") as dataset:
    ...     pass  # Create empty dataset
    >>> viewer = spotlight.show(
    ...     "docs/example.h5",
    ...     "127.0.0.1", port=5001,
    ...     no_browser=True,
    ...     wait=False
    ... )
    Spotlight running on http://127.0.0.1:5001/
    >>> viewer
    http://127.0.0.1:5001/
    >>> spotlight.close()

Example:
    >>> import time
    >>> import pandas as pd
    >>> from renumics import spotlight
    >>> df = pd.DataFrame({"a":[0, 1, 2], "b":["x", "y", "z"]})
    >>> viewer = spotlight.show(df, "127.0.0.1", port=5001, no_browser=True, wait=False)
    Spotlight running on http://127.0.0.1:5001/
    >>> viewer
    http://127.0.0.1:5001/
    >>> viewer.df["a"].to_list()
    [0, 1, 2]
    >>> spotlight.close()

"""

import os
from pathlib import Path
import threading
from typing import List, Union, Optional, Dict, Type

import pandas as pd
from typing_extensions import Literal
import ipywidgets as widgets
import IPython.display

import __main__
from renumics.spotlight.webbrowser import launch_browser_in_thread
from renumics.spotlight.dataset import ColumnType
from renumics.spotlight.layout import _LayoutLike, parse
from renumics.spotlight.backend.server import create_server, Server
from renumics.spotlight.backend.websockets import RefreshMessage
from renumics.spotlight.backend import create_datasource
from renumics.spotlight.develop.vite import Vite
from renumics.spotlight.settings import settings

from renumics.spotlight.dtypes.typing import ColumnTypeMapping

from renumics.spotlight.typing import is_pathtype


class ViewerNotFoundError(Exception):
    """
    Raised if a Spotlight viewer is not found.
    """


class Viewer:
    """
    A Spotlight viewer. It corresponds to a single running Spotlight instance.

    Viewer can be created using the :func:`show` function.

    Attributes:
        host: host at which Spotlight is running
        port: port at which Spotlight is running
    """

    _thread: Optional[threading.Thread]
    _server: Server
    _vite: Optional[Vite]

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: Union[int, Literal["auto"]] = "auto",
        log_level: Union[
            int, Literal["trace", "debug", "info", "warning", "error", "critical"]
        ] = "critical",
    ) -> None:
        self._server = create_server(host, port, log_level=log_level)
        self._thread = None
        if settings.dev:
            self._vite = Vite()
        else:
            self._vite = None
        _VIEWERS.append(self)

    # pylint: disable=too-many-arguments
    def show(
        self,
        dataset_or_folder: Optional[Union[str, os.PathLike, pd.DataFrame]] = None,
        layout: Optional[_LayoutLike] = None,
        no_browser: bool = False,
        wait: Union[bool, Literal["auto"]] = "auto",
        dtype: Optional[ColumnTypeMapping] = None,
    ) -> None:
        """
        Show a dataset or folder in this spotlight viewer.

        Args:
            dataset_or_folder: root folder, dataset file or pandas.DataFrame (df) to open.
            layout: optional Spotlight :mod:`layout <renumics.spotlight.layout>`.
            no_browser: do not show Spotlight in browser.
            wait: If `True`, block code execution until all Spotlight browser tabs are closed.
                If `False`, continue code execution after Spotlight start.
                If "auto" (default), choose the mode automatically: non-blocking for
                `jupyter notebook`, `ipython` and other interactive sessions;
                blocking for scripts.
            log_level: optional log level to use in Spotlight server. In notebooks,
                server's output will be printed in the last visited cell, so low log
                levels can be confusing.
            dtype: Optional dict with mapping `column name -> column type` with
                column types allowed by Spotlight (for dataframes only).
        """

        if dataset_or_folder is None:
            dataset_or_folder = Path.cwd()

        in_interactive_session = not hasattr(__main__, "__file__")
        if wait == "auto":
            # `__main__.__file__` is not set in an interactive session, do not wait then.
            wait = not in_interactive_session

        app = self._server.app

        # set correct project folder
        if is_pathtype(dataset_or_folder):
            path = Path(dataset_or_folder).absolute()
            if path.is_dir():
                app.project_root = path
            else:
                app.project_root = path.parent
                app.data_source = create_datasource(path, dtype=dtype)
        else:
            app.data_source = create_datasource(dataset_or_folder, dtype=dtype)

        app.layout = None if layout is None else parse(layout)
        self.refresh()

        if not self.running:
            if self._vite:
                self._vite.start()
                app.vite_url = self._vite.url

            self._thread = self._server.run_in_thread()

            if self not in _VIEWERS:
                _VIEWERS.append(self)

        if not in_interactive_session or wait:
            print(f"Spotlight running on http://{self.host}:{self.port}/")

        if not no_browser:
            self.open_browser()
        if wait:
            self.close(True)

    def close(self, wait: bool = False) -> None:
        """
        Shutdown the corresponding Spotlight instance.
        """
        if self not in _VIEWERS:
            return

        _VIEWERS.remove(self)

        if self._thread is None:
            return

        if self._vite:
            self._vite.stop()

        if wait:
            wait_event = threading.Event()
            timer: Optional[threading.Timer] = None

            def stop() -> None:
                wait_event.set()

            def on_connect(_: int) -> None:
                nonlocal timer
                if timer:
                    timer.cancel()
                    timer = None

            def on_disconnect(active_connections: int) -> None:
                if not active_connections:
                    ## create timer
                    nonlocal timer
                    timer = threading.Timer(3, stop)
                    timer.start()

            self._server.app.websocket_manager.add_disconnect_callback(on_disconnect)
            self._server.app.websocket_manager.add_connect_callback(on_connect)
            try:
                wait_event.wait()
            except KeyboardInterrupt as e:
                # cleanup on KeyboarInterrupt to prevent zombie processes
                self.close(wait=False)
                raise e

        self._server.should_exit = True
        self._thread.join()
        self._thread = None

    def open_browser(self) -> None:
        """
        Open the corresponding Spotlight instance in a browser.
        """
        launch_browser_in_thread(self.host, self.port)

    def refresh(self) -> None:
        """
        Refresh the corresponding Spotlight instance in a browser.
        """
        if self.running:
            self._server.app.websocket_manager.broadcast(RefreshMessage())

    @property
    def running(self) -> bool:
        """
        True if the viewer's webserver is running, false otherwise.
        """
        return self._thread is not None

    @property
    def df(self) -> Optional[pd.DataFrame]:
        """
        Get served `DataFrame` if a `DataFrame` is served, `None` otherwise.
        """
        if self._server.app.data_source:
            return self._server.app.data_source.df
        return None

    @property
    def host(self) -> str:
        """
        The configured host setting.
        """
        return self._server.config.host

    @property
    def port(self) -> int:
        """
        The port the viewer is running on.
        """
        return self._server.config.port

    def __repr__(self) -> str:
        return f"http://{self.host}:{self.port}/"

    def _ipython_display_(self) -> None:
        if self._server.should_exit:
            return

        # pylint: disable=undefined-variable
        if get_ipython().__class__.__name__ == "ZMQInteractiveShell":  # type: ignore
            # in notebooks display a rich html widget

            label = widgets.Label(
                f"Spotlight running on http://{self.host}:{self.port}/"
            )
            open_button = widgets.Button(
                description="open", tooltip="Open spotlight viewer"
            )
            close_button = widgets.Button(description="stop", tooltip="Stop spotlight")

            def on_click_open(_: widgets.Button) -> None:
                self.open_browser()

            open_button.on_click(on_click_open)

            def on_click_close(_: widgets.Button) -> None:
                open_button.disabled = True
                close_button.disabled = True
                label.value = "Spotlight stopped"
                self.close()

            close_button.on_click(on_click_close)

            IPython.display.display(
                widgets.VBox([label, widgets.HBox([open_button, close_button])])
            )
        else:
            print(self)


_VIEWERS: List[Viewer] = []


def viewers() -> List[Viewer]:
    """
    Get all active Spotlight viewer instances.
    """
    return list(_VIEWERS)


# pylint: disable=too-many-arguments
def show(
    dataset_or_folder: Optional[Union[str, os.PathLike, pd.DataFrame]] = None,
    host: str = "127.0.0.1",
    port: Union[int, Literal["auto"]] = "auto",
    layout: Optional[_LayoutLike] = None,
    no_browser: bool = False,
    wait: Union[bool, Literal["auto"]] = "auto",
    log_level: Union[
        int, Literal["trace", "debug", "info", "warning", "error", "critical"]
    ] = "critical",
    dtype: Optional[Dict[str, Type[ColumnType]]] = None,
) -> Viewer:
    """
    Start a new Spotlight viewer.

    Args:
        dataset_or_folder: root folder, dataset file or pandas.DataFrame (df) to open.
        host: optional host to run Spotlight at.
        port: optional port to run Spotlight at.
            If "auto" (default), automatically choose a random free port.
        layout: optional Spotlight :mod:`layout <renumics.spotlight.layout>`.
        no_browser: do not show Spotlight in browser.
        wait: If `True`, block code execution until all Spotlight browser tabs are closed.
            If `False`, continue code execution after Spotlight start.
            If "auto" (default), choose the mode automatically: non-blocking for
            `jupyter notebook`, `ipython` and other interactive sessions;
            blocking for scripts.
        log_level: optional log level to use in Spotlight server. In notebooks,
            server's output will be printed in the last visited cell, so low log
            levels can be confusing.
        dtype: Optional dict with mapping `column name -> column type` with
            column types allowed by Spotlight (for dataframes only).
    """

    viewer = None
    if port != "auto":
        # reuse viewer with the same port if specified
        for index, viewer in enumerate(_VIEWERS):
            if viewer.port == port:
                viewer = _VIEWERS[index]
                break
    if not viewer:
        viewer = Viewer(host, port, log_level=log_level)

    viewer.show(
        dataset_or_folder, layout=layout, no_browser=no_browser, wait=wait, dtype=dtype
    )
    return viewer


def close(port: Union[int, Literal["last"]] = "last") -> None:
    """
    Close an active Spotlight viewer.

    Args:
        port: optional port number at which the Spotlight viewer is running.
            If "last" (default), close the last started Spotlight viewer.

    Raises:
        ViewNotFoundError: if no Spotlight viewer found at the given `port`.
    """
    if port == "last":
        try:
            _VIEWERS[-1].close()
        except IndexError as e:
            raise ViewerNotFoundError("No active viewers found.") from e
        return
    for index, viewer in enumerate(_VIEWERS):
        if viewer.port == port:
            _VIEWERS[index].close()
            return
    raise ViewerNotFoundError(f"No viewer found at the port {port}.")
