"""
Data for h5 tests
"""

import datetime
from typing import Dict, Tuple

import numpy as np
from renumics import spotlight


COLUMNS: Dict[str, Tuple[str, list]] = {
    "bool": ("bool", [True, False]),
    "int": ("int", [0, 1]),
    "float": ("float", [0.0, np.nan]),
    "str": ("str", ["foobar", ""]),
    "datetime": ("datetime", [datetime.datetime.min, np.datetime64("NaT")]),
    "categorical": ("Category", ["foo", "bar"]),
    "array": ("array", [[[0]], [1, 2, 3]]),
    "window": ("Window", [[0, 1], [-np.inf, np.nan]]),
    "embedding": ("Embedding", [[1, 2, 3], [4, np.nan, 5]]),
    "sequence": ("Sequence1D", [[[1, 2, 3], [2, 3, 4]], [[2, 3], [5, 5]]]),
    "optional_sequence": ("Sequence1D", [[[1, 2, 3], [2, 3, 4]], None]),
    "image": ("Image", [spotlight.Image.empty(), None]),
    "audio": ("Audio", [spotlight.Audio.empty(), None]),
    "video": ("Video", [spotlight.Video.empty(), None]),
    "mesh": ("Mesh", [spotlight.Mesh.empty(), None]),
}
