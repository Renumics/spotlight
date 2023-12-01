"""
A decorator for data analysis functions
"""

import functools
from typing import Callable, Dict, Optional, Any
from renumics.spotlight import dtypes

from renumics.spotlight.dtypes import create_dtype
from renumics.spotlight.embeddings.preprocessors import (
    preprocess_audio_batch,
    preprocess_batch,
    preprocess_image_batch,
)
from .typing import EmbedFunc, FunctionalEmbedder
from .registry import register_embedder


def embed(
    dtype: Any, *, name: Optional[str] = None, sampling_rate: Optional[int] = None
) -> Callable[[EmbedFunc], EmbedFunc]:
    dtype = create_dtype(dtype)

    kwargs: Dict[str, Any] = {}

    if dtypes.is_image_dtype(dtype):
        kwargs["preprocess_func"] = preprocess_image_batch
    elif dtypes.is_audio_dtype(dtype):
        if sampling_rate is None:
            raise ValueError(
                "No sampling rate specified, but required for audio embedding."
            )

        kwargs["preprocess_func"] = functools.partial(
            preprocess_audio_batch, sampling_rate=sampling_rate
        )
    else:
        kwargs["preprocess_func"] = preprocess_batch

    def decorate(func: EmbedFunc) -> EmbedFunc:
        kwargs["embed_func"] = func
        register_embedder(
            FunctionalEmbedder,
            dtype,
            func.__name__ if name is None else name,
            **kwargs,
        )
        return func

    return decorate
