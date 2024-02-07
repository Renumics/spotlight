"""
Renumics Spotlight allows you to quickly explore your datasets.

To serve an interactive view of your dataset, simply pass it to [`spotlight.show`](#show()).

```python
import pandas as pd
from renumics import spotlight
df = pd.DataFrame(
   {
        "int": range(4),
        "str": "foo",
        "dt": pd.Timestamp("2017-01-01T12"),
        "cat": pd.Categorical(["foo", "bar"] * 2),
    }
)
spotlight.show(df)
```

Spotlight tries to infer supported column types from your data, but you can
overwrite these column types. Supply your custom mapping as `dtype` parameter to
[`spotlight.show`](#show()). For detailed overview of all the supported data types, see
[`renumics.spotlight.dtypes`](./dtypes).

```python
viewer = spotlight.show(df, dtype={"int": "float", "str": "category"})
```

We try to support a wide range of data sources, such as CSV, Parquet, ORC and
Hugging Face datasets.

```python
df = pd.read_csv("https://renumics.com/data/mnist/mnist-tiny.csv")
spotlight.show(df, dtype={"image": dtypes.image_dtype})

import datasets
ds = datasets.load_dataset("mnist", split="test")
spotlight.show(ds)
```

As an alternative that fully supports and persist our column types you can use
our custom [H5 dataset](./dataset).

```python
from datetime import datetime
from renumics import spotlight
with spotlight.Dataset("docs/example.h5", "w") as dataset:
    dataset.append_int_column("int", range(4))
    dataset.append_string_column("str", "foo")
    dataset.append_datetime_column("dt", datetime(2017, 1, 1, 12))
    dataset.append_categorical_column("cat", ["foo", "bar"] * 2)
spotlight.show("docs/example.h5")
```

To show an updated dataset change some viewer settings (e.g. provide custom
types), you can reuse the viewer instance returned by [`spotlight.show`](#show()).

```python
df = pd.read_csv("https://renumics.com/data/mnist/mnist-tiny.csv")
viewer = spotlight.show(df)
df["str"] = "foo"
viewer.show(df)
viewer.show(dtype={"image": dtypes.image_dtype})
```
"""

from . import cache, logging
from .__version__ import __version__  # noqa: F401
from .analysis.typing import DataIssue
from .dataset import Dataset  # noqa: F401
from .dtypes.legacy import Category, Window  # noqa: F401
from .media import (
    Audio,  # noqa: F401
    Embedding,  # noqa: F401
    Image,  # noqa: F401
    Mesh,  # noqa: F401
    Sequence1D,  # noqa: F401
    Video,  # noqa: F401
)
from .plugin_loader import load_plugins
from .settings import settings
from .viewer import Viewer, close, show, viewers

if not settings.verbose:
    logging.disable()

__plugins__ = load_plugins()

__all__ = ["show", "close", "viewers", "Viewer", "clear_caches", "DataIssue"]


def clear_caches() -> None:
    """
    Clear all cached data.
    """
    cache.clear("external-data")
