"""
Manage data analyzers available for spotlights automatic dataset analysis.
"""
from typing import Set, Type

from .typing import Embedder

registered_embedders: Set[Type[Embedder]] = set()


def register_embedder(embedder: Type[Embedder]) -> None:
    """
    Register an embedder
    """
    registered_embedders.add(embedder)


def unregister_embedder(embedder: Type[Embedder]) -> None:
    """
    Unregister an embedder
    """
    registered_embedders.remove(embedder)
