---
tags: []
id: similarity-map
sidebar_position: 30
slug: /docs/custom-visualizations/ui-components/similarity-map
---

# Similarity Map

The Similarity Map projects the datapoints onto a 2D Map based on the similarity of the selected columns to place by. The Similarity is measured by either pre computed descriptions (e.G. embeddings retrieved from a ML workflow) or based on one or multiple scalar columns in the dataset.

## Placement

Simply select one ore more columns to ‘placeBy’ in the settings and watch the dimension reduction arranging the data on the map.

In order to compute the dimension reduction we offer two different algorithms:
[UMAP](https://arxiv.org/abs/1802.03426) and [PCA](https://en.wikipedia.org/wiki/Principal_component_analysis).
If the columns values have different distributions,
The reduction might run into problems and overestimate the impact of some columns.
To counteract this problem, a robust distance metric is available in the advanced settings.

Per default only reduced settings are available to control UMAP
which help you in configuring the reduction to place the samples with more weight on local vs. global similarities.
However, there also are advanced settings available in order give more control over the dimension reduction.

At the moment the samples can be placed by number columns and Embedding/Array columns.

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/similarity-map/placement-720.jpg">
  <source src="../../../assets/data/docs/ui-components/similarity-map/placement-720.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/similarity-map/placement-720.mp4" type="video/mp4" />
</video>

_fsd50k_ - place datapoints on the **similarity map** based on a column

## Controls

The map can be moved and zoomed by using the mouse.

Zooming can be done with the mousewheel, resetting zoom can be done with the `Fit points` button.

The map can be moved by clicking the `middle mouse` button or with the `left mouse` button if the `alt` key is pressed simultaneously.

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/similarity-map/controls-720.jpg">
  <source src="../../../assets/data/docs/ui-components/similarity-map/controls-720.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/similarity-map/controls-720.mp4" type="video/mp4" />
</video>

_fsd50k_ - navigate in the **similarity map**

## Selection

Similar to the [data table](table_view.md), a single row can be added or removed from the selection.

In order to select a single point simply click on it. This will reset any selection and exclusively select the clicked point.

To add a point to a selection click on it while pressing `shift` and to remove it press `ctrl` while clicking on it.

These steps also apply for multiple points. By pressing the left mouse button and moving the mouse,
a selection rectangle will be shown. On releasing the left mouse button, the selection will be applied in the same fashion as it is done for a single point.

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/similarity-map/selection-720.jpg">
  <source src="../../../assets/data/docs/ui-components/similarity-map/selection-720.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/similarity-map/selection-720.mp4" type="video/mp4" />
</video>

_fsd50k_ - select and deselect points in the **similarity map**

## Coloring and Sizing

Coloring and sizing can be used to represent more columns on the map. The coloring palette can be altered in the global coloring settings.

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/similarity-map/coloring-scaling-720.jpg">
  <source src="../../../assets/data/docs/ui-components/similarity-map/coloring-scaling-720.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/similarity-map/coloring-scaling-720.mp4" type="video/mp4" />
</video>

_fsd50k_ - colorize and scale datapoints on the **similarity map** based on a column

## Filtering

Per default the similarity map also accounts for similarities of filtered out points.
In order to compute the similarities only on the filtered points,
`hide unfiltered` has to be checked.

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/similarity-map/filtering-720.jpg">
  <source src="../../../assets/data/docs/ui-components/similarity-map/filtering-720.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/similarity-map/filtering-720.mp4" type="video/mp4" />
</video>

_fsd50k_ - show/hide filtered datapoints on the **similarity map**
