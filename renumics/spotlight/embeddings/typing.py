"""
Shared types for embeddings
"""

from typing import Any, Callable, Optional

import numpy as np


Embedder = Callable[[Any, str], Optional[np.ndarray]]
