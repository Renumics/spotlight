import io
from typing import Any, List

from PIL import Image
import numpy as np
import transformers

from renumics.spotlight import dtypes
from renumics.spotlight.embeddings.decorator import embedder
from renumics.spotlight.embeddings.exceptions import CannotEmbed
from renumics.spotlight.embeddings.registry import unregister_embedder
from renumics.spotlight.embeddings.typing import Embedder
from renumics.spotlight.logging import logger

try:
    import torch
except ImportError:
    logger.warning("`ViTEmbedder` requires `pytorch` to be installed.")
    _torch_available = False
else:
    _torch_available = True


@embedder
class ViTEmbedder(Embedder):
    def __init__(self, data_store: Any, column: str) -> None:
        if not dtypes.is_image_dtype(data_store.dtypes[column]):
            raise CannotEmbed
        self._data_store = data_store
        self._column = column

        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        model_name = "google/vit-base-patch16-224"
        self.processor = transformers.AutoImageProcessor.from_pretrained(model_name)
        self.model = transformers.ViTModel.from_pretrained(model_name).to(self.device)

    def __call__(self) -> np.ndarray:
        values = self._data_store.get_converted_values(
            self._column, indices=slice(None), simple=False, check=False
        )
        none_mask = [sample is None for sample in values]
        if all(none_mask):
            return np.array([None] * len(values), dtype=np.object_)

        embeddings = self.embed_images(
            [Image.open(io.BytesIO(value)) for value in values if value is not None]
        )

        if any(none_mask):
            res = np.empty(len(values), dtype=np.object_)
            res[np.nonzero(~np.array(none_mask))[0]] = list(embeddings)
            return res

        return embeddings

    def embed_images(self, batch: List[Image.Image]) -> np.ndarray:
        images = [image.convert("RGB") for image in batch]
        inputs = self.processor(images=images, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs.to(self.device))
        embeddings = outputs.last_hidden_state[:, 0].cpu().numpy()

        return embeddings


if not _torch_available:
    unregister_embedder(ViTEmbedder)
