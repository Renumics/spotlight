"""
    Tests for the renumics spotlight app and in mem data frame serving
"""

import json
from typing import List, Any

import requests
import pytest

from renumics import spotlight


def _column_by_name(columns: List, col_name: str) -> Any:
    return [col for col in columns if col["name"] == col_name][0]


@pytest.mark.parametrize("col_name", ["audio", "image"])
@pytest.mark.parametrize("row_index", [0, 1])
def test_get_valid_external_value(
    viewer_tally_df: spotlight.Viewer, col_name: str, row_index: int
) -> None:
    """test getting valid external values from df"""
    app_url = f"http://{viewer_tally_df.host}:{viewer_tally_df.port}"
    generation_id = json.loads(requests.get(f"{app_url}/api/table/", timeout=5).text)[
        "generation_id"
    ]
    response = requests.get(
        f"{app_url}/api/table/{col_name}/{row_index}?generation_id={generation_id}",
        timeout=5,
    )
    assert response.status_code == 200
    assert len(response.content) > 1000


@pytest.mark.parametrize("col_name", ["audio", "image"])
@pytest.mark.parametrize("row_index", [2, 3])
def test_get_empty_external_value(
    viewer_tally_df: spotlight.Viewer, col_name: str, row_index: int
) -> None:
    """test getting valid external values from df"""
    app_url = f"http://{viewer_tally_df.host}:{viewer_tally_df.port}"
    generation_id = json.loads(requests.get(f"{app_url}/api/table/", timeout=5).text)[
        "generation_id"
    ]
    response = requests.get(
        f"{app_url}/api/table/{col_name}/{row_index}?generation_id={generation_id}",
        timeout=5,
    )
    assert response.status_code == 200
    assert response.text == "null"


@pytest.mark.parametrize("col_name", ["audio", "image"])
@pytest.mark.parametrize("row_index", [4, 5])
def test_get_invalid_external_value(
    viewer_tally_df: spotlight.Viewer, col_name: str, row_index: int
) -> None:
    """test getting valid external values from df"""
    app_url = f"http://{viewer_tally_df.host}:{viewer_tally_df.port}"
    generation_id = json.loads(requests.get(f"{app_url}/api/table/", timeout=5).text)[
        "generation_id"
    ]
    response = requests.get(
        f"{app_url}/api/table/{col_name}/{row_index}?generation_id={generation_id}",
        timeout=5,
    )
    assert response.status_code == 422
    assert response.json()["type"] == "ConversionFailed"


def test_read_table(viewer_tally_df: spotlight.Viewer) -> None:
    """test full table can be read an returns data"""
    app_url = f"http://{viewer_tally_df.host}:{viewer_tally_df.port}"
    response = requests.get(app_url + "/api/table/", timeout=5)
    assert response.status_code == 200
    assert len(response.text) > 1000
    json_data = json.loads(response.text)
    assert _column_by_name(json_data["columns"], "even_text")["role"] == "str"
    assert _column_by_name(json_data["columns"], "encoded")["role"] == "Embedding"
    assert not json_data["max_rows_hit"]
    assert not json_data["max_columns_hit"]
