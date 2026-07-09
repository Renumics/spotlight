---
tags: []
id: histogram
sidebar_position: 45
slug: /docs/custom-visualizations/ui-components/histogram
---

# Histogram

The histogram component in Spotlight allows you to visualize the distribution of your data across a continuous range of values.
This can be particularly useful when working with numerical or categorical data, as it gives you a quick and easy way to identify patterns,
outliers, and other characteristics of your dataset.

The histogram component works by grouping your data into a series of bins, each of which represents a specific range of values.
It supports two different modes: single Column and stacked histogram.

The single Column mode is the default mode, and it allows you to
visualize the distribution of a single variable.
By specifying a column to `stackBy` the distribution of values for this column are plotet for each bin.

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/histogram/placement-720.jpg">
  <source src="../../../assets/data/docs/ui-components/histogram/placement-720.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/histogram/placement-720.mp4" type="video/mp4" />
</video>

_fsd50k_ - analyze column distribution in **histogram**

## Filtering

Per default the histogram also accounts for filtered out points and displays them greyed out.
In order to hide all filtered values and recompute the displayed bins based on the active filters `hide unfiltered` has to be checked.

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/histogram/filtering-720.jpg">
  <source src="../../../assets/data/docs/ui-components/histogram/filtering-720.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/histogram/filtering-720.mp4" type="video/mp4" />
</video>

_fsd50k_ - show/hide filtered datapoints in the **histogram**
