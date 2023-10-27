"""
Renumics Spotlight

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
    >>> spotlight.viewers()
    []

Serving a CSV file:
    >>> import pandas as pd
    >>> from renumics import spotlight
    >>> from renumics.spotlight import dtypes
    >>> df = pd.read_csv("https://renumics.com/data/mnist/mnist-tiny.csv")
    >>> viewer = spotlight.show(df, dtype={"image": dtypes.image_dtype}, port=5000, no_browser=True, wait=False)
    Spotlight running on http://127.0.0.1:5000/
    >>> spotlight.close()
"""

from .__version__ import __version__  # noqa: F401
from .dataset import Dataset  # noqa: F401
from .media import (
    Audio,  # noqa: F401
    Embedding,  # noqa: F401
    Image,  # noqa: F401
    Mesh,  # noqa: F401
    Sequence1D,  # noqa: F401
    Video,  # noqa: F401
)
from .dtypes.legacy import Category, Window  # noqa: F401
from .viewer import Viewer, close, viewers, show
from .plugin_loader import load_plugins
from .settings import settings
from .analysis.typing import DataIssue
from . import cache, logging

if not settings.verbose:
    logging.disable()

__plugins__ = load_plugins()

__all__ = ["show", "close", "viewers", "Viewer", "clear_caches", "DataIssue"]


def clear_caches() -> None:
    """
    Clear all cached data.
    """
    cache.clear("external-data")
