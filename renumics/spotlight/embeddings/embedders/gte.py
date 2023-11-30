from typing import Any, List

import numpy as np
import sentence_transformers

from renumics.spotlight import dtypes
from renumics.spotlight.embeddings.decorator import embedder
from renumics.spotlight.embeddings.exceptions import CannotEmbed
from renumics.spotlight.embeddings.typing import Embedder
from renumics.spotlight.logging import logger

try:
    import torch
except ImportError:
    logger.warning("`GTE Embedder` requires `pytorch` to be installed.")
else:

    @embedder
    class GteEmbedder(Embedder):
        def __init__(self, data_store: Any, column: str) -> None:
            if not dtypes.is_str_dtype(data_store.dtypes[column]):
                raise CannotEmbed
            self._data_store = data_store
            self._column = column

        def __call__(self) -> np.ndarray:
            values = self._data_store.get_converted_values(
                self._column, indices=slice(None), simple=False, check=False
            )
            none_mask = [sample is None for sample in values]
            if all(none_mask):
                return np.array([None] * len(values), dtype=np.object_)

            device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

            model = sentence_transformers.SentenceTransformer(
                "thenlper/gte-base", device=device
            )

            def _embed_batch(batch: List[str]) -> np.ndarray:
                return model.encode(batch, normalize_embeddings=True)

            embeddings = _embed_batch([value for value in values if value is not None])

            if any(none_mask):
                res = np.empty(len(values), dtype=np.object_)
                res[np.nonzero(~np.array(none_mask))[0]] = list(embeddings)
                return res

            return embeddings
