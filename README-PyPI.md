# Renumics Spotlight

> Spotlight helps you to **identify critical data segments and model failure modes**. It enables you to build and maintain reliable machine learning models by **curating a high-quality datasets**.

## Introduction

Spotlight is built on the idea that you can only truly **understand unstructured datasets** if you can **interactively explore** them. Its core principle is to identify and fix critical data segments by leveraging **data enrichments** (e.g. features, embeddings, uncertainties). We are building Spotlight for cross-functional teams that want to be in **control of their data and data curation processes**. Currently, Spotlight supports many use cases based on image, audio, video and time series data.

## Quickstart

Get started by installing Spotlight and loading your first dataset.

#### What you'll need

-   [Python](https://www.python.org/downloads/) version 3.8-3.10

#### Install Spotlight via [pip](https://packaging.python.org/en/latest/key_projects/#pip)

```bash
pip install renumics-spotlight
```

> We recommend installing Spotlight and everything you need to work on your data in a separate [virtual environment](https://docs.python.org/3/tutorial/venv.html)

#### Load a dataset and start exploring

```python
import pandas as pd
from renumics import spotlight

df = pd.read_csv("https://spotlight.renumics.com/data/mnist/mnist-tiny.csv")
spotlight.show(df, dtype={"image": spotlight.Image, "embedding": spotlight.Embedding})
```

> `pd.read_csv` loads a sample csv file as a pandas [DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html).

> `spotlight.show` opens up spotlight in the browser with the pandas dataframe ready for you to explore. The `dtype` argument specifies custom column types for the browser viewer.

#### Load a [Hugging Face](https://huggingface.co/) dataset

```python
import datasets
from renumics import spotlight

dataset = datasets.load_dataset("olivierdehaene/xkcd", split="train")
df = dataset.to_pandas()
spotlight.show(df, dtype={"image_url": spotlight.Image})
```

> The `datasets` package can be installed via pip.
