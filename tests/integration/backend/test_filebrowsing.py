"""
Tests that file browsing and table opening are confined to the project root
"""

from collections.abc import Iterator
from pathlib import Path

import pandas as pd
import pytest
import requests

from renumics import spotlight

# encoded dots, so that the HTTP client does not normalize them away
PARENT = "%2E%2E"


@pytest.fixture()
def project(tmp_path: Path) -> Path:
    """a project root with one dataset inside and one dataset outside"""
    project_root = tmp_path / "project"
    (project_root / "subfolder").mkdir(parents=True)
    pd.DataFrame({"public": [1, 2, 3]}).to_csv(project_root / "inside.csv")
    pd.DataFrame({"secret": [4, 5, 6]}).to_csv(tmp_path / "outside.csv")
    (tmp_path / "outside_folder").mkdir()
    return project_root


@pytest.fixture()
def app_url(project: Path) -> Iterator[str]:
    """url of a viewer with file browsing enabled on the project root"""
    viewer = spotlight.show(
        folder=project,
        host="127.0.0.1",
        no_browser=True,
        port="auto",
        wait=False,
        allow_filebrowsing=True,
    )
    yield f"http://{viewer.host}:{viewer.port}"
    viewer.close()


@pytest.mark.parametrize("path", ["", "subfolder", "subfolder/" + PARENT])
def test_browse_inside_project_root(app_url: str, path: str) -> None:
    """folders inside the project root can be browsed"""
    response = requests.get(f"{app_url}/api/browse/{path}", timeout=5)
    assert response.status_code == 200


@pytest.mark.parametrize(
    "path",
    [
        PARENT,
        f"{PARENT}/outside_folder",
        f"subfolder/{PARENT}/{PARENT}",
        f"{PARENT}/{PARENT}/{PARENT}/{PARENT}/{PARENT}/{PARENT}",
    ],
)
def test_browse_outside_project_root(app_url: str, path: str) -> None:
    """folders outside the project root cannot be browsed"""
    response = requests.get(f"{app_url}/api/browse/{path}", timeout=5)
    assert response.status_code == 403
    assert "outside.csv" not in response.text


def test_browse_absolute_path(app_url: str, tmp_path: Path) -> None:
    """absolute paths outside the project root cannot be browsed"""
    response = requests.get(f"{app_url}/api/browse/{tmp_path}", timeout=5)
    assert response.status_code == 403
    assert "outside.csv" not in response.text


@pytest.mark.parametrize("path", ["inside.csv", f"subfolder/{PARENT}/inside.csv"])
def test_open_table_inside_project_root(app_url: str, path: str) -> None:
    """tables inside the project root can be opened"""
    response = requests.post(f"{app_url}/api/table/open/{path}", timeout=5)
    assert response.status_code == 200
    response = requests.get(f"{app_url}/api/table/", timeout=5)
    assert "public" in response.text


@pytest.mark.parametrize(
    "path", [f"{PARENT}/outside.csv", f"subfolder/{PARENT}/{PARENT}/outside.csv"]
)
def test_open_table_outside_project_root(app_url: str, path: str) -> None:
    """tables outside the project root cannot be opened"""
    response = requests.post(f"{app_url}/api/table/open/{path}", timeout=5)
    assert response.status_code == 403
    response = requests.get(f"{app_url}/api/table/", timeout=5)
    assert "secret" not in response.text


def test_open_table_absolute_path(app_url: str, tmp_path: Path) -> None:
    """absolute table paths outside the project root cannot be opened"""
    response = requests.post(
        f"{app_url}/api/table/open/{tmp_path / 'outside.csv'}", timeout=5
    )
    assert response.status_code == 403
    response = requests.get(f"{app_url}/api/table/", timeout=5)
    assert "secret" not in response.text
