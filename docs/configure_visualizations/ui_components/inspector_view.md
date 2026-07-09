---
tags: []
id: inspector
sidebar_position: 20
slug: /docs/custom-visualizations/ui-components/inspector
---

# Inspector

The Inspector Widget is a component in Spotlight that lets you examine and edit the features of **individual data points** in your dataset.
With its multiple views for **different modalities**, the Inspector Widget provides a detailed look at a data point's underlying structure.

The Inspector Widget's views for text, audio, video, and 3D geometry data allow you to explore a data point's features in depth.
You can also edit those features directly within the view, making it easy to make changes to a data point without navigating to a separate screen.
The Inspector Widget is an essential tool for working with multimodal datasets and gives you greater control over the structure and quality of your data.

!!! info

    The open source version of Renumics Spotlight allows you to inspect your data to find critical segments. The Pro version of Spotlight also enables data tagging and annotation.

By configuring the inspector view you can choose how each datapoint should be represented. The main configuration options are available in the upper right corner of the view:

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/inspector-view/inspector-view-overview-720.jpg">
  <source src="../../../assets/data/docs/ui-components/inspector-view/inspector-view-overview-720.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/inspector-view/inspector-view-overview-720.mp4" type="video/mp4" />
</video>

_fsd50k_ - add and layout components in the **Inspector View**

There are visualization and interaction components available for many different data types. These include:

### Text data

**Text data** can be represented either with a **Value** view or a **Select** view that features autocomplete.

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/inspector-view/text-value-field-512.jpg">
  <source src="../../../assets/data/docs/ui-components/inspector-view/text-value-field-512.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/inspector-view/text-value-field-512.mp4" type="video/mp4" />
</video>

_fsd50k_ - display annotation in a **Value** view

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/inspector-view/text-select-field-720.jpg">
  <source src="../../../assets/data/docs/ui-components/inspector-view/text-select-field-720.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/inspector-view/text-select-field-720.mp4" type="video/mp4" />
</video>

_fsd50k_ - display and update annotation in a **Select** view

### Categorical data

**Categorical data** is represented similarly to **Text data** with the exception, that when there are not too many categories, they can also be edited with a switch component.

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/inspector-view/category-switch-field-512.jpg">
  <source src="../../../assets/data/docs/ui-components/inspector-view/category-switch-field-512.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/inspector-view/category-switch-field-512.mp4" type="video/mp4" />
</video>

_mnist_ - display and update categories in a **Switch** view

### Image data

**Image data** can be represented with an imager viewer that supports zooming and panning.

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/inspector-view/image-view-512.jpg">
  <source src="../../../assets/data/docs/ui-components/inspector-view/image-view-512.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/inspector-view/image-view-512.mp4" type="video/mp4" />
</video>

_mnist_ - display and zoom/pan images in a **Image** view

### Audio data

**Audio data** can be represented with an _Audio Player_ or a _Spectrogram_. The _Audio Player_ supports annotating event windows in the data.

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/inspector-view/audio-window-view-512.jpg">
  <source src="../../../assets/data/docs/ui-components/inspector-view/audio-window-view-512.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/inspector-view/audio-window-view-512.mp4" type="video/mp4" />
</video>

_fsd50k_ - display and control audio with/without an additional window

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/inspector-view/audio-window-edit-view-512.jpg">
  <source src="../../../assets/data/docs/ui-components/inspector-view/audio-window-edit-view-512.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/inspector-view/audio-window-edit-view-512.mp4" type="video/mp4" />
</video>

_fsd50k_ - edit audio window

### Video data

**Video data** can be represented with an _Video Player_.

### 3D Meshes

**3D meshes** can be represented by a _Mesh Viewer_. This components supports surface coloring to display mesh properties (e.g. stresses) and animated meshes.

### Boolean data

**Boolean data** can be represented by a _Switch_ element to facilitate efficient data annotation and tagging.

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/inspector-view/bool-switch-view-512.jpg">
  <source src="../../../assets/data/docs/ui-components/inspector-view/bool-switch-view-512.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/inspector-view/bool-switch-view-512.mp4" type="video/mp4" />
</video>

_fsd50k_ - edit bool values in **Switch** view
