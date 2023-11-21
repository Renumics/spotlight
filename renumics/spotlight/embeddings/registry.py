"""
Manage data analyzers available for spotlights automatic dataset analysis.
"""
from typing import Set

from .typing import Embedder

registered_embedders: Set[Embedder] = set()


def register_embedder(embedder: Embedder) -> None:
    """
    Register an embedder
    """
    registered_embedders.add(embedder)


def unregister_embedder(embedder: Embedder) -> None:
    """
    Unregister an embedder
    """
    registered_embedders.remove(embedder)
