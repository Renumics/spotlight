---
sidebar_position: 20
slug: /docs/loading-data
---

# Loading data

With Spotlight you can interactively explore your unstructured data directly from your dataframe. When the data is loaded into Spotlight, the tabular data (e.g. labels, metadata) is loaded into memory and you can use the web frontend to perform efficient in-memory analytics. Unstructured data samples (e.g. images, video, audio, time series) are loaded lazily from disk or web storage.

## Supported data formats

Spotlight can be started either through the Python API or via the Command Line Interface (CLI). Three different dataset representations are supported: [Pandas](https://pandas.pydata.org/) dataframes, [Huggingface datasets](https://huggingface.co/docs/datasets/index) and Spotlight datasets based on the HDF5-Format.

If you load your dataset via CLI, you can specify a file to be loaded. In this example we load a CSV file:

```bash
spotlight mnist-tiny.csv
```

With the Python API you can additionally load in-memory datasets. This is useful when working in a notebook. Loading a Pandas dataframe is as simple as:

```python
from renumics import spotlight

spotlight.show(df)
```

This table gives an overview over the supported data formats:

| Format                                      | CLI | Python API |
| ------------------------------------------- | --- | ---------- |
| CSV, Parquet, Feather, ORC (through Pandas) | ✅  | ✅         |
| Pandas in memory                            | ❌  | ✅         |
| Huggingface                                 | ❌  | ✅         |
| Spotlight HDF5                              | ✅  | ✅         |

## Supported data types

Spotlight supports a wide range of data types both for tabular and unstructured data types. When possible, the data types are automatically discovered.

It is also possible to manually specify data types for certain columns:

```python
from renumics import spotlight

dtype = {"image": spotlight.Image, "embedding":spotlight.Embedding}
spotlight.show(df, dtype=dtype)
```

We provide a more detailed description vor both [tabular data types](supported_data_types.md#tabular-data-types) and [unstructured data types](supported_data_types.md#unstructured-data-types).

## Load a Pandas dataset

Find [more information how to load your Pandas dataframe](loading_pandas_data.md) in just a few lines of code.

## Huggingface

Find [more information how to load your Hugging Face dataset](loading_huggingface_data.md) in just a few lines of code.

## Spotlight HDF5 dataset

Find more information how to use the [Spotlight HDF5 dataset format](loading_hdf5_data.md) to load complex multimdal data.
