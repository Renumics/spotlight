"""
A decorator for data analysis functions
"""

from typing import Callable, Iterable, List, Optional, Type, Any
import itertools
import io
import av
import numpy as np
import PIL.Image
from numpy._typing import DTypeLike
from numpy.lib import math
from renumics.spotlight import dtypes

from renumics.spotlight.dtypes import create_dtype

from renumics.spotlight.embeddings.exceptions import CannotEmbed
from .typing import Embedder
from .registry import register_embedder


def embedder(klass: Type[Embedder]) -> Type[Embedder]:
    """
    register an embedder class
    """
    register_embedder(klass)
    return klass


def embed(accepts: DTypeLike, *, sampling_rate: Optional[int] = None):
    dtype = create_dtype(accepts)

    if dtypes.is_image_dtype(dtype):

        def _preprocess_batch(raw_values: List[bytes]):
            return [PIL.Image.open(io.BytesIO(value)) for value in raw_values]

    elif dtypes.is_audio_dtype(dtype):
        if sampling_rate is None:
            raise ValueError(
                "No sampling rate specified, but required for `audio` embedding."
            )

        def _preprocess_batch(raw_values: Any):
            resampled_batch = []
            for raw_data in raw_values:
                with av.open(io.BytesIO(raw_data), "r") as container:
                    resampler = av.AudioResampler(
                        format="dbl", layout="mono", rate=16000
                    )
                    data = []
                    for frame in container.decode(audio=0):
                        resampled_frames = resampler.resample(frame)
                        for resampled_frame in resampled_frames:
                            frame_array = resampled_frame.to_ndarray()[0]
                            data.append(frame_array)
                    resampled_batch.append(np.concatenate(data, axis=0))
            return resampled_batch

    else:

        def _preprocess_batch(raw_values: Any):
            return raw_values

    def decorate(
        func: Callable[[Iterable[list]], Iterable[List[Optional[np.ndarray]]]]
    ):
        class EmbedderImpl(Embedder):
            def __init__(self, data_store: Any, column: str):
                self.dtype = dtype
                if data_store.dtypes[column].name != self.dtype.name:
                    raise CannotEmbed()

                self.data_store = data_store
                self.column = column
                self.batch_size = 16

                self._occupied_indices = []

            def _iter_batches(self):
                self._occupied_indices = []
                batch = []
                for i in range(len(self.data_store)):
                    value = self.data_store.get_converted_value(
                        self.column, i, simple=False, check=False
                    )

                    if value is None:
                        continue

                    self._occupied_indices.append(i)
                    batch.append(value)
                    if len(batch) == self.batch_size:
                        yield _preprocess_batch(batch)
                        batch = []

            def __call__(self) -> np.ndarray:
                embeddings = itertools.chain(*func(self._iter_batches()))
                res = np.empty(len(self.data_store), dtype=np.object_)
                res[self._occupied_indices] = list(embeddings)
                return res

        register_embedder(EmbedderImpl)

    return decorate
