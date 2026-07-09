---
tags: []
id: filter-bar
sidebar_position: 15
slug: /docs/custom-visualizations/ui-components/filter-bar
---

# Filter Bar

The Filter Bar is a key component of Spotlight's UI that allows you to filter your data based on specific criteria.
With the Filter Bar, you can quickly narrow down your dataset to a subset that meets your needs, making it easier to work with and analyze.

Using the Filter Bar is simple: just select the column and the predicate to filter by, and Spotlight will update the data views accordingly.

Additional you can convert any active Selection into a Filter and apply it on your dataset.
You can also combine all currently applied filters and rename the new Filter.

Most of the components Spotlight provides will react to data being filtered out of the dataset, and will update accordingly.<br />
The [Similarity Map](similarity_map.md) and others even have options to completely ignore all datapoints not in the filtered dataset.

## Adding a Predicate Filter

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/filter-bar/add-filter-720.jpg">
  <source src="../../../assets/data/docs/ui-components/filter-bar/add-filter-720.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/filter-bar/add-filter-720.mp4" type="video/mp4" />
</video>

_fsd50k_ - add Predicate Filters to the Filter Bar

## Disabling and Delating a Filter

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/filter-bar/disable-delete-filter-720.jpg">
  <source src="../../../assets/data/docs/ui-components/filter-bar/disable-delete-filter-720.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/filter-bar/disable-delete-filter-720.mp4" type="video/mp4" />
</video>

_fsd50k_ - disable and delete Predicate Filters from the Filter Bar

## Combining Filters

To create a new filter based on the currently applied filters, click the "Combine Filters" button.
This will merge all active filters into a new filter,
which you can rename to suit your needs.

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/filter-bar/combine-filters-720.jpg">
  <source src="../../../assets/data/docs/ui-components/filter-bar/combine-filters-720.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/filter-bar/combine-filters-720.mp4" type="video/mp4" />
</video>

_fsd50k_ - combine multiple filters into one

## Filter Selected

If you want to create a new filter based on the currently selected data points,
you can use the "Filter from Selection" feature.
This allows you to quickly turn your selection into a new filter

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/filter-bar/combine-selection-720.jpg">
  <source src="../../../assets/data/docs/ui-components/filter-bar/combine-selection-720.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/filter-bar/combine-selection-720.mp4" type="video/mp4" />
</video>

_fsd50k_ - combine the active selection into a filter

## Filter string column

At first glance, filtering string columns in Spotlight may appear similar to filtering other data types.
However, string filtering is actually much more powerful because it allows you to use
[regular expressions](https://en.wikipedia.org/wiki/Regular_expression) to filter matching strings.

This allows for filtering more complex patterns than just equality or inequality of two strings.

In order to find all labels columns in the _fsd50k_ dataset containing the label `Siren` or `Alarm` you can e.g. create the following filter:

`labels = Siren|Alarm`

Overall, the use of regular expressions in Spotlight's string filtering feature gives you greater flexibility
and control over your data analysis.
Whether you're filtering for simple patterns or using complex regular expressions to refine your dataset.

<video controls muted loop playsinline preload="metadata" poster="../../../assets/data/docs/ui-components/filter-bar/filter-regex-720.jpg">
  <source src="../../../assets/data/docs/ui-components/filter-bar/filter-regex-720.webm" type="video/webm" />
  <source src="../../../assets/data/docs/ui-components/filter-bar/filter-regex-720.mp4" type="video/mp4" />
</video>

_fsd50k_ - filter string columns using regular expressions
