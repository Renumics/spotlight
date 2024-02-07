"""
Dataset Analysis
"""

import importlib
import pkgutil
from typing import Dict, List

import numpy as np

from renumics.spotlight.data_store import DataStore
from renumics.spotlight.embeddings.typing import Embedder

from . import embedders as embedders_namespace
from .decorator import embed  # noqa: F401
from .registry import registered_embedders

# import all modules in .embedders
for module_info in pkgutil.iter_modules(embedders_namespace.__path__):
    importlib.import_module(embedders_namespace.__name__ + "." + module_info.name)


def create_embedders(data_store: DataStore, columns: List[str]) -> Dict[str, Embedder]:
    """
    Create embedding functions for the given data store.
    """
    embedders: Dict[str, Embedder] = {}
    for column in columns:
        for name, (embedder_class, dtype, args, kwargs) in registered_embedders.items():
            if data_store.dtypes[column].name != dtype.name:
                continue

            embedder = embedder_class(data_store, column, *args, **kwargs)
            embedders[f"{column}.{name}.embedding"] = embedder
    return embedders


def run_embedders(embedders: Dict[str, Embedder]) -> Dict[str, np.ndarray]:
    """
    Run the given functions.
    """
    return {column: embedder() for column, embedder in embedders.items()}
