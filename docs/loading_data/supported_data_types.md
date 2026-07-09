---
title: 🧰 Supported data types
slug: /docs/loading-data/data-types
sidebar_position: 10
---

# Supported data types

Spotlight supports a wide range of data types both for tabular and unstructured data types. When possible, the data types are automatically discovered.

It is also possible to manually specify data types for certain columns:

```python
from renumics import spotlight

dtype = {"image": spotlight.Image, "embedding":spotlight.Embedding}
spotlight.show(df, dtype=dtype)
```

In the following sections, we decribe the supported data types in more detail.

## Tabular data types

Spotlight supports standard tabular data types like `str`, `int`, `float`, `bool` and `datetime`.

The `CategoryDType` is used to specify categorical variables. You can also specify a mapping for this data type. An important application is to specify a label mapping for a dataset. You simply supply a dictionary that maps the label string to the label number:

```python
label_mapping = {'cat': 0, 'dog': 1, 'mouse': 2}
spotlight.show(ds, dtype={'img': spotlight.Image, 'label': spotlight.dtypes.CategoryDType(categories=label_mapping)})
```

## Unstructured data types

Spotlight is designed to work well with a wide range of unstructured data. Thanks to the flexible Inspector widget, an arbitrary combination of these data types can be loaded into Spotlight. This is especially useful for complex multi-modal or multi-channel data.

Most data types can be supplied in two different ways: Either as a reference to a file (as a path or URL) or directly in the dataframe. In the following, we describe the supported unstructured data types in more detail.

### **Image**

The Spotlight data type for images is `spotlight.Image`.
Images can be supplied as reference to a [Pillow-compatible](https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html) file (path or URL). Alternatively, the following formats are supported: [Pillow](https://pillow.readthedocs.io/en/stable/) object, bytes or an [Array-like](https://numpy.org/devdocs/reference/typing.html#arraylike) format with the dimensions (n x m x c), where (n x m) denotes the resolution of the image and the number of channels c is in {1,3,4}.

### **Audio**

The Spotlight data type for Audio is `spotlight.Audio`.
Audio can be supplied as reference to a [PyAV-compatible](https://pyav.org/docs/stable/) file (path or URL). Alternatively, it can be directly loaded from raw bytes saved in the dataframe.

### **Mesh**

The Spotlight data type for images is `spotlight.Mesh`.
Meshes can be supplied as reference to a [trimesh-compatible](https://trimesh.org/) file (path or URL). Alternatively, it can be directly loaded from the dataframe as a trimesh object.

### **Video**

The Spotlight data type for images is `spotlight.Video`.
Videos can be supplied as reference to a file (path or URL). No encoding or decoding is currently performed by Spotlight, so only formats supported by your browser (.mp4, .ogg, .webm, .mov etc.) can be visualized in Spotlight.

### **Time series**

The Spotlight data type for time series data is `spotlight.Sequence1D`.
Time series data is loaded from an [Array-like](https://numpy.org/devdocs/reference/typing.html#arraylike) data structure in your dataframe column. The following dimensions are supported:

-   1D array of length n
-   2D array in the format (2,n) or (n,2) where your supply an index and the values (similar to [Pandas series](https://pandas.pydata.org/docs/reference/api/pandas.Series.html)).

### **Embedding**

The Spotlight data type for embedding data is `spotlight.Embedding`.
Embedding data is loaded from an [Array-like](https://numpy.org/devdocs/reference/typing.html#arraylike) data structure in your dataframe column. The embedding can have an arbitrary length n that is fixed for all data points.

### **Window**

The Spotlight data type for windows is `spotlight.Window`.
Windows are loaded as an [Array-like](https://numpy.org/devdocs/reference/typing.html#arraylike) data structure in your dataframe column. The dimensions are (2,n) to specify n windows with to coordinates each.
