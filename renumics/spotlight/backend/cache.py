"""
Cache for backend files.
"""

from pathlib import Path
from sqlite3 import OperationalError
from typing import Any

import diskcache

from renumics.spotlight import appdirs


class Cache:
    """
    A simple wrapper around `diskcache.Cache`.
    """

    _dir: Path
    _cache: diskcache.Cache

    def __init__(self, name: str) -> None:
        self._dir = appdirs.cache_dir / name
        self._cache = self._init_cache()

    def _init_cache(self) -> diskcache.Cache:
        return diskcache.Cache(
            str(self._dir),
            size_limit=2e9,
            eviction_policy="least-recently-used",
        )

    def __getitem__(self, name: str) -> Any:
        try:
            return self._cache[name]
        except OperationalError:
            self._cache.close()
            self._cache = self._init_cache()
            return self._cache[name]

    def __setitem__(self, name: str, value: Any) -> None:
        try:
            self._cache[name] = value
        except OperationalError:
            self._cache.close()
            self._cache = self._init_cache()
            self._cache[name] = value
