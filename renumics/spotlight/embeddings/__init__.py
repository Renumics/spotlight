"""
Dataset Analysis
"""

import importlib
import pkgutil
from typing import Any, Dict, List

import numpy as np
from renumics.spotlight.embeddings.exceptions import CannotEmbed
from renumics.spotlight.embeddings.typing import Embedder

from renumics.spotlight.logging import logger

from .registry import registered_embedders
from . import embedders as embedders_namespace

# import all modules in .embedders
for module_info in pkgutil.iter_modules(embedders_namespace.__path__):
    importlib.import_module(embedders_namespace.__name__ + "." + module_info.name)


def create_embedders(data_store: Any, columns: List[str]) -> Dict[str, Embedder]:
    """
    Create embedding functions for the given data store.
    """

    logger.info("Embedding started.")

    embedders: Dict[str, Embedder] = {}
    for column in columns:
        for embedder_class in registered_embedders:
            try:
                embedder = embedder_class(data_store, column)
            except CannotEmbed:
                continue
            embedders[f"{column}.embedding"] = embedder
            break

    logger.info("Embedding done.")

    return embedders


def embed(embedders: Dict[str, Embedder]) -> Dict[str, np.ndarray]:
    """
    Run the given functions.
    """
    return {column: embedder() for column, embedder in embedders.items()}
