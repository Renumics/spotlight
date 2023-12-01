"""
A decorator for data analysis functions
"""

import functools
from typing import (
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Any,
    Union,
    overload,
)

import PIL.Image
import numpy as np
from renumics.spotlight import dtypes
from renumics.spotlight.media.audio import Audio
from renumics.spotlight.media.embedding import Embedding

from renumics.spotlight.media.image import Image
from renumics.spotlight.media.sequence_1d import Sequence1D
from .preprocessors import (
    preprocess_audio_batch,
    preprocess_batch,
    preprocess_image_batch,
)
from .registry import register_embedder
from .typing import EmbedFunc, FunctionalEmbedder


EmbedImageFunc = Callable[
    [Iterable[List[PIL.Image.Image]]], Iterable[List[Optional[np.ndarray]]]
]
EmbedArrayFunc = Callable[
    [Iterable[List[np.ndarray]]], Iterable[List[Optional[np.ndarray]]]
]


@overload
def embed(
    dtype: Union[Literal["image", "Image"], Image], *, name: Optional[str] = None
) -> Callable[[EmbedImageFunc], EmbedImageFunc]:
    ...


@overload
def embed(
    dtype: Union[Literal["audio", "Audio"], Audio],
    *,
    name: Optional[str] = None,
    sampling_rate: int,
) -> Callable[[EmbedArrayFunc], EmbedArrayFunc]:
    ...


@overload
def embed(
    dtype: Union[
        Literal["embedding", "Embedding", "sequence1d", "Sequence1D"],
        Embedding,
        Sequence1D,
    ],
    *,
    name: Optional[str] = None,
) -> Callable[[EmbedArrayFunc], EmbedArrayFunc]:
    ...


@overload
def embed(
    dtype: Any, *, name: Optional[str] = None, sampling_rate: Optional[int] = None
) -> Callable[[EmbedFunc], EmbedFunc]:
    ...


def embed(
    dtype: Any, *, name: Optional[str] = None, sampling_rate: Optional[int] = None
) -> Callable[[EmbedFunc], EmbedFunc]:
    dtype = dtypes.create_dtype(dtype)

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
