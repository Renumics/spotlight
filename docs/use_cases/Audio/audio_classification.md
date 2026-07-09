---
tags: []
id: audio-classification
slug: /docs/use-cases/audio-classification
---

# Detect Problems in Audio Classification Datasets

Use the [**sliceguard**](https://github.com/Renumics/sliceguard) library and [**Spotlight**](https://github.com/Renumics/spotlight) to quickly **detect problem clusters** that can cause issues when training your audio classification model. Shows problems such as:

1. Label Inconsistencies
2. Outliers and Errors
3. Audio-specific Issues (e.g. clipping)

Generally it will show you everything that is hard to learn for a classification model. All you need is a dataframe containing **paths to audio files** and **labels**.

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
df = from_huggingface("renumics/emodb")

# DataFrame Format:
# +---------------------+---------+
# |        audio        | emotion |
# +---------------------+---------+
# | /path/to/audio1.wav | joy     |
# | /path/to/audio2.wav | anger   |
# | /path/to/audio3.wav | joy     |
# | ...                 |         |
# +---------------------+---------+

# Detect Issues Using sliceguard
sg = SliceGuard()
issues = sg.find_issues(df, features=["audio"], y="emotion", metric=accuracy_score)
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
