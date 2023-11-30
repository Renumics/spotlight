from typing import Any, List

import numpy as np
import transformers
import av
import io

from renumics.spotlight import dtypes
from renumics.spotlight.embeddings.decorator import embedder
from renumics.spotlight.embeddings.exceptions import CannotEmbed
from renumics.spotlight.embeddings.typing import Embedder
from renumics.spotlight.logging import logger

try:
    import torch
except ImportError:
    logger.warning("`Wav2Vec Embedder` requires `pytorch` to be installed.")
else:

    @embedder
    class Wav2VecEmbedder(Embedder):
        def __init__(self, data_store: Any, column: str) -> None:
            if not dtypes.is_audio_dtype(data_store.dtypes[column]):
                raise CannotEmbed
            self._data_store = data_store
            self._column = column

        def __call__(self) -> np.ndarray:
            device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
            model_name = "facebook/wav2vec2-base-960h"
            sampling_rate = 16000
            processor = transformers.AutoFeatureExtractor.from_pretrained(model_name)
            model = transformers.AutoModel.from_pretrained(model_name).to(device)

            values = self._data_store.get_converted_values(
                self._column, indices=slice(None), simple=False, check=False
            )
            none_mask = [sample is None for sample in values]
            if all(none_mask):
                return np.array([None] * len(values), dtype=np.object_)

            def _embed_batch(batch: List[bytes]) -> np.ndarray:
                resampled_batch = []
                for raw_data in batch:
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

                inputs = processor(
                    raw_speech=resampled_batch,
                    sampling_rate=sampling_rate,
                    padding="longest",
                    return_tensors="pt",
                )
                with torch.no_grad():
                    outputs = model(**inputs.to(device))
                embeddings = outputs.last_hidden_state[:, 0].cpu().numpy()
                return embeddings

            embeddings = _embed_batch([value for value in values if value is not None])

            if any(none_mask):
                res = np.empty(len(values), dtype=np.object_)
                res[np.nonzero(~np.array(none_mask))[0]] = list(embeddings)
                return res

            return embeddings
