---
title: Renumics Spotlight
---

# Renumics Spotlight

Spotlight helps you to **understand unstructured datasets** fast. Create **interactive
visualizations** from your dataframe with just a few lines of code, and leverage data
enrichments (e.g. embeddings, predictions, uncertainties) to **identify critical clusters**
in your data.

```python
import pandas as pd
from renumics import spotlight

df = pd.read_csv("https://raw.githubusercontent.com/Renumics/spotlight/refs/heads/main/data/mnist/mnist-tiny.csv")
spotlight.show(df, dtype={"image": spotlight.Image, "embedding": spotlight.Embedding})
```

## Where to go next

- [🚀 Getting Started](getting_started/index.md) — install Spotlight and load your first dataset.
- [Loading data](loading_data/index.md) — Pandas, Hugging Face, and HDF5 datasets.
- [Configure visualizations](configure_visualizations/index.md) — tailor the UI to your data.
- [Use cases](use_cases/index.md) — worked examples across audio, vision, NLP, and multimodal data.
- [Data-centric AI workflows](data-centric_ai/playbook/index.md) — a playbook of data-curation plays.
- [API reference](API/index.md) — the `renumics.spotlight` Python API.
