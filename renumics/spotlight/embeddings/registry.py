"""
Manage data analyzers available for spotlights automatic dataset analysis.
"""

from typing import Any

from renumics.spotlight import dtypes

from .typing import Embedder

registered_embedders: dict[
    str, tuple[type[Embedder], dtypes.DType, tuple, dict[str, Any]]
] = {}


def register_embedder(
    embedder: type[Embedder], dtype: dtypes.DType, name: str, *args: Any, **kwargs: Any
) -> None:
    """
    Register an embedder
    """
    registered_embedders[name] = (embedder, dtype, args, kwargs)


def unregister_embedder(embedder: str) -> None:
    """
    Unregister an embedder
    """
    del registered_embedders[embedder]
