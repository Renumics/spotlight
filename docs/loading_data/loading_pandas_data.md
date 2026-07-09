---
title: 🐼 Loading Data from Pandas
slug: /docs/loading-data/pandas
sidebar_position: 20
---

# Loading data from Pandas

Pandas dataframes are a very popular in-memory data structure. Unstructured data is typically stored as a file reference in the dataframe. However, Spotlight also supports dataframes that contain unstructured data as Numpy arrays or bytes.

Most column types are inferred automatically by Spotlight. Data types that are ambigous (e.g. embedding, time series) should be manually specified.

In this basic example, we load a dataframe froma .csv file and load it into Spotlight:

```python
import pandas as pd
from renumics import spotlight

df = pd.read_csv("https://renumics.com/data/mnist/mnist-tiny.csv")
spotlight.show(df, dtype={"image": spotlight.Image})
```

## Supported data types

More details on the supported data types can be found in the [data types section](supported_data_types.md#supported-data-types)

## Detailed examples

Take a look at our [use case section](../use_cases/index.md) to find more detailed examples for different modalities.
