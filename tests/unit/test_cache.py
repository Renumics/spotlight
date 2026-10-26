"""
Test the disk cache of backend files.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from renumics.spotlight import appdirs
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


def test_clear_empties_the_cache_of_all_objects() -> None:
    """
    Test clearing a cache by its name empties it for objects that were opened before.
    """
    from renumics.spotlight import cache as cache_module

    cache = Cache("shared")
    cache["key"] = 1
    cache_module.clear("shared")
    with pytest.raises(KeyError):
        cache["key"]


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
