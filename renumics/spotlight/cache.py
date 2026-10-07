"""
Cache for backend files.
"""

from pathlib import Path
from sqlite3 import OperationalError
from typing import Any, Optional

import diskcache

from renumics.spotlight import appdirs


class Cache:
    """
    A simple wrapper around `diskcache.Cache`, which is opened when it is first used
    (importing the module creates no cache directories).
    """

    _dir: Path
    _cache: Optional[diskcache.Cache]

    def __init__(self, name: str) -> None:
        self._dir = appdirs.cache_dir / name
        self._cache = None

    def _init_cache(self) -> diskcache.Cache:
        return diskcache.Cache(
            str(self._dir),
            size_limit=2e9,
            eviction_policy="least-recently-used",
        )

    def _open(self) -> diskcache.Cache:
        if self._cache is None:
            self._cache = self._init_cache()
        return self._cache

    def _reopen(self) -> diskcache.Cache:
        if self._cache is not None:
            self._cache.close()
        self._cache = self._init_cache()
        return self._cache

    def __getitem__(self, name: str) -> Any:
        try:
            return self._open()[name]
        except OperationalError:
            return self._reopen()[name]

    def __setitem__(self, name: str, value: Any) -> None:
        try:
            self._open()[name] = value
        except OperationalError:
            self._reopen()[name] = value

    def clear(self) -> None:
        """
        Clear the whole cache.
        """
        self._open().clear()


external_data_cache = Cache("external-data")
reduction_cache = Cache("reduction")


def clear(name: str) -> None:
    """
    Clear cache by its name.
    """
    cache = Cache(name)
    cache.clear()
