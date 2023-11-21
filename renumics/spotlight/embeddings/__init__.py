"""
Dataset Analysis
"""

import importlib
import pkgutil
from typing import Any, Dict, List

import numpy as np

from renumics.spotlight.logging import logger

from .registry import registered_embedders
from . import embedders as embedders_namespace

# import all modules in .embedders
for module_info in pkgutil.iter_modules(embedders_namespace.__path__):
    importlib.import_module(embedders_namespace.__name__ + "." + module_info.name)


def embed_columns(data_store: Any, columns: List[str]) -> Dict[str, np.ndarray]:
    """
    Find dataset issues in the data source
    """

    logger.info("Embedding started.")

    all_embeddings: Dict[str, np.ndarray] = {}
    for column in columns:
        for embedder in registered_embedders:
            if (embeddings := embedder(data_store, column)) is not None:
                all_embeddings[f"{column}.embedding"] = embeddings
                break

    logger.info("Embedding done.")

    return all_embeddings
