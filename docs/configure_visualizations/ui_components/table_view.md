---
tags: []
id: data-table
sidebar_position: 40
slug: /docs/custom-visualizations/ui-components/data-table
---

# Data Table

The Table View is used to display all datapoints, that can be found in the dataset.
Each datapoint is displayed in a single row with each of its attributes in a separate column.

Columns visibility can be adjusted via the settings menu located in the right top corner of the **data table**.

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/table-view/visibility-720.jpg">
  <source src="../../../assets/data/docs/ui-components/table-view/visibility-720.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/table-view/visibility-720.mp4" type="video/mp4" />
</video>

_fsd50k_ - change column visibility in the **table view**

At the top of the **data table**, 3 Tabs are available in order to control what the **data table** is displaying.
All, Filtered and Selected, where All will simply show all available datapoints,
Filtered will only show datapoints that have not been excluded via Filters and Selected displays all selected datapoints.

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/table-view/tabs-720.jpg">
  <source src="../../../assets/data/docs/ui-components/table-view/tabs-720.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/table-view/tabs-720.mp4" type="video/mp4" />
</video>

_fsd50k_ - navigate the **data table`s** tabs

## Ordering

There are two kinds of orderings in the **data table**. Row ordering and Column ordering.

Row ordering can be controlled by clicking on the column header. A sorting indicator will be displayed in the header column.
By repeatedly clicking the header, the sorting is toggled.

In order to apply multiple orderings simply hold `ctrl` and add more columns to the ordering by clicking on their headers.
The last added ordering takes precedence over other orderings.

Column ordering can be controlled via the order attribute defined while appending a column in backstage.

### Importance

In order to help in the identification of possibly relevant rows regarding a group of selected rows,
we calculate an indicator, that tries to emphasise important columns. The importance of a column is
calculated by comparing the value distribution of all selected rows to the value distribution of all filtered rows.

In the `settings` the columns can be ordered by their calculated relevance.

## Creating Rows and Columns

A new column can be created by clicking on the `Add Column` button.
In order to create a new row duplicate an existing row by right clicking on it and selecting `Duplicate Row`.

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/table-view/create-720.jpg">
  <source src="../../../assets/data/docs/ui-components/table-view/create-720.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/table-view/create-720.mp4" type="video/mp4" />
</video>

_fsd50k_ - create new columns/rows in the **data table`s**

## Deleting Rows and Columns

Rows and columns can be deleted via the context menu that can be made visible by right clicking on a row or column.

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/table-view/delete-720.jpg">
  <source src="../../../assets/data/docs/ui-components/table-view/delete-720.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/table-view/delete-720.mp4" type="video/mp4" />
</video>

_fsd50k_ - create new columns in the **data table`s**

## Editing

To edit a single cell simply click on a selected cell and the editing dialog will appear.
To accept an edit hit enter. To cancel an edit simply click somewhere else in the data table or hit esc.

In order to edit multiple or all cells, the context menu can be made visible by right clicking on one of the cells to be edited.

At the moment most of the available scalar columns can be edited.

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/table-view/editing-720.jpg">
  <source src="../../../assets/data/docs/ui-components/table-view/editing-720.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/table-view/editing-720.mp4" type="video/mp4" />
</video>

_fsd50k_ - edit cells in the **data table`s**

## Filtering

By using the context menu you can directly filter the data table by the selected cell.

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/table-view/filtering-720.jpg">
  <source src="../../../assets/data/docs/ui-components/table-view/filtering-720.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/table-view/filtering-720.mp4" type="video/mp4" />
</video>

_fsd50k_ - edit cells in the **data table`s**
