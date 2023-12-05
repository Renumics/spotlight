from typing import Iterable, List, Optional

import numpy as np
import transformers

from renumics.spotlight.embeddings.decorator import embed
from renumics.spotlight.logging import logger

try:
    import torch
except ImportError:
    logger.warning("Wav2Vec embedder requires `pytorch` to be installed.")
else:

    @embed("audio", sampling_rate=16000)
    def wav2vec2(
        batches: Iterable[List[np.ndarray]],
    ) -> Iterable[List[Optional[np.ndarray]]]:
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        model_name = "facebook/wav2vec2-base-960h"
        processor = transformers.AutoFeatureExtractor.from_pretrained(model_name)
        model = transformers.AutoModel.from_pretrained(model_name).to(device)

        for batch in batches:
            inputs = processor(
                raw_speech=batch,
                sampling_rate=16000,
                padding="longest",
                return_tensors="pt",
            )
            with torch.no_grad():
                outputs = model(**inputs.to(device))
            embeddings = outputs.last_hidden_state[:, 0].cpu().numpy()
            yield list(embeddings)
