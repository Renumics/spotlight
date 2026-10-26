"""
This module provides a simple dataclass for storing task information
"""

import dataclasses
from concurrent.futures import Future


@dataclasses.dataclass
class Task:
    """
    An executing task.
    """

    name: str | None
    tag: str | int | None
    future: Future
