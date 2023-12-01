"""
Manage data analyzers available for spotlights automatic dataset analysis.
"""
from typing import Any, Dict, Tuple, Type

from renumics.spotlight.dtypes import DType

from .typing import Embedder

registered_embedders: Dict[
    str, Tuple[Type[Embedder], DType, tuple, Dict[str, Any]]
] = {}


def register_embedder(
    embedder: Type[Embedder], dtype: DType, name: str, *args: Any, **kwargs: Any
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
