from typing import Iterable, List

import numpy as np
import sentence_transformers
from renumics.spotlight.embeddings.decorator import embed

from renumics.spotlight.logging import logger

try:
    import torch
except ImportError:
    logger.warning("`GTE Embedder` requires `pytorch` to be installed.")
else:

    @embed("str")
    def gte(batches: Iterable[List[str]]) -> Iterable[List[np.ndarray]]:
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        model = sentence_transformers.SentenceTransformer(
            "thenlper/gte-base", device=device
        )

        for batch in batches:
            embeddings = model.encode(batch, normalize_embeddings=True)
            yield list(embeddings)
