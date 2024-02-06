"""
This module allows user to start Spotlight from a python script/notebook.

Serving a `pandas.DataFrame`:
    >>> import pandas as pd
    >>> from renumics import spotlight
    >>> df = pd.DataFrame(
    ...    {
    ...         "int": range(4),
    ...         "str": "foo",
    ...         "dt": pd.Timestamp("2017-01-01T12"),
    ...         "cat": pd.Categorical(["foo", "bar"] * 2),
    ...     }
    ... )
    >>> viewer = spotlight.show(df, port=5000, no_browser=True, wait=False)
    Spotlight running on http://127.0.0.1:5000/
    >>> spotlight.viewers()
    [http://127.0.0.1:5000/]
    >>> spotlight.close()

Serving a CSV file:
    >>> import pandas as pd
    >>> from renumics import spotlight
    >>> from renumics.spotlight import dtypes
    >>> df = pd.read_csv("https://renumics.com/data/mnist/mnist-tiny.csv")
    >>> viewer = spotlight.show(
    ...     df,
    ...     dtype={"image": dtypes.image_dtype},
    ...     port=5000,
    ...     no_browser=True,
    ...     wait=False,
    ... )
    Spotlight running on http://127.0.0.1:5000/
    >>> spotlight.close()

Serving a Hugging Face dataset:
    >>> import datasets
    >>> from renumics import spotlight
    >>> ds = datasets.load_dataset("mnist", split="test")
    >>> viewer = spotlight.show(ds, port=5000, no_browser=True, wait=False)
    Spotlight running on http://127.0.0.1:5000/
    >>> spotlight.close()

Serving a H5 dataset:
    >>> from datetime import datetime
    >>> import datasets
    >>> from renumics import spotlight
    >>> with spotlight.Dataset("docs/example.h5", "w") as dataset:
    ...     dataset.append_int_column("int", range(4))
    ...     dataset.append_string_column("str", "foo")
    ...     dataset.append_datetime_column("dt", datetime(2017, 1, 1, 12))
    ...     dataset.append_categorical_column("cat", ["foo", "bar"] * 2)
    >>> viewer = spotlight.show(
    ...     "docs/example.h5", port=5000, no_browser=True, wait=False
    ... )
    Spotlight running on http://127.0.0.1:5000/
    >>> spotlight.close()

Serving multiple datasets:
    >>> import datasets
    >>> import pandas as pd
    >>> from renumics import spotlight
    >>> spotlight.viewers()
    []
    >>> df = pd.read_csv("https://renumics.com/data/mnist/mnist-tiny.csv")
    >>> df_viewer = spotlight.show(df, port=5000, no_browser=True, wait=False)
    Spotlight running on http://127.0.0.1:5000/
    >>> ds = datasets.load_dataset("mnist", split="test")
    >>> ds_viewer = spotlight.show(ds, port=5001, no_browser=True, wait=False)
    Spotlight running on http://127.0.0.1:5001/
    >>> spotlight.viewers()
    [http://127.0.0.1:5000/, http://127.0.0.1:5001/]
    >>> spotlight.close(5000)
    >>> spotlight.viewers()
    [http://127.0.0.1:5001/]
    >>> spotlight.close()
    >>> spotlight.viewers()
    []

Reuse the dataset `Viewer`:
    >>> import datasets
    >>> import pandas as pd
    >>> from renumics import spotlight
    >>> df = pd.read_csv("https://renumics.com/data/mnist/mnist-tiny.csv")
    >>> viewer = spotlight.show(df, port=5000, no_browser=True, wait=False)
    Spotlight running on http://127.0.0.1:5000/
    >>> ds = datasets.load_dataset("mnist", split="test")
    >>> viewer.show(ds, no_browser=True, wait=False)
    Spotlight running on http://127.0.0.1:5000/
    >>> spotlight.close()
"""

import time
from pathlib import Path
from typing import Any, Collection, Dict, List, Optional, Union

import IPython.display
import ipywidgets as widgets
import pandas as pd
from typing_extensions import Literal

