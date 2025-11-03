"""
Tests for the renumics spotlight app and in mem data frame serving
"""

import json
from typing import Any, List, Tuple

import requests

from renumics import spotlight


def _column_by_name(columns: List, col_name: str) -> Any:
    return [col for col in columns if col["name"] == col_name][0]


def test_read_table(
    viewer_double_tally_df: Tuple[spotlight.Viewer, spotlight.Viewer],
) -> None:
    """test that the two spotlight instances return different data"""

    viewer_tally_df = viewer_double_tally_df[0]
    app_url = f"http://{viewer_tally_df.host}:{viewer_tally_df.port}"

    response = requests.get(app_url + "/api/table/", timeout=5)
    assert response.status_code == 200
    assert len(response.text) > 1000
    json_data1 = json.loads((response.text))

    viewer_tally_df = viewer_double_tally_df[1]
    app_url = f"http://{viewer_tally_df.host}:{viewer_tally_df.port}"

    response = requests.get(app_url + "/api/table/", timeout=5)
    assert response.status_code == 200
    assert len(response.text) > 1000
    json_data2 = json.loads((response.text))

    assert all(
        v < 100 for v in _column_by_name(json_data1["columns"], "number")["values"]
    )
    assert all(
        v > 100 for v in _column_by_name(json_data2["columns"], "number")["values"]
    )
