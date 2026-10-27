"""
Tests for path helper functions
"""

from pathlib import Path

import pytest

from renumics.spotlight.io.path import is_path_relative_to


@pytest.mark.parametrize(
    "path",
    [".", "file.csv", "folder/file.csv", "folder/../file.csv", "./folder/."],
)
def test_path_inside_parent(tmp_path: Path, path: str) -> None:
    """paths inside the parent are relative to it"""
    assert is_path_relative_to(tmp_path / path, tmp_path)


@pytest.mark.parametrize(
    "path", ["..", "../file.csv", "folder/../../file.csv", "../../../../../../etc"]
)
def test_path_outside_parent(tmp_path: Path, path: str) -> None:
    """paths escaping the parent via `..` are not relative to it"""
    assert not is_path_relative_to(tmp_path / path, tmp_path)


def test_absolute_path_outside_parent(tmp_path: Path) -> None:
    """absolute paths outside the parent are not relative to it"""
    assert not is_path_relative_to(tmp_path / "/etc", tmp_path)


def test_symlink_outside_parent(tmp_path: Path) -> None:
    """symlinks pointing outside the parent are not relative to it"""
    parent = tmp_path / "parent"
    parent.mkdir()
    (parent / "link").symlink_to(tmp_path)
    assert not is_path_relative_to(parent / "link", parent)
