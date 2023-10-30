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
