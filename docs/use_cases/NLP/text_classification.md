---
tags: []
id: text-classification
slug: /docs/use-cases/text-classification
---

# Detect Problems in Text Classification Datasets

Use the [**sliceguard**](https://github.com/Renumics/sliceguard) library and [**Spotlight**](https://github.com/Renumics/spotlight) to quickly **detect problem clusters** that can cause issues when training your text classification model. Shows problems such as:

1. Label Inconsistencies
2. Outliers and Errors
3. Text-specific Issues (e.g. typos, empty samples)

Generally it will show you everything that is hard to learn for a classification model. All you need is a dataframe containing **texts** and **labels**.

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
df = from_huggingface("dair-ai/emotion")

# DataFrame Format:
# +-------+-------+
# | text  | label |
# +-------+-------+
# | text1 | joy   |
# | text2 | anger |
# | text3 | joy   |
# | ...   |       |
# +-------+-------+

# Detect Issues Using sliceguard
sg = SliceGuard()
issues = sg.find_issues(df, features=["text"], y="label", metric=accuracy_score)
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
