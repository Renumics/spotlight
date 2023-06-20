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
from typing import Collection, List, Union, Optional

import pandas as pd
from typing_extensions import Literal
import ipywidgets as widgets
import IPython.display

import __main__
from renumics.spotlight.dtypes.typing import ColumnTypeMapping
from renumics.spotlight.layout import _LayoutLike, parse
from renumics.spotlight.backend.server import create_server, Server
from renumics.spotlight.backend.websockets import RefreshMessage, ResetLayoutMessage
from renumics.spotlight.backend import create_datasource
from renumics.spotlight.develop.vite import Vite
from renumics.spotlight.settings import settings
from renumics.spotlight.typing import PathType, is_pathtype
from renumics.spotlight.webbrowser import launch_browser_in_thread

from renumics.spotlight.analysis.typing import DataIssue


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

    # pylint: disable=too-many-instance-attributes

    _thread: Optional[threading.Thread]
    _server: Optional[Server]
    _vite: Optional[Vite]
    _host: str
    _requested_port: Union[int, Literal["auto"]]
    _dataset_or_folder: Optional[Union[PathType, pd.DataFrame]]
    _allow_filebrowsing: Optional[bool]
    _layout: Optional[_LayoutLike]

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: Union[int, Literal["auto"]] = "auto",
    ) -> None:
        self._host = host
        self._requested_port = port
        self._dataset_or_folder = None
        self._allow_filebrowsing = None
        self._server = None
        self._thread = None
        self._vite = None

    def _init_server(self) -> None:
        """create a new uvicorn server if necessary"""
        if self._server:
            return

        self._server = create_server(self._host, self._requested_port)
        app = self._server.app

        if settings.dev:
            self._vite = Vite()
            self._vite.start()
            app.vite_url = self._vite.url

        self._thread = self._server.run_in_thread()
        if self not in _VIEWERS:
            _VIEWERS.append(self)

    def show(
        self,
        dataset_or_folder: Optional[Union[PathType, pd.DataFrame]] = None,
        layout: Optional[_LayoutLike] = None,
        no_browser: bool = False,
        allow_filebrowsing: Union[bool, Literal["auto"]] = "auto",
        wait: Union[bool, Literal["auto"]] = "auto",
        dtype: Optional[ColumnTypeMapping] = None,
        analyze: Optional[bool] = None,
        issues: Optional[Collection[DataIssue]] = None,
    ) -> None:
        """
        Show a dataset or folder in this spotlight viewer.

        Args:
            dataset_or_folder: root folder, dataset file or pandas.DataFrame (df) to open.
            layout: optional Spotlight :mod:`layout <renumics.spotlight.layout>`.
            no_browser: do not show Spotlight in browser.
            allow_filebrowsing: Whether to allow users to browse and open datasets.
                If "auto" (default), allow to browse if `dataset_or_folder` is a path.
            wait: If `True`, block code execution until all Spotlight browser tabs are closed.
                If `False`, continue code execution after Spotlight start.
                If "auto" (default), choose the mode automatically: non-blocking for
                `jupyter notebook`, `ipython` and other interactive sessions;
                blocking for scripts.
            dtype: Optional dict with mapping `column name -> column type` with
                column types allowed by Spotlight (for dataframes only).
            analyze: Automatically analyze common dataset issues (disabled by default).
            issues: Custom dataset issues displayed in the viewer.
        """
        # pylint: disable=too-many-branches,too-many-arguments

        self._init_server()
        if not self._server:
            raise RuntimeError("Failed to launch backend server")
        app = self._server.app

        in_interactive_session = not hasattr(__main__, "__file__")
        if wait == "auto":
            # `__main__.__file__` is not set in an interactive session, do not wait then.
            wait = not in_interactive_session

        if analyze is not None:
            app.analyze_issues = analyze

        if dataset_or_folder is not None:
            self._dataset_or_folder = dataset_or_folder
        elif self._dataset_or_folder is None:
            self._dataset_or_folder = Path.cwd()
        if dtype is not None:
            app.dtype = dtype

        if dataset_or_folder is not None or dtype is not None:
            # set correct project folder
            if is_pathtype(self._dataset_or_folder):
                path = Path(self._dataset_or_folder).absolute()
                if path.is_dir():
                    app.project_root = path
                else:
                    app.project_root = path.parent
                    app.data_source = create_datasource(path, dtype=app.dtype)
            else:
                app.data_source = create_datasource(
                    self._dataset_or_folder, dtype=app.dtype
                )
            self.refresh()

        if issues is not None:
            app.custom_issues = list(issues)

        if layout is not None:
            app.layout = parse(layout)
            if app.websocket_manager:
                app.websocket_manager.broadcast(ResetLayoutMessage())

        if allow_filebrowsing != "auto":
            self._allow_filebrowsing = allow_filebrowsing
        elif self._allow_filebrowsing is None:
            self._allow_filebrowsing = is_pathtype(self._dataset_or_folder)
        app.filebrowsing_allowed = self._allow_filebrowsing

        if not in_interactive_session or wait:
            print(f"Spotlight running on http://{self.host}:{self.port}/")

        if (
            not no_browser
            and app.websocket_manager
            and len(app.websocket_manager.connections) == 0
        ):
            self.open_browser()
        if wait:
            self.close(True)

    def close(self, wait: bool = False) -> None:
        """
        Shutdown the corresponding Spotlight instance.
        """

        if self not in _VIEWERS:
            return

        if self._thread is None or self._server is None:
            return

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

            if self._server.app.websocket_manager:
                self._server.app.websocket_manager.add_disconnect_callback(
                    on_disconnect
                )
                self._server.app.websocket_manager.add_connect_callback(on_connect)
            try:
                wait_event.wait()
            except KeyboardInterrupt as e:
                # cleanup on KeyboarInterrupt to prevent zombie processes
                self.close(wait=False)
                raise e

        if self._vite:
            self._vite.stop()

        _VIEWERS.remove(self)
        self._server.should_exit = True
        self._thread.join()
        self._server = None
        self._thread = None
        self._vite = None

    def open_browser(self) -> None:
        """
        Open the corresponding Spotlight instance in a browser.
        """
        if not self.port:
            return
        launch_browser_in_thread(self.host, self.port)

    def refresh(self) -> None:
        """
        Refresh the corresponding Spotlight instance in a browser.
        """
        if self._server and self._server.app.websocket_manager:
            self._server.app.websocket_manager.broadcast(RefreshMessage())

    @property
    def running(self) -> bool:
        """
        True if the viewer's webserver is running, false otherwise.
        """
        return self._thread is not None and self._server is not None

    @property
    def df(self) -> Optional[pd.DataFrame]:
        """
        Get served `DataFrame` if a `DataFrame` is served, `None` otherwise.
        """
        if self._server and self._server.app.data_source:
            return self._server.app.data_source.df
        return None

    @property
    def host(self) -> str:
        """
        The configured host setting.
        """
        return self._host

    @property
    def port(self) -> Optional[int]:
        """
        The port the viewer is running on.
        """
        if not self._server:
            return None
        return self._server.config.port

    def __repr__(self) -> str:
        return f"http://{self.host}:{self.port}/"

    def _ipython_display_(self) -> None:
        if not self._server:
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
    allow_filebrowsing: Union[bool, Literal["auto"]] = "auto",
    wait: Union[bool, Literal["auto"]] = "auto",
    dtype: Optional[ColumnTypeMapping] = None,
    analyze: Optional[bool] = None,
    issues: Optional[Collection[DataIssue]] = None,
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
        allow_filebrowsing: Whether to allow users to browse and open datasets.
            If "auto" (default), allow to browse if `dataset_or_folder` is a path.
        wait: If `True`, block code execution until all Spotlight browser tabs are closed.
            If `False`, continue code execution after Spotlight start.
            If "auto" (default), choose the mode automatically: non-blocking for
            `jupyter notebook`, `ipython` and other interactive sessions;
            blocking for scripts.
        dtype: Optional dict with mapping `column name -> column type` with
            column types allowed by Spotlight (for dataframes only).
        analyze: Automatically analyze common dataset issues (disabled by default).
        issues: Custom dataset issues displayed in the viewer.
    """

    viewer = None
    if port != "auto":
        # reuse viewer with the same port if specified
        for index, viewer in enumerate(_VIEWERS):
            if viewer.port == port:
                viewer = _VIEWERS[index]
                break
    if not viewer:
        viewer = Viewer(host, port)

    viewer.show(
        dataset_or_folder,
        layout=layout,
        no_browser=no_browser,
        allow_filebrowsing=allow_filebrowsing,
        wait=wait,
        dtype=dtype,
        analyze=analyze,
        issues=issues,
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
