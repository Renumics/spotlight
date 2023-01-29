# <img src="https://spotlight.renumics.com/img/spotlight.svg" width="25"> Renumics Spotlight

![GitHub](https://img.shields.io/github/license/renumics/spotlight)

 Spotlight helps you to **identify critical data segments and model failure modes**. It enables you to build and maintain reliable machine learning models by **curating high-quality datasets**.

> We are in the process of releasing the core version of Renumics Spotlight on Github und the MIT license. Spotlight is already available on [PyPI](https://pypi.org/project/renumics-spotlight/).

- [Homepage](https://www.renumics.com)
- [Documentation](https://spotlight.renumics.com)
- [Github](https://github.com/renumics/spotlight)
- [Slack](link here)


## 🚀 Introduction

Spotlight is built on the idea that you can only **truly understand unstructured datasets** if you can **interactively explore** them. Its core principle is to identify and fix critical data segments by leveraging **data enrichments** (e.g. features, embeddings, uncertainties). Pre-defined templates (link: recipes) for typical data curation workflows get you started quickly and connect your stack to the data-centric AI ecosystem.

We at [Renumic](https://renumics.com) are building Spotlight for cross-functional teams that want to be in **control of their data and data curation processes**. Currently, Spotlight supports many use cases based on image, audio, video and time series data. 



## ⏱️ Quickstart

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

df = pd.read_csv("sample.csv")
spotlight.show(df)
```
> `pd.read_csv` loads a sample csv file as a pandas [DataFrame](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html).

> `spotlight.show(df)` opens up spotlight in the browser with the pandas dataframe ready for you to explore.

## 🧭 Start by use case

You can adapt Spotlight to your data curation tasks. To get you started quickly, we are continuously developing pre-defined recipes for common workflows. 

#### Get started quickly with our Examples:
- [Evaluate Model](../examples/evaluate_model.mdx)
- [Find label inconsistencies](../examples/find_label_inconsistencies.mdx)
- [Find noisy samples](../examples/find_noisy_samples.mdx)
- [Select featues](../examples/select_features.mdx)

#### Tell us which data curation task is important for your work:
- Join our channel on [Slack](???)
- Open an issue on [Github](https://github.com/renumics)
- Have a [coffee talk](https://calendly.com/stefan-suwelack/dcai-intro-30-min) with us 
