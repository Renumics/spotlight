"""
Data for h5 tests
"""

import datetime

import numpy as np
from renumics import spotlight


COLUMNS = {
    "bool": (bool, [True, False]),
    "int": (int, [0, 1]),
    "float": (float, [0.0, np.nan]),
    "str": (str, ["foobar", ""]),
    "datetime": (datetime.datetime, [datetime.datetime.min, np.datetime64("NaT")]),
    "categorical": (spotlight.Category, ["foo", "bar"]),
    "array": (np.ndarray, [[[0]], [1, 2, 3]]),
    "window": (spotlight.Window, [[0, 1], [-np.inf, np.nan]]),
    "embedding": (spotlight.Embedding, [[1, 2, 3], [4, np.nan, 5]]),
    "sequence": (
        spotlight.Sequence1D,
        [[[1, 2, 3], [2, 3, 4]], [[1, 2, 3], [2, 3, 5]]],
    ),
    "image": (spotlight.Image, [spotlight.Image.empty(), None]),
    "audio": (spotlight.Audio, [spotlight.Audio.empty(), None]),
    "video": (spotlight.Video, [spotlight.Video.empty(), None]),
    "mesh": (spotlight.Mesh, [spotlight.Mesh.empty(), None]),
}