import __main__
from renumics.spotlight.analysis.typing import DataIssue
from renumics.spotlight.app_config import AppConfig
from renumics.spotlight.dtypes import create_dtype
from renumics.spotlight.layout import _LayoutLike, parse
from renumics.spotlight.server import Server
from renumics.spotlight.settings import settings
from renumics.spotlight.typing import PathType, is_pathtype
from renumics.spotlight.webbrowser import launch_browser_in_thread


class ViewerNotFoundError(Exception):
    """
    Raised if a Spotlight viewer is not found.
    """


class Viewer:
    """
    A Spotlight viewer. It corresponds to a single running Spotlight instance.

    Viewer can be created using `spotlight.show`.

    Attributes:
        host: host at which Spotlight is running
        port: port at which Spotlight is running
    """

    _host: str
    _requested_port: Union[int, Literal["auto"]]
    _server: Optional[Server]

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: Union[int, Literal["auto"]] = "auto",
    ) -> None:
        self._host = host
        self._requested_port = port
        self._server = None

    def show(
        self,
        dataset: Union[PathType, pd.DataFrame, None],
        folder: Optional[PathType] = None,
        layout: Optional[_LayoutLike] = None,
        no_browser: bool = False,
        allow_filebrowsing: Union[bool, Literal["auto"]] = "auto",
        wait: Union[bool, Literal["auto", "forever"]] = "auto",
        dtype: Optional[Dict[str, Any]] = None,
        analyze: Optional[Union[List[str], bool]] = None,
        issues: Optional[Collection[DataIssue]] = None,
        embed: Optional[Union[List[str], bool]] = None,
    ) -> None:
        """
        Show a dataset or folder in this spotlight viewer.

        Args:
            dataset: Dataset file or pandas.DataFrame (df) to open.
            folder: Root folder for filebrowser and lookup of dataset files.
            layout: Optional Spotlight [layout](./layout).
            no_browser: Do not show Spotlight in browser.
            allow_filebrowsing: Whether to allow users to browse and open datasets.
                If "auto" (default), allow to browse if `dataset_or_folder` is a path.
            wait: If `True`, block code execution until all Spotlight browser tabs are closed.
                If `False`, continue code execution after Spotlight start.
                If "forever", keep spotlight running forever, but block.
                If "auto" (default), choose the mode automatically: non-blocking (`False`) for
                `jupyter notebook`, `ipython` and other interactive sessions;
                blocking (`True`) for scripts.
            dtype: Optional dict with mapping `column name -> column type` with
                column types allowed by Spotlight (for dataframes only).
            analyze: Automatically analyze common dataset issues (disabled by default).
            issues: Custom dataset issues displayed in the viewer.
            embed: Automatically embed all or given columns with default
                embedders (disabled by default).
        """

        if is_pathtype(dataset):
            dataset = Path(dataset).absolute()
            if dataset.is_dir():
                project_root = dataset
            else:
                project_root = dataset.parent
        else:
            project_root = None

        if folder:
            project_root = Path(folder)

        if allow_filebrowsing == "auto":
            filebrowsing_allowed = project_root is not None
        else:
            filebrowsing_allowed = allow_filebrowsing

        layout = layout or settings.layout
        parsed_layout = parse(layout) if layout else None
        converted_dtypes = (
            {column_name: create_dtype(d) for column_name, d in dtype.items()}
            if dtype
            else None
        )

        config = AppConfig(
            dataset=dataset,
            dtypes=converted_dtypes,
            project_root=project_root,
            analyze=analyze,
            custom_issues=list(issues) if issues else None,
            embed=embed,
            layout=parsed_layout,
            filebrowsing_allowed=filebrowsing_allowed,
        )

        if not self._server:
            port = 0 if self._requested_port == "auto" else self._requested_port
            self._server = Server(host=self._host, port=port)
            self._server.start(config)

            if self not in _VIEWERS:
                _VIEWERS.append(self)
        else:
            try:
                self._server.update(config)
            except Exception as e:
                self.close()
                raise e

        if not no_browser and self._server.connected_frontends == 0:
            self.open_browser()

        in_interactive_session = not hasattr(__main__, "__file__")
        if wait == "auto":
            # `__main__.__file__` is not set in an interactive session, do not wait then.
            wait = not in_interactive_session

        if not in_interactive_session or wait:
            print(f"Spotlight running on {self.url}")

        if wait:
            self.close(wait)

    def close(self, wait: Union[bool, Literal["forever"]] = False) -> None:
        """
        Shutdown the corresponding Spotlight instance.
        """

        if self not in _VIEWERS:
            return

        if self._server is None:
            return

        if wait:
            if wait == "forever":
                while True:
                    time.sleep(1)
            else:
                self._server.wait_for_frontend_disconnect()

        _VIEWERS.remove(self)
        self._server.stop()
        self._server = None

    def open_browser(self) -> None:
        """
        Open the corresponding Spotlight instance in a browser.
        """
        if not self.port:
            return
        launch_browser_in_thread("localhost", self.port)

    def refresh(self) -> None:
        """
        Refresh the corresponding Spotlight instance in a browser.
        """
        if self._server:
            self._server.refresh_frontends()

    @property
    def running(self) -> bool:
        """
        True if the viewer's webserver is running, false otherwise.
        """
        return self._server is not None and self._server.running

    @property
    def df(self) -> Optional[pd.DataFrame]:
        """
        Get served `DataFrame` if a `DataFrame` is served, `None` otherwise.
        """
        if self._server:
            return self._server.get_df()

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
        return self._server.port

    @property
    def url(self) -> str:
        """
        The viewer's url.
        """
        return f"http://{self.host}:{self.port}/"

    def __repr__(self) -> str:
        return self.url

    def _ipython_display_(self) -> None:
        if not self._server:
            return

        if get_ipython().__class__.__name__ == "ZMQInteractiveShell":  # type: ignore # noqa: F821
            # in notebooks display a rich html widget

            label = widgets.Label(f"Spotlight running on {self.url}")
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


