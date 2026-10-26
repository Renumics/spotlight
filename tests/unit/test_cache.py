"""
Test the disk cache of backend files.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from renumics.spotlight import appdirs
from renumics.spotlight import cache as cache_module
from renumics.spotlight.cache import Cache


@pytest.fixture(autouse=True)
def cache_dir(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    """Use an empty cache directory"""
    monkeypatch.setattr(appdirs, "cache_dir", tmp_path)
    return tmp_path


def test_cache_is_opened_when_it_is_used(cache_dir: Path) -> None:
    """
    Test a cache creates nothing before it is used.
    """
    cache = Cache("lazy")
    assert not (cache_dir / "lazy").exists()

    cache["key"] = "value"
    assert (cache_dir / "lazy").is_dir()
    assert cache["key"] == "value"


def test_missing_key_is_a_key_error() -> None:
    """
    Test reading a key that was not stored raises a `KeyError`.
    """
    with pytest.raises(KeyError):
        Cache("missing")["key"]


def test_clear_all_empties_all_created_caches() -> None:
    """
    Test clearing all caches empties every cache that was created.
    """
    first = Cache("first")
    second = Cache("second")
    first["key"] = 1
    second["key"] = 2
    cache_module.clear_all()
    with pytest.raises(KeyError):
        first["key"]
    with pytest.raises(KeyError):
        second["key"]


def test_clear_all_creates_no_cache_directory(cache_dir: Path) -> None:
    """
    Test clearing all caches does not open caches that were never stored to.
    """
    Cache("unused")
    cache_module.clear_all()
    assert not (cache_dir / "unused").exists()


def test_importing_spotlight_creates_no_cache_directory(tmp_path: Path) -> None:
    """
    Test importing the package does not touch the file system for its caches, so that
    merely importing it leaves empty cache directories nowhere.
    """
    environment = {**os.environ, "XDG_CACHE_HOME": str(tmp_path)}
    subprocess.run(
        [sys.executable, "-c", "import renumics.spotlight"],
        env=environment,
        check=True,
        timeout=300,
    )
    assert list(tmp_path.rglob("cache.db")) == []
