---
sidebar_position: 10
slug: /docs/configure-visualizations/ui-components
---

# 🎛 UI components

> If you want to follow these examples hands-on, you can use the Spotlight example instances fired up in the [🚀 Getting Started](../../getting_started/index.md) section.<br />
> Examples will be annotated with the corresponding datasets name. You can use the tabs below for a quick reminder on how to load those datasets into Spotlight.

=== "mnist"

    ```bash
    curl https://raw.githubusercontent.com/Renumics/spotlight/refs/heads/main/data/mnist/mnist-tiny.csv -o mnist-tiny.csv
    spotlight mnist-tiny.csv --dtype image=Image --dtype embedding=Embedding --dtype label=Category
    ```

=== "fsd50k"

    ```bash
    curl https://raw.githubusercontent.com/Renumics/spotlight/main/data/fsd50k/fsd50k-tiny.csv -o fsd50k-tiny.csv
    spotlight fsd50k-tiny.csv --dtype window=Window --dtype embedding=Embedding --dtype audio=Audio
    ```

<br />

Spotlight includes the [Inspector](./inspector_view.md) and the [Data Table](./table_view.md) to help you in analyzing and understanding individual datapoints. Other visualization options like the [Similarity Map](./similarity_map.md), the [Scatter Plot](./scatter_plot.md) and the [Histogram](./histogram.md) aide you to understand the overall distribution of your data.

The [Filter Bar](./filter_bar.md) is a special component that allows you to filter your data based on the values of your features.<br/>
Filtering and selecting datapoints can affect how data is presented in the other components and therefore can greatly help you in analyzing and reasoning about your data.

### Data Table

The [data table](./table_view.md) often is the primary view on the data.
In addition to several options that control which data is displayed, the table view also allows to edit datapoints.
This includes the creation of new columns.

### Inspector

The [inspector](./inspector_view.md) lets you examine individual data points in depth by providing multiple different views for many of the data types supported by Spotlight.
Including images, audio, 3D meshes and more.

### Similarity map

The [similarity map](./similarity_map.md) is a core element of most data-centric AI workflows.
It allows for to map a given vector to a scatter plot by using a dimensionality reduction via UMAP or PCA.
Different normalization options are available to handle metadata and embeddings. Additionally, dots on the scatter plot can be colored and sized.

### Scatter plot

The [scatter plot](./scatter_plot.md) is typically useful as a supporting view to determine correlation between metadata information.
Several aspects of the view can be customized dot size and color.

### Histogram

The [histogram view](./histogram.md) can be stacked to provide inside into data segments over two different dimensions.
