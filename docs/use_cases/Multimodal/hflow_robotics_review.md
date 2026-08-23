---
tags: []
id: hflow-robotics-review
slug: /docs/use-cases/hflow-robotics-review
---

# Review physical-AI episodes exported by HFlow

[HFlow](https://github.com/Hebbian-Robotics/hflow) processes robotics and
physical-AI recordings into canonical MCAP episodes plus a Parquet catalog of
metadata, quality measurements, tags, intervals, and derived artifacts. Its
review export turns a selected catalog snapshot into standard Parquet tables
and optionally copies preview media beside them. Spotlight can inspect that
export through an ordinary pandas DataFrame; no HFlow-specific Spotlight
plugin is required.

## Export a self-contained review dataset

Install the dependencies:

```bash
pip install hflow pandas pyarrow renumics-spotlight
```

Assuming HFlow has processed recordings under `data/`, select the episodes to
review and copy their recorded artifacts into a portable directory:

```bash
hflow curate \
  "SELECT episode_id FROM episodes WHERE status = 'ok'" \
  --output data/review-manifest.parquet

hflow export review \
  --manifest data/review-manifest.parquet \
  --output data/review-export \
  --media copy
```

The export contains one wide row per episode in `episodes.parquet`, typed
long-form evidence in `measurements.parquet`, and an artifact index in
`media.parquet`. In copy mode each media URI is a path relative to the export
directory.

## Build the Spotlight DataFrame

Load the Parquet tables and add one contact-sheet column to the episode rows:

```python
from pathlib import Path

import pandas as pd

dataset_directory = Path("data/review-export").resolve()
episodes = pd.read_parquet(dataset_directory / "episodes.parquet")
media = pd.read_parquet(dataset_directory / "media.parquet")

contact_sheets = (
    media.loc[media["role"] == "contact_sheet", ["episode_id", "uri"]]
    .sort_values(["episode_id", "uri"])
    .drop_duplicates("episode_id")
    .rename(columns={"uri": "contact_sheet"})
)
review_rows = episodes.merge(contact_sheets, on="episode_id", how="left")
review_rows["contact_sheet"] = review_rows["contact_sheet"].map(
    lambda relative_path: str(dataset_directory / relative_path)
    if isinstance(relative_path, str)
    else relative_path
)
```

`episodes.parquet` already includes numeric and boolean quality measurements
as columns, so Spotlight can filter or sort by fields such as blackout share,
motion stability, or a user-defined review score while showing the associated
preview.

## Open the review in Spotlight

Declare the contact-sheet column as an image and pass the DataFrame to
Spotlight:

```python
from renumics import spotlight

spotlight.show(review_rows, dtype={"contact_sheet": spotlight.Image})
```

The same approach works for artifacts produced by custom HFlow enrichments.
Filter `media` by `artifact_name`, `producer`, `role`, or `media_kind`, pivot
the desired URI into the episode rows, and declare its Spotlight data type.
The source export remains a generic Parquet dataset that DuckDB, Polars, and
other review tools can read directly.

See HFlow's
[portable review export guide](https://github.com/Hebbian-Robotics/hflow/blob/main/docs/how-to/export-review-dataset.md)
for the full table contract and reference-versus-copy behavior.
