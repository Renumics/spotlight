"""
    Tests for the renumics spotlight app and in mem data frame serving
"""

import json
from typing import List, Any

import requests

from renumics import spotlight


def _column_by_name(columns: List, col_name: str) -> Any:
    return [col for col in columns if col["name"] == col_name][0]


def test_read_table(viewer_weather_df: spotlight.Viewer) -> None:
    """test full table can be read an returns data"""
    app_url = f"http://{viewer_weather_df.host}:{viewer_weather_df.port}"
    response = requests.get(app_url + "/api/table/", timeout=5)
    assert response.status_code == 200
    assert len(response.text) > 1000
    json_data = json.loads((response.text))
    assert _column_by_name(json_data["columns"], "WindGustSpeed")["role"] == "str"
    assert not json_data["max_rows_hit"]
    assert not json_data["max_columns_hit"]
