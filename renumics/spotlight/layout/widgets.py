"""
Implementation of widget models and interfaces for widget creation.
"""

from typing import List, Optional

from pydantic import BaseModel, Field
from typing_extensions import Literal

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
    name: Optional[str] = None
    config: Optional[WidgetConfig] = None
    kind: Literal["widget"] = "widget"


class HistogramConfig(WidgetConfig):
    """
    Histogram configuration model.
    """

    column: Optional[str] = Field(None, alias="columnKey")
    stack_by_column: Optional[str] = Field(None, alias="stackByColumnKey")
    filter: bool = Field(False, alias="filter")


class Histogram(Widget):
    """
    Spotlight histogram model.
    """

    type: Literal["histogram"] = "histogram"
    config: Optional[HistogramConfig] = None


class ScatterplotConfig(WidgetConfig):
    """
    Scatter plot configuration model.
    """

    x_column: Optional[str] = Field(None, alias="xAxisColumn")
    y_column: Optional[str] = Field(None, alias="yAxisColumn")
    color_by_column: Optional[str] = Field(None, alias="colorBy")
    size_by_column: Optional[str] = Field(None, alias="sizeBy")
    filter: bool = Field(False, alias="filter")


class Scatterplot(Widget):
    """
    Spotlight scatter plot model.
    """

    type: Literal["scatterplot"] = "scatterplot"
    config: Optional[ScatterplotConfig] = None


TableView = Literal["full", "filtered", "selected"]


class TableConfig(WidgetConfig):
    """
    Table configuration model.
    """

    active_view: TableView = Field("full", alias="tableView")
    visible_columns: Optional[List[str]] = Field(None, alias="visibleColumns")
    sort_by_columns: Optional[List[List[str]]] = Field(None, alias="sorting")
    order_by_relevance: bool = Field(False, alias="orderByRelevance")


class Table(Widget):
    """
    Spotlight table model.
    """

    type: Literal["table"] = "table"
    config: Optional[TableConfig] = None


ReductionMethod = Literal["umap", "pca"]
UmapMetric = Literal[
    "euclidean", "standardized euclidean", "robust euclidean", "cosine", "mahalanobis"
]
PCANormalization = Literal["none", "standardize", "robust standardize"]


class SimilaritymapConfig(WidgetConfig):
    """
    Similarity map configuration model.
    """

    columns: Optional[List[str]] = Field(None, alias="placeBy")
    reduction_method: Optional[ReductionMethod] = Field(None, alias="reductionMethod")
    color_by_column: Optional[str] = Field(None, alias="colorBy")
    size_by_column: Optional[str] = Field(None, alias="sizeBy")
    filter: bool = Field(False, alias="filter")
    umap_nn: Optional[int] = Field(None, alias="umapNNeighbors")
    umap_metric: Optional[UmapMetric] = Field(None, alias="umapMetric")
    umap_min_dist: Optional[float] = Field(None, alias="umapMinDist")
    pca_normalization: Optional[PCANormalization] = Field(
        None, alias="pcaNormalization"
    )
    umap_balance: Optional[float] = Field(None, alias="umapMenuLocalGlobalBalance")
    umap_is_advanced: bool = Field(False, alias="umapMenuIsAdvanced")


class Similaritymap(Widget):
    """
    Spotlight similarity map model.
    """

    type: Literal["similaritymap"] = "similaritymap"
    config: Optional[SimilaritymapConfig] = None


NumInspectorColumns = Literal[1, 2, 4, 6, 8]


class InspectorConfig(WidgetConfig):
    """
    Inspector configuration model.
    """

    lenses: Optional[List[Lens]] = Field(default_factory=None, alias="views")
    num_columns: NumInspectorColumns = Field(4, alias="visibleColumns")


class Inspector(Widget):
    """
    Spotlight inspector model.
    """

    type: Literal["inspector"] = "inspector"
    config: Optional[InspectorConfig] = None


class Issues(Widget):
    """
    Spotlight issues widget
    """

    type: Literal["IssuesWidget"] = "IssuesWidget"


WordCloudScaling = Literal["log", "linear", "sqrt"]


class WordCloudConfig(WidgetConfig):
    """
    Config for the Word Cloud Widget.
    """

    column: Optional[str] = Field(None, alias="cloudByColumnKey")
    min_word_length: Optional[int] = Field(None, alias="minWordLength")
    stop_words: Optional[List[str]] = Field(None, alias="stopwords")
    scaling: Optional[WordCloudScaling] = Field(None, alias="scaling")
    max_word_count: Optional[int] = Field(None, alias="wordCount")
    filter: Optional[bool] = Field(None, alias="hideFiltered")


class WordCloud(Widget):
    """
    Word Cloud Widget.
    """

    type: Literal["wordcloud"] = "wordcloud"
    config: Optional[WordCloudConfig] = None


class ConfusionMatrixConfig(WidgetConfig):
    """
    Config for the Confusion Matrix Widget.
    """

    x_column: Optional[str] = Field(None, alias="xColumn")
    y_column: Optional[str] = Field(None, alias="yColumn")
    filter: bool = Field(False, alias="filter")


class ConfusionMatrix(Widget):
    """
    Confusion Matrix Widget.
    """

    type: Literal["ConfusionMatrix"] = "ConfusionMatrix"
    config: Optional[ConfusionMatrixConfig] = None


class MetricWidgetConfig(WidgetConfig):
    """
    Config for the Metric Widget.
    """

    metric: Optional[str] = None
    columns: List[Optional[str]] = Field(default_factory=list, alias="columns")


class MetricWidget(Widget):
    """
    Metric Widget.
    """

    type: Literal["Metric"] = "Metric"
    config: Optional[MetricWidgetConfig] = None