def show(
    dataset: Union[PathType, pd.DataFrame, None] = None,
    folder: Optional[PathType] = None,
    host: str = "127.0.0.1",
    port: Union[int, Literal["auto"]] = "auto",
    layout: Optional[_LayoutLike] = None,
    no_browser: bool = False,
    allow_filebrowsing: Union[bool, Literal["auto"]] = "auto",
    wait: Union[bool, Literal["auto", "forever"]] = "auto",
    dtype: Optional[Dict[str, Any]] = None,
    analyze: Optional[Union[bool, List[str]]] = None,
    issues: Optional[Collection[DataIssue]] = None,
    embed: Optional[Union[List[str], bool]] = None,
) -> Viewer:
    """
    Start a new Spotlight viewer.

    Args:
        dataset: Dataset file or pandas.DataFrame (df) to open.
        folder: Root folder for filebrowser and lookup of dataset files.
        host: optional host to run Spotlight at.
        port: optional port to run Spotlight at.
            If "auto" (default), automatically choose a random free port.
        layout: optional Spotlight [layout](./layout).
        no_browser: do not show Spotlight in browser.
        allow_filebrowsing: Whether to allow users to browse and open datasets.
            If "auto" (default), allow to browse if `dataset_or_folder` is a path.
        wait: If `True`, block code execution until all Spotlight browser tabs are closed.
                If `False`, continue code execution after Spotlight start.
                If "forever", keep spotlight running forever, but block.
                If "auto" (default), choose the mode automatically: non-blocking (`False`) for
                `jupyter notebook`, `ipython` and other interactive sessions;
                blocking (`True`) for scripts.
        dtype: Optional dict with mapping `column name -> column type` with
            column types allowed by Spotlight (for dataframes only).
        analyze: Automatically analyze common dataset issues (disabled by default).
        issues: Custom dataset issues displayed in the viewer.
        embed: Automatically embed all or given columns with default
            embedders (disabled by default).
    """

    viewer = None
    if port != "auto":
        # reuse viewer with the same port if specified
        for index, viewer_ in enumerate(_VIEWERS):
            if viewer_.port == port:
                viewer = _VIEWERS[index]
                break
    if not viewer:
        viewer = Viewer(host, port)

    viewer.show(
        dataset,
        folder=folder,
        layout=layout,
        no_browser=no_browser,
        allow_filebrowsing=allow_filebrowsing,
        wait=wait,
        dtype=dtype,
        analyze=analyze,
        issues=issues,
        embed=embed,
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
