"""
Integration Test on API level for h5 data sources
"""

import tempfile
from typing import Iterator
import datetime

import pytest
import httpx
import numpy as np

from renumics import spotlight

COLUMNS = {
    "bool": (bool, [True, False]),
    "int": (int, [0, 1]),
    "float": (float, [0.0, np.nan]),
    "str": (str, ["foobar", ""]),
    "datetime": (datetime.datetime, [datetime.datetime.min, np.datetime64("NaT")]),
    "categorical": (spotlight.Category, ["foo", "bar"]),
    "array": (np.ndarray, [[[0]], [1,2,3]]),
    "window": (spotlight.Window, [[0, 1], [-np.inf, np.nan]]),
    "embedding": (spotlight.Embedding, [[1, 2, 3], [4,np.nan,5]]),
    "sequence": (spotlight.Sequence1D, [[[1, 2, 3], [2, 3, 4]], [[1, 2, 3, 5], [2, 3, 4, 5]]]),
    "image": (spotlight.Image, [spotlight.Image.empty(), None]),
    "audio": (spotlight.Audio, [spotlight.Audio.empty(), None]),
    "video": (spotlight.Video, [spotlight.Video.empty(), None]),
    "mesh": (spotlight.Mesh, [spotlight.Mesh.empty(), None]),
}


@pytest.fixture
def dataset_path() -> Iterator[str]:
    """
    H5 Dataset for tests
    """

    with tempfile.NamedTemporaryFile(suffix=".h5") as temp:
        with spotlight.Dataset(temp.name, "w") as ds:
            for col, (dtype, values) in COLUMNS.items():
                ds.append_column(col, column_type=dtype, values=values, optional=dtype not in (int, bool))
        yield temp.name


def test_get_table_returns_http_ok(dataset_path: str) -> None:
    """
    Ensure /api/table/ returns a valid response
    """
    viewer = spotlight.show(dataset_path, no_browser=True, wait=False)
    response = httpx.Client(base_url=viewer.url).get("/api/table/")
    viewer.close()
    assert response.status_code == 200


@pytest.mark.parametrize("col", COLUMNS.keys())
def test_get_cell_returns_http_ok(dataset_path: str, col: str) -> None:
    """
    Serve h5 dataset and get cell data for dtype
    """
    viewer = spotlight.show(dataset_path, no_browser=True, wait=False)
    gen_id = (
        httpx.Client(base_url=viewer.url).get("/api/table/").json()["generation_id"]
    )
    response = httpx.Client(base_url=viewer.url).get(
        f"/api/table/{col}/0?generation_id={gen_id}"
    )
    viewer.close()
    assert response.status_code == 200
