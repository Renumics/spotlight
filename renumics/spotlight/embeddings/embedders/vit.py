from typing import Iterable, List, Optional

import numpy as np
import PIL.Image
import transformers

from renumics.spotlight.embeddings.decorator import embed
from renumics.spotlight.logging import logger

try:
    import torch
except ImportError:
    logger.warning("ViT embedder requires `pytorch` to be installed.")
else:

    @embed("image")
    def vit(
        batches: Iterable[List[PIL.Image.Image]],
    ) -> Iterable[List[Optional[np.ndarray]]]:
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        model_name = "google/vit-base-patch16-224"
        processor = transformers.AutoImageProcessor.from_pretrained(model_name)
        model = transformers.ViTModel.from_pretrained(model_name).to(device)

        for batch in batches:
            images = [image.convert("RGB") for image in batch]
            inputs = processor(images=images, return_tensors="pt")
            with torch.no_grad():
                outputs = model(**inputs.to(device))
            embeddings = outputs.last_hidden_state[:, 0].cpu().numpy()

            yield list(embeddings)
