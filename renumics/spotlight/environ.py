"""
Environment variables' manipulation.
"""

import os
from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def set_temp_environ(**kwargs: str | None) -> Iterator[None]:
    """
    Temporarily set passed environment variables. If value `None` is passed,
    temporarily delete respective variable.
    """
    old_environ: dict[str, str | None] = {key: os.getenv(key, None) for key in kwargs}
    try:
        for key, value in kwargs.items():
            if value is None:
                if key in os.environ:
                    del os.environ[key]
            else:
                os.environ[key] = value
        yield
    finally:
        for key, old_value in old_environ.items():
            if old_value is None:
                del os.environ[key]
            else:
                os.environ[key] = old_value
