"""
This module provides a simple dataclass for storing task information
"""

import dataclasses
from concurrent.futures import Future
from typing import Optional, Union


@dataclasses.dataclass
class Task:
    """
    An executing task.
    """

    name: Optional[str]
    tag: Optional[Union[str, int]]
    future: Future
