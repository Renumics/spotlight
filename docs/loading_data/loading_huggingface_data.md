---
title: 🤗 Loading Huggingface Data
slug: /docs/loading-data/huggingface
sidebar_position: 30
---

# Loading Data from Huggingface datasets

![Huggingface example](../assets/img/speech_commands_vis_s.gif)

The Hugging Face datasets library not only provides access to more than 70k publicly available datasets, but also offers very convenient data preparation pipelines for custom datasets.

Renumics Spotlight allows you to create interactive visualizations to identify critical clusters in your data. Because Spotlight understands the data semantics within Hugging Face datasets, you can get started with just one line of code:

```python
import datasets
from renumics import spotlight

ds = datasets.load_dataset('speech_commands', 'v0.01', split='validation')

spotlight.show(ds)
```

## Spotlight 🤝 Hugging Face datasets

The datasets library has several features that makes it an ideal tool for working with ML datasets: It stores tabular data (e.g. metadata, labels) along with unstructured data (e.g. images, audio) in a common Arrows table. Datasets also describes important data semantics through features (e.g. images, audio) and additional task-specific metadata.

Spotlight directly works on top of the datasets library. This means that there is no need to copy or pre-process the dataset for data visualization and inspection. Spotlight loads the tabular data into memory to allow for efficient, client-side data analytics. Memory-intensive unstructured data samples (e.g. audio, images, video) are loaded lazily on demand. In most cases, data types and label mappings are inferred directly from the dataset. Here, we visualize the CIFAR-100 dataset with one line of code:

```python
ds = datasets.load_dataset('cifar100', split='test')
spotlight.show(ds)
```

In cases where the data types are ambiguous or not specified, the Spotlight API allows to manually assign them:

```python
label_mapping = dict(zip(ds.features['fine_label'].names, range(len(ds.features['fine_label'].names))))
spotlight.show(ds, dtype={'img': spotlight.Image, 'fine_label': spotlight.dtypes.CategoryDType(categories=label_mapping)})
```

## Supported data types

More details on the supported data types can be found in the [data types section](supported_data_types.md#supported-data-types)

## Detailed examples

Take a look at our [use case section](../use_cases/index.md) to find more detailed examples for different modalities.
