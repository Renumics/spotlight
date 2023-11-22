from typing import Any, Optional

import numpy as np

from renumics.spotlight import dtypes
from renumics.spotlight.embeddings.decorator import embedder


@embedder
def dummy(data_store: Any, column: str) -> Optional[np.ndarray]:
    if dtypes.is_image_dtype(data_store.dtypes[column]):
        return np.random.random((len(data_store), 4))
    return None
