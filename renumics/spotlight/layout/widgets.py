"""
Implementation of widget models and interfaces for widget creation.
"""

from typing import Literal, TypeAlias

from pydantic import BaseModel, Field

from .lenses import Lens


class WidgetConfig(BaseModel, populate_by_name=True):
    """
    Base Spotlight widget configuration model.
    """


class Widget(BaseModel, extra="forbid"):
    """
    Spotlight widget model.
    """

    type: str
    name: str | None = None
    config: WidgetConfig | None = None
    kind: Literal["widget"] = "widget"


class HistogramConfig(WidgetConfig):
    """
    Histogram configuration model.
    """

    column: str | None = Field(None, alias="columnKey")
    stack_by_column: str | None = Field(None, alias="stackByColumnKey")
    filter: bool = Field(False, alias="filter")


class Histogram(Widget):
    """
    Spotlight histogram model.
    """

    type: Literal["histogram"] = "histogram"
    config: HistogramConfig | None = None


class ScatterplotConfig(WidgetConfig):
    """
    Scatter plot configuration model.
    """

    x_column: str | None = Field(None, alias="xAxisColumn")
    y_column: str | None = Field(None, alias="yAxisColumn")
    color_by_column: str | None = Field(None, alias="colorBy")
    size_by_column: str | None = Field(None, alias="sizeBy")
    filter: bool = Field(False, alias="filter")


class Scatterplot(Widget):
    """
    Spotlight scatter plot model.
    """

    type: Literal["scatterplot"] = "scatterplot"
    config: ScatterplotConfig | None = None


TableView: TypeAlias = Literal["full", "filtered", "selected"]


class TableConfig(WidgetConfig):
    """
    Table configuration model.
    """

    active_view: TableView = Field("full", alias="tableView")
    visible_columns: list[str] | None = Field(None, alias="visibleColumns")
    sort_by_columns: list[list[str]] | None = Field(None, alias="sorting")
    order_by_relevance: bool = Field(False, alias="orderByRelevance")


class Table(Widget):
    """
    Spotlight table model.
    """

    type: Literal["table"] = "table"
    config: TableConfig | None = None


ReductionMethod: TypeAlias = Literal["umap", "pca"]
UmapMetric: TypeAlias = Literal[
    "euclidean", "standardized euclidean", "robust euclidean", "cosine", "mahalanobis"
]
PCANormalization: TypeAlias = Literal["none", "standardize", "robust standardize"]


class SimilaritymapConfig(WidgetConfig):
    """
    Similarity map configuration model.
    """

    columns: list[str] | None = Field(None, alias="placeBy")
    reduction_method: ReductionMethod | None = Field(None, alias="reductionMethod")
    color_by_column: str | None = Field(None, alias="colorBy")
    size_by_column: str | None = Field(None, alias="sizeBy")
    filter: bool = Field(False, alias="filter")
    umap_nn: int | None = Field(None, alias="umapNNeighbors")
    umap_metric: UmapMetric | None = Field(None, alias="umapMetric")
    umap_min_dist: float | None = Field(None, alias="umapMinDist")
    pca_normalization: PCANormalization | None = Field(None, alias="pcaNormalization")
    umap_balance: float | None = Field(None, alias="umapMenuLocalGlobalBalance")
    umap_is_advanced: bool = Field(False, alias="umapMenuIsAdvanced")


class Similaritymap(Widget):
    """
    Spotlight similarity map model.
    """

    type: Literal["similaritymap"] = "similaritymap"
    config: SimilaritymapConfig | None = None


NumInspectorColumns: TypeAlias = Literal[1, 2, 4, 6, 8]


class InspectorConfig(WidgetConfig):
    """
    Inspector configuration model.
    """

    lenses: list[Lens] | None = Field(None, alias="views")
    num_columns: NumInspectorColumns = Field(4, alias="visibleColumns")


class Inspector(Widget):
    """
    Spotlight inspector model.
    """

    type: Literal["inspector"] = "inspector"
    config: InspectorConfig | None = None


class Issues(Widget):
    """
    Spotlight issues widget
    """

    type: Literal["IssuesWidget"] = "IssuesWidget"


WordCloudScaling: TypeAlias = Literal["log", "linear", "sqrt"]


class WordCloudConfig(WidgetConfig):
    """
    Config for the Word Cloud Widget.
    """

    column: str | None = Field(None, alias="cloudByColumnKey")
    min_word_length: int | None = Field(None, alias="minWordLength")
    stop_words: list[str] | None = Field(None, alias="stopwords")
    scaling: WordCloudScaling | None = Field(None, alias="scaling")
    max_word_count: int | None = Field(None, alias="wordCount")
    filter: bool | None = Field(None, alias="hideFiltered")


class WordCloud(Widget):
    """
    Word Cloud Widget.
    """

    type: Literal["wordcloud"] = "wordcloud"
    config: WordCloudConfig | None = None


class ConfusionMatrixConfig(WidgetConfig):
    """
    Config for the Confusion Matrix Widget.
    """

    x_column: str | None = Field(None, alias="xColumn")
    y_column: str | None = Field(None, alias="yColumn")
    filter: bool = Field(False, alias="filter")


class ConfusionMatrix(Widget):
    """
    Confusion Matrix Widget.
    """

    type: Literal["ConfusionMatrix"] = "ConfusionMatrix"
    config: ConfusionMatrixConfig | None = None


class MetricWidgetConfig(WidgetConfig):
    """
    Config for the Metric Widget.
    """

    metric: str | None = None
    columns: list[str | None] = Field(default_factory=list, alias="columns")


class MetricWidget(Widget):
    """
    Metric Widget.
    """

    type: Literal["Metric"] = "Metric"
    config: MetricWidgetConfig | None = None
