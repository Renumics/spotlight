"""
    Spotlight core plugin
    Provides core datatypes and sources.
"""

from renumics.spotlight.app import SpotlightApp

from .api import (
    config as config_api,
)
from .api import (
    filebrowser as file_api,
)
from .api import (
    issues as issues_api,
)
from .api import (
    layout as layout_api,
)
from .api import (
    table as table_api,
)

__version__ = "0.0.1"
__priority__ = 0


def __register__() -> None:
    """
    register data sources
    """
    from . import (
        hdf5_data_source,  # noqa: F401
        huggingface_datasource,  # noqa: F401
        pandas_data_source,  # noqa: F401
    )


def __activate__(app: SpotlightApp) -> None:
    """
    setup additional api routes
    """
    app.include_router(layout_api.router, prefix="/api/layout")
    app.include_router(table_api.router, prefix="/api/table")
    app.include_router(file_api.router, prefix="/api/browse")
    app.include_router(config_api.router, prefix="/api/config")
    app.include_router(issues_api.router, prefix="/api/issues")
