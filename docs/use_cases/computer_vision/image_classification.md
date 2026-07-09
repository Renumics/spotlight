---
tags: []
id: image-classification
slug: /docs/use-cases/image-classification
---

# Detect Problems in Image Classification Datasets

Use the [**sliceguard**](https://github.com/Renumics/sliceguard) library and [**Spotlight**](https://github.com/Renumics/spotlight) to quickly **detect problem clusters** that can cause issues when training your image classification model. Shows problems such as:

1. Label Inconsistencies
2. Outliers and Errors
3. Image-specific Issues (e.g. blurry images)

Generally it will show you everything that is hard to learn for a classification model. All you need is a dataframe containing **paths to image files** and **labels**.

First install the dependencies:

```
pip install renumics-spotlight sliceguard[all] scikit-learn
```

Then run the following code to detect problematic clusters:

```python
# The Imports
from renumics import spotlight
from sliceguard import SliceGuard
from sliceguard.data import from_huggingface
from sklearn.metrics import accuracy_score

# Load an Example Dataset as DataFrame
df = from_huggingface("Matthijs/snacks")

# DataFrame Format:
# +-------------------+---------+
# |       image       |  label  |
# +-------------------+---------+
# | /path/to/img1.png | popcorn |
# | /path/to/img2.png | muffin  |
# | /path/to/img3.png | cake    |
# | ...               |         |
# +-------------------+---------+

# Detect Issues Using sliceguard
sg = SliceGuard()
issues = sg.find_issues(df, features=["image"], y="label", metric=accuracy_score)
report_df, spotlight_data_issues, spotlight_dtypes, spotlight_layout = sg.report(
    no_browser=True
)

# Visualize Detected Issues in Spotlight:
spotlight.show(
    report_df,
    dtype=spotlight_dtypes,
    issues=spotlight_data_issues,
    layout=spotlight_layout,
)

```
