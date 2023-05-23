"""
Environment variables' manipulation.
"""
import os
from contextlib import contextmanager
from typing import Dict, Iterator, Optional


@contextmanager
def set_temp_environ(**kwargs: Optional[str]) -> Iterator[None]:
    """
    Temporarily set passed environment variables. If value `None` is passed,
    temporarily delete respective variable.
    """
    old_environ: Dict[str, Optional[str]] = {
        key: os.getenv(key, None) for key in kwargs
    }
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
