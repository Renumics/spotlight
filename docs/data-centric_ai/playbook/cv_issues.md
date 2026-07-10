---
tags: []
id: cv-issues
sidebar_position: 85
slug: /docs/data-centric-ai/playbook/cv-issues
---

# Find typical issues in image datasets with Cleanvision

We extract typical issues (regarding brightness, blurr, aspect ratio, SNR and duplicates) in image datasets with the [Cleanvision library](https://github.com/cleanlab/cleanvision). We then identify critical segments with Spotlight.

> Use Chrome to run Spotlight in Colab. Due to Colab restrictions (e.g. no websocket support), the performance is limited. Run the notebook locally for the full Spotlight experience.

[Open In Colab](https://colab.research.google.com/github/Renumics/spotlight/blob/main/playbook/veteran/cv_issues.ipynb)

=== "inputs"

    -   `df['image']` contains the paths to the [images](../glossary/index.md#image-data) in the dataset

=== "outputs"

    -   `df['dark_score']` contains a score [0,1] that denotes the [darkness](../glossary/index.md#darkness) of the image sample.
    -   `df['light_score']` contains a score [0,1] that denotes the [lightness](../glossary/index.md#lightness) of the image sample.
    -   `df['blurry_score']` contains a score [0,1] that denotes the [blurriness](../glossary/index.md#blurr) of the image sample.
    -   `df['low_information_score']` contains a score [0,1] that denotes the [Signal-to-Noise ratio](../glossary/index.md#signal-to-noise-ratio) of the image sample.
    -   `df['odd_aspect_ratio_score']` contains a score [0,1] that denotes anomalies in the [aspect ratio](../glossary/index.md#aspect-ratio) of the image sample.

=== "parameters"

![Spotlight_screenshot_outliers](../../assets/playbook/outlier_cleanlab_screenshot.png)

## Imports and play as copy-n-paste functions

??? note "# Install dependencies"

    ```python
    #@title Install required packages with PIP

    !pip install renumics-spotlight cleanlab datasets
    ```

??? note "# Play as copy-n-paste functions"

    ```python
    #@title Play as copy-n-paste functions

    from cleanvision.imagelab import Imagelab
    import pandas as pd
    from renumics import spotlight
    import requests

    def cv_issues_cleanvision(df, image_name='image'):

        image_paths = df['image'].to_list()
        imagelab = Imagelab(filepaths=image_paths)
        imagelab.find_issues()

        df_cv=imagelab.issues.reset_index()

        return df_cv
    ```

## Step-by-step example on CIFAR-100

### Load CIFAR-100 from Huggingface hub and convert it to Pandas dataframe

```python
dataset = datasets.load_dataset("renumics/cifar100-enriched", split="train")
df = dataset.to_pandas()
```

### Compute heuristics for typical image data error scores with Cleanvision

```python
df_cv=cv_issues_cleanvision(df)
df = pd.concat([df, df_cv], axis=1)
```

### Inspect errors and detect problematic data segments with Spotlight

```python
df_show = df.drop(columns=['embedding', 'probabilities'])
layout_url = "https://raw.githubusercontent.com/Renumics/spotlight/playbook/playbook/rookie/cv_issues.json"
response = requests.get(layout_url)
layout = spotlight.layout.nodes.Layout(**json.loads(response.text))
spotlight.show(df_show, dtype={"image": spotlight.Image, "embedding_reduced": spotlight.Embedding}, layout=layout)
```
