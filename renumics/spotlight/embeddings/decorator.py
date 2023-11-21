"""
A decorator for data analysis functions
"""

from .typing import Embedder
from .registry import register_embedder


def embedder(func: Embedder) -> Embedder:
    """
    register an embedder function
    """
    register_embedder(func)
    return func
