"""
Integration Test on API level for h5 data sources
"""
from typing import Type

import httpx
import numpy as np
import pytest

from renumics import spotlight
from renumics.spotlight.dataset.typing import OutputType

from .data import COLUMNS


def test_get_table_returns_http_ok(dataset_path: str) -> None:
    """
    Ensure /api/table/ returns a valid response
    """
    viewer = spotlight.show(dataset_path, no_browser=True, wait=False)
    response = httpx.Client(base_url=viewer.url).get("/api/table/")
    viewer.close()
    assert response.status_code == 200


@pytest.mark.parametrize(
    "col,dtype",
    [
        ("bool", int),
        ("int", float),
        ("datetime", str),
        ("str", spotlight.Category),
        ("embedding", np.ndarray),
    ],
)
def test_custom_dtypes(dataset_path: str, col: str, dtype: Type[OutputType]) -> None:
    """
    Test h5 data source with custom dtypes.
    """
    viewer = spotlight.show(
        dataset_path, dtype={col: dtype}, no_browser=True, wait=False
    )
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
