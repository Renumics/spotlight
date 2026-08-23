---
tags: []
id: hflow-dataset-snapshot
slug: /docs/use-cases/hflow-dataset-snapshot
---

# Inspect robotics dataset snapshots from HFlow

[HFlow](https://github.com/Hebbian-Robotics/hflow) processes robotics
recordings into canonical MCAP episodes and a Parquet catalog of metadata,
quality measurements, tags, intervals, and derived artifacts. Its dataset
snapshot export packages a selected catalog view as standard Parquet tables
and, optionally, copies the referenced media into the same directory.

Use Spotlight to inspect the snapshot through a `pandas.DataFrame`. This
workflow doesn't require an HFlow-specific Spotlight adapter.

## Before you begin

Install HFlow, Spotlight, and the pandas Parquet reader on your local machine:

```bash
pip install hflow pandas pyarrow renumics-spotlight
```

## Export a self-contained snapshot

To select episodes and export their media, complete the following steps:

1. Select the episodes that you want to inspect:

    ```bash
    hflow curate \
      "SELECT episode_id FROM episodes WHERE status = 'ok'" \
      --output data/snapshot-manifest.parquet
    ```

2. Create a self-contained snapshot that includes the selected media:

    ```bash
    hflow export snapshot \
      --manifest data/snapshot-manifest.parquet \
      --output data/dataset-snapshot \
      --media copy
    ```

The export creates the following files:

- `samples.parquet`: One wide row per episode.
- `measurements.parquet`: Long-form quality evidence.
- `media.parquet`: An index of the exported artifacts.

Because the command uses copy mode, each media URI is a path relative to the
snapshot directory.

## Load image samples

To prepare the image samples for Spotlight, read the sample table, select rows
whose representative artifact is an image, and resolve the copied media paths:

```python
from pathlib import Path

import pandas as pd

snapshot_directory = Path("data/dataset-snapshot").resolve()
samples = pd.read_parquet(snapshot_directory / "samples.parquet")
image_samples = samples.loc[samples["media_kind"] == "image"].copy()
image_samples["media_uri"] = image_samples["media_uri"].map(
    lambda media_uri: str(snapshot_directory / media_uri)
)
```

HFlow uses a contact sheet as the representative artifact when one is
available. Otherwise, it selects an image before video, audio, and other
artifact types. The remaining sample columns include episode metadata, status,
version stamps, and numeric or boolean quality measurements. You can filter
and compare these columns alongside the preview.

## Open the snapshot in Spotlight

Declare the media column as an image and pass the `pandas.DataFrame` to
Spotlight:

```python
from renumics import spotlight

spotlight.show(image_samples, dtype={"media_uri": spotlight.Image})
```

## Optional: Load all media artifacts

If you need every camera or derived artifact, load
`media.parquet`, filter it by `artifact_name`, `producer`, `role`, or
`media_kind`, and join the selected rows to `samples.parquet` on `episode_id`.
You can also read the same snapshot with DuckDB, Polars, pandas, and other
tools.

For the complete table contract and reference-versus-copy behavior, see the
[HFlow dataset snapshot guide](https://github.com/Hebbian-Robotics/hflow/blob/main/docs/how-to/export-dataset-snapshot.md).
