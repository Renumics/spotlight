"""
Types used in backend
"""

from typing import Optional
from fastapi import FastAPI

from renumics.spotlight.analysis import update_issues
from renumics.spotlight.backend.data_source import DataSource
from renumics.spotlight.backend.tasks.task_manager import TaskManager
from renumics.spotlight.backend.websockets import WebsocketManager
from renumics.spotlight.layout.nodes import Layout
from renumics.spotlight.backend.config import Config
from renumics.spotlight.typing import PathType
from renumics.spotlight.dtypes.typing import ColumnTypeMapping


class SpotlightApp(FastAPI):
    """
    Custom FastAPI Application class
    Provides typing support for our custom app attributes
    """

    # pylint: disable=too-many-instance-attributes

    _data_source: Optional[DataSource]
    dtype: Optional[ColumnTypeMapping]
    task_manager: TaskManager
    websocket_manager: WebsocketManager
    layout: Optional[Layout]
    config: Config
    project_root: PathType
    vite_url: Optional[str]
    username: str
    filebrowsing_allowed: bool

    @property
    def data_source(self) -> Optional[DataSource]:
        """
        Current data source.
        """
        return self._data_source

    @data_source.setter
    def data_source(self, new_data_source: Optional[DataSource]) -> None:
        self._data_source = new_data_source
        update_issues(self)
