"""
A decorator for data analysis functions
"""

import functools
from typing import Any, Callable, Dict, Literal, Optional, Union, overload

from renumics.spotlight import dtypes
from renumics.spotlight.media import Audio, Embedding, Image, Sequence1D

from .preprocessors import (
    preprocess_audio_batch,
    preprocess_batch,
    preprocess_image_batch,
)
from .registry import register_embedder
from .typing import EmbedArrayFunc, EmbedFunc, EmbedImageFunc, FunctionalEmbedder


@overload
def embed(
    dtype: Union[Literal["image", "Image"], Image], *, name: Optional[str] = None
) -> Callable[[EmbedImageFunc], EmbedImageFunc]: ...


@overload
def embed(
    dtype: Union[Literal["audio", "Audio"], Audio],
    *,
    name: Optional[str] = None,
    sampling_rate: int,
) -> Callable[[EmbedArrayFunc], EmbedArrayFunc]: ...


@overload
def embed(
    dtype: Union[
        Literal["embedding", "Embedding", "sequence1d", "Sequence1D"],
        Embedding,
        Sequence1D,
    ],
    *,
    name: Optional[str] = None,
) -> Callable[[EmbedArrayFunc], EmbedArrayFunc]: ...


@overload
def embed(
    dtype: Any, *, name: Optional[str] = None, sampling_rate: Optional[int] = None
) -> Callable[[EmbedFunc], EmbedFunc]: ...


def embed(
    dtype: Any, *, name: Optional[str] = None, sampling_rate: Optional[int] = None
) -> Callable[[EmbedFunc], EmbedFunc]:
    """
    Decorator for marking an embedding function as an Spotlight embedder for the
    given data type.

    The decorated function receives an iterable with preprocessed data batches
    as Python lists. Batches contain preprocessed data samples:
        Pillow images in case of an image embedder;
        mono channel audio PCM resampled to the given sampling rate as an double
            array in case of an audio embedder;
        raw data from Spotlight data store otherwise.
    The decorated function should return iterable with batches of embeddings.
    Embeddings must be represented by arrays of the same length, or `None` if an
    input sample cannot be embedded).

    Args:
        dtype: Spotlight data type which can be embedded with the given
            function. For more than one data type, use this decorator multiple
            times.
        name: Optional embedder name. If not given, the name of the decorated
            function will be used.
        sampling_rate: Optional sampling rate. Only relevant for audio
            embedders, otherwise ignored.

    Example of the [JinaAI v2 small](https://huggingface.co/jinaai/jina-embeddings-v2-small-en)
    model:
    ```python
    from typing import Iterable, List, Optional

    import numpy as np
    import transformers
    from renumics.spotlight import embed

    @embed("str", name="jina-v2-small")
    def jina_v2_small(batches: Iterable[List[str]]) -> Iterable[List[Optional[np.ndarray]]]:
        model = AutoModel.from_pretrained('jinaai/jina-embeddings-v2-small-en', trust_remote_code=True)
        for batch in batches:
            embeddings = model.encode(batch)
            yield list(embeddings)
    ```
    """
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
