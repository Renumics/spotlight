"""
A decorator for data analysis functions
"""

from typing import Type
from .typing import Embedder
from .registry import register_embedder


def embedder(klass: Type[Embedder]) -> Type[Embedder]:
    """
    register an embedder class
    """
    register_embedder(klass)
    return klass
