---
tags: []
id: layout
sidebar_position: 10
slug: /docs/custom-visualizations/ui-components/layout
---

# Layout

Spotlights layout system works similar to the layout in normal desktop applications.<br />
You can add or remove widgets, rename them, move them around, resize and stack them.

If you find a layout that fits your needs you can easily save it and load it later.

## Add and Delete Widget

Widgets can easily be added to an existing Tab group by clicking on the + button in the top of the Tab group.
To delete a Widget click on the x button in the top of the Widget.

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/layout/add-delete-widget-720.jpg">
  <source src="../../../assets/data/docs/ui-components/layout/add-delete-widget-720.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/layout/add-delete-widget-720.mp4" type="video/mp4" />
</video>

_fsd50k_

## Resize Widgets

To resize a widget simply drag the widgets border and move it to the desired size.
By clicking on the maximize/minimize button a widget can be put to fullscreen mode and vice versa.

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/layout/resize-widget-720.jpg">
  <source src="../../../assets/data/docs/ui-components/layout/resize-widget-720.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/layout/resize-widget-720.mp4" type="video/mp4" />
</video>

_fsd50k_

## Move and Stack Widgets

To move a widget simply drag the widgets title bar and move it to the desired position.

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/layout/move-widget-720.jpg">
  <source src="../../../assets/data/docs/ui-components/layout/move-widget-720.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/layout/move-widget-720.mp4" type="video/mp4" />
</video>

_fsd50k_

## Rename Widgets

In order to rename a widget simply double-click on the widgets title bar and type in the new name.

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/layout/rename-widget-720.jpg">
  <source src="../../../assets/data/docs/ui-components/layout/rename-widget-720.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/layout/rename-widget-720.mp4" type="video/mp4" />
</video>

_fsd50k_

## Save, Load and Reset the Layout

Layouts can easily be saved, loaded or resetted by clicking on the layout button in the top right corner of the window.

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/layout/save-load-reset-layout-720.jpg">
  <source src="../../../assets/data/docs/ui-components/layout/save-load-reset-layout-720.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/layout/save-load-reset-layout-720.mp4" type="video/mp4" />
</video>

_fsd50k_

## Build a layout with the Python API

Instead of composing your layout in the UI and exporting it you can also build it with the Python API.

More information on the layout customization API can be found in the
[layout API documentation](../../API/layout.md). You can also look at our
[workflow examples](../../data-centric_ai/playbook/index.md) to browse through more complex examples.

This example illustrates the basic functionality:

```python
import pandas as pd
from renumics import spotlight
from renumics.spotlight import layout

df = pd.read_csv("https://spotlight.renumics.com/data/fsd50k/fsd50k-tiny.csv")
spotlight.show(
    df,
    dtype={"audio": spotlight.Audio, "embedding": spotlight.Embedding},
    layout=layout.layout(
        [
            [layout.table()],
            [
                layout.similaritymap(
                    columns=["embedding"],
                    color_by_column="annotation",
                    size_by_column="entropy",
                )
            ],
            [
                layout.histogram(
                    column="annotation", stack_by_column="prediction_incorrect"
                )
            ],
        ],
        layout.widgets.Inspector(),
    ),
)
```
