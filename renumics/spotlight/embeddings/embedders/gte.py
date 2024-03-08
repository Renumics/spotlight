from typing import Iterable, List, Optional

import numpy as np
import transformers

from renumics.spotlight.embeddings.decorator import embed
from renumics.spotlight.logging import logger

try:
    import torch
    import torch.nn.functional as F
except ImportError:
    logger.warning("GTE embedder requires `pytorch` to be installed.")
else:

    def average_pool(
        last_hidden_state: torch.Tensor, attention_mask: torch.Tensor
    ) -> torch.Tensor:
        masked_last_hidden_state = last_hidden_state.masked_fill(
            ~attention_mask[..., None].bool(), 0.0
        )
        return (
            masked_last_hidden_state.sum(dim=1) / attention_mask.sum(dim=1)[..., None]
        )

    @embed("str")
    def gte(batches: Iterable[List[str]]) -> Iterable[List[Optional[np.ndarray]]]:
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        model_name = "thenlper/gte-base"
        tokenizer = transformers.AutoTokenizer.from_pretrained(model_name)
        model = transformers.AutoModel.from_pretrained(model_name).to(device)

        for batch in batches:
            inputs = tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=512,
                return_tensors="pt",
            )
            with torch.no_grad():
                outputs = model(**inputs)
                embeddings = average_pool(
                    outputs.last_hidden_state, inputs["attention_mask"]
                )
                embeddings = F.normalize(embeddings, p=2, dim=1).cpu().numpy()
            yield list(embeddings)
