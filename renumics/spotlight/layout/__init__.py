"""
This module allows user customize layout to start Spotlight from a python script/notebook.

A Spotlight layout consists of multiple widgets, grouped into tabs and splits.
"""

import os
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple, Union, cast, overload

import requests
import validators
from pydantic import ValidationError
from typing_extensions import Literal

from renumics.spotlight.backend.exceptions import InvalidLayout

from .lenses import Lens
from .nodes import (
    Layout,
    Split,
    Tab,
)
from .nodes import (
    Orientation as _Orientation,
)
from .widgets import (
    ConfusionMatrix,
    ConfusionMatrixConfig,
    Histogram,
    HistogramConfig,
    Inspector,
    InspectorConfig,
    Issues,
    MetricWidget,
    MetricWidgetConfig,
    Scatterplot,
    ScatterplotConfig,
    Similaritymap,
    SimilaritymapConfig,
    Table,
    TableConfig,
    WordCloud,
    WordCloudConfig,
)
from .widgets import (
    NumInspectorColumns as _NumInspectorColumns,
)
from .widgets import (
    PCANormalization as _PCANormalization,
)
from .widgets import (
    ReductionMethod as _ReductionMethod,
)
from .widgets import (
    TableView as _TableView,
)
from .widgets import (
    UmapMetric as _UmapMetric,
)
from .widgets import (
    Widget as _Widget,
)
from .widgets import (
    WordCloudScaling as _WordCloudScaling,
)

__all__ = [
    "layout",
    "split",
    "tab",
    "histogram",
    "inspector",
    "scatterplot",
    "similaritymap",
    "table",
    "issues",
    "wordcloud",
    "confusion_matrix",
    "metric",
]


_WidgetLike = Union[_Widget, str]
_NodeLike = Union[Split, Tab, _WidgetLike, List]
_LayoutLike = Union[str, os.PathLike, Layout, _NodeLike]


def layout(*nodes: _NodeLike, orientation: _Orientation = None) -> Layout:
    """
    Create a new layout with the given orientation and given nodes inside.
    """
    cleaned_nodes: List[Union[Split, Tab]]
    if all(isinstance(node, (_Widget, str)) for node in nodes):
        widgets = cast(Iterable[_WidgetLike], nodes)
        cleaned_nodes = [tab(*widgets)]
    else:
        cleaned_nodes = []
        for node in nodes:
            if isinstance(node, (Split, Tab)):
                cleaned_nodes.append(node)
            elif isinstance(node, (_Widget, str)):
                cleaned_nodes.append(tab(node))
            elif isinstance(node, list):
                if all(isinstance(subnode, (_Widget, str)) for subnode in node):
                    # All widgets inside, group them into one tab.
                    cleaned_nodes.append(tab(*node))
                else:
                    # Non-homogeneous content, wrap into a split.
                    cleaned_nodes.append(split(*node))
            else:
                raise TypeError(
                    f"Cannot parse layout content. Unexpected node of type {type(node)} received."
                )
    return Layout(children=cleaned_nodes, orientation=orientation)


def split(
    *nodes: _NodeLike, weight: Union[float, int] = 1, orientation: _Orientation = None
) -> Split:
    """
    Create a new split with the given weight, orientation and given nodes inside.
    """
    cleaned_nodes = []
    for node in nodes:
        if isinstance(node, (Split, Tab)):
            cleaned_nodes.append(node)
        elif isinstance(node, (_Widget, str)):
            cleaned_nodes.append(tab(node))
        elif isinstance(node, list):
            if all(isinstance(subnode, (_Widget, str)) for subnode in node):
                # All widgets inside, group them into one tab.
                cleaned_nodes.append(tab(*node))
            else:
                # Non-homogeneous content, wrap into a split.
                cleaned_nodes.append(split(*node))
        else:
            raise TypeError(
                f"Cannot parse layout content. Unexpected node of type {type(node)} received."
            )
    return Split(children=cleaned_nodes, weight=weight, orientation=orientation)


def tab(*widgets: _WidgetLike, weight: Union[float, int] = 1) -> Tab:
    """
    Create a new tab with the given weight and given widgets inside.
    """
    return Tab(
        children=[_Widget(type=x) if isinstance(x, str) else x for x in widgets],
        weight=weight,
    )


def parse(layout_: _LayoutLike) -> Layout:
    """
    Parse layout from a file, url, layout or given nodes.
    """

    if isinstance(layout_, Layout):
        return layout_

    if isinstance(layout_, str) and validators.url(layout_):
        try:
            resp = requests.get(str(layout_), timeout=20)
            return Layout(**resp.json())
        except (ValidationError, requests.JSONDecodeError) as e:
            raise InvalidLayout() from e

    if (isinstance(layout_, (os.PathLike, str))) and os.path.isfile(layout_):
        obj = Path(layout_).read_text()
        return Layout.model_validate_json(obj)

    layout_ = cast(_NodeLike, layout_)
    return layout(layout_)


def histogram(
    name: Optional[str] = None,
    column: Optional[str] = None,
    stack_by_column: Optional[str] = None,
    filter: bool = False,
) -> Histogram:
    """
    Add configured histogram to Spotlight layout.
    """

    return Histogram(
        name=name,
        config=HistogramConfig(
            column=column,
            stack_by_column=stack_by_column,
            filter=filter,
        ),
    )


def inspector(
    name: Optional[str] = None,
    lenses: Optional[Iterable[Lens]] = None,
    num_columns: _NumInspectorColumns = 4,
) -> Inspector:
    """
    Add an inspector widget with optionally preconfigured viewers (lenses).

    Example:
        >>> from renumics.spotlight import layout
        >>> from renumics.spotlight.layout import lenses
        >>> spotlight_layout = layout.layout(
        ...     layout.inspector(
        ...         "My Inspector",
        ...         [
        ...             lenses.scalar("bool"),
        ...             lenses.scalar("float"),
        ...             lenses.scalar("str"),
        ...             lenses.scalar("datetime"),
        ...             lenses.scalar("category"),
        ...             lenses.scalar("int"),
        ...             lenses.text("str", name="text"),
        ...             lenses.html("str", name="HTML (safe)"),
        ...             lenses.html("str", name="HTML", unsafe=True),
        ...             lenses.markdown("str", name="MD"),
        ...             lenses.array("embedding"),
        ...             lenses.array("window"),
        ...             lenses.array("array"),
        ...             lenses.sequences("sequence"),
        ...             lenses.sequences(["sequence1", "sequence2"], name="sequences"),
        ...             lenses.mesh("mesh"),
        ...             lenses.image("image"),
        ...             lenses.video("video"),
        ...             lenses.audio("audio"),
        ...             lenses.audio("audio", window_column="window", name="windowed audio"),
        ...             lenses.spectrogram("audio"),
        ...             lenses.spectrogram(
        ...                 "audio",
        ...                 window_column="window",
        ...                 name="windowed spectrogram",
        ...             ),
        ...         ],
        ...         num_columns=2,
        ...     )
        ... )
    """
    return Inspector(
        name=name,
        config=InspectorConfig(
            lenses=lenses if lenses is None else list(lenses), num_columns=num_columns
        ),
    )


def scatterplot(
    name: Optional[str] = None,
    x_column: Optional[str] = None,
    y_column: Optional[str] = None,
    color_by_column: Optional[str] = None,
    size_by_column: Optional[str] = None,
    filter: bool = False,
) -> Scatterplot:
    """
    Add configured scatter plot to Spotlight layout.
    """

    return Scatterplot(
        name=name,
        config=ScatterplotConfig(
            x_column=x_column,
            y_column=y_column,
            color_by_column=color_by_column,
            size_by_column=size_by_column,
            filter=filter,
        ),
    )


_UmapBalance = Literal["local", "normal", "global"]
_UMAP_BALANCE_TO_FLOAT: Dict[_UmapBalance, float] = {
    "local": 0.0,
    "normal": 0.5,
    "global": 1.0,
}


@overload
def similaritymap(
    name: Optional[str] = None,
    columns: Optional[List[str]] = None,
    reduction_method: Literal[None] = None,
    color_by_column: Optional[str] = None,
    size_by_column: Optional[str] = None,
    filter: bool = False,
) -> Similaritymap: ...


@overload
def similaritymap(
    name: Optional[str] = None,
    columns: Optional[List[str]] = None,
    reduction_method: Literal["umap"] = "umap",
    color_by_column: Optional[str] = None,
    size_by_column: Optional[str] = None,
    filter: bool = False,
    *,
    umap_metric: Optional[_UmapMetric] = None,
    umap_balance: Optional[_UmapBalance] = None,
) -> Similaritymap: ...


@overload
def similaritymap(
    name: Optional[str] = None,
    columns: Optional[List[str]] = None,
    reduction_method: Literal["pca"] = "pca",
    color_by_column: Optional[str] = None,
    size_by_column: Optional[str] = None,
    filter: bool = False,
    *,
    pca_normalization: Optional[_PCANormalization] = None,
) -> Similaritymap: ...


def similaritymap(
    name: Optional[str] = None,
    columns: Optional[List[str]] = None,
    reduction_method: Optional[_ReductionMethod] = None,
    color_by_column: Optional[str] = None,
    size_by_column: Optional[str] = None,
    filter: bool = False,
    *,
    umap_metric: Optional[_UmapMetric] = None,
    umap_balance: Optional[_UmapBalance] = None,
    pca_normalization: Optional[_PCANormalization] = None,
) -> Similaritymap:
    """
    Add configured similarity map to Spotlight layout.
    """

    umap_balance_float = None
    if reduction_method == "umap":
        pca_normalization = None
        if umap_balance is not None:
            umap_balance_float = _UMAP_BALANCE_TO_FLOAT[umap_balance]
    elif reduction_method == "pca":
        umap_metric = None
        umap_balance = None
    return Similaritymap(
        name=name,
        config=SimilaritymapConfig(
            columns=columns,
            reduction_method=reduction_method,
            color_by_column=color_by_column,
            size_by_column=size_by_column,
            filter=filter,
            umap_metric=umap_metric,
            umap_balance=umap_balance_float,
            pca_normalization=pca_normalization,
        ),
    )


_TableTab = Literal["all", "filtered", "selected"]
_TABLE_TAB_TO_TABLE_VIEW: Dict[_TableTab, _TableView] = {
    "all": "full",
    "filtered": "filtered",
    "selected": "selected",
}
_SortOrder = Literal["ascending", "descending"]
_SORT_ORDER_MAPPING: Dict[_SortOrder, str] = {
    "ascending": "ASC",
    "descending": "DESC",
}


def table(
    name: Optional[str] = None,
    active_view: _TableTab = "all",
    visible_columns: Optional[List[str]] = None,
    sort_by_columns: Optional[List[Tuple[str, _SortOrder]]] = None,
    order_by_relevance: bool = False,
) -> Table:
    """
    Add configured table to Spotlight layout.
    """
    return Table(
        name=name,
        config=TableConfig(
            active_view=_TABLE_TAB_TO_TABLE_VIEW[active_view],
            visible_columns=visible_columns,
            sort_by_columns=(
                None
                if sort_by_columns is None
                else [
                    [column, _SORT_ORDER_MAPPING[order]]
                    for column, order in sort_by_columns
                ]
            ),
            order_by_relevance=order_by_relevance,
        ),
    )


def issues(name: Optional[str] = None) -> Issues:
    """
    Add a widget displaying data issues.
    """

    return Issues(name=name)


def wordcloud(
    name: Optional[str] = None,
    column: Optional[str] = None,
    min_word_length: Optional[int] = None,
    stop_words: Optional[Iterable[str]] = None,
    scaling: Optional[_WordCloudScaling] = None,
    max_word_count: Optional[int] = None,
    filter: Optional[bool] = None,
) -> WordCloud:
    """
    Add configured confusion matrix to Spotlight layout.
    """
    if min_word_length is not None and min_word_length < 1:
        raise ValueError(
            f"`min_word_length` argument should be positive, but value "
            f"{min_word_length} received."
        )
    if max_word_count is not None and max_word_count < 1:
        raise ValueError(
            f"`max_word_count` argument should be positive, but value "
            f"{max_word_count} received."
        )
    return WordCloud(
        name=name,
        config=WordCloudConfig(
            column=column,
            min_word_length=min_word_length,
            stop_words=None if stop_words is None else list(stop_words),
            scaling=scaling,
            max_word_count=max_word_count,
            filter=filter,
        ),
    )


def confusion_matrix(
    name: Optional[str] = None,
    x_column: Optional[str] = None,
    y_column: Optional[str] = None,
) -> ConfusionMatrix:
    """
    Add configured confusion matrix to Spotlight layout.
    """
    return ConfusionMatrix(
        name=name,
        config=ConfusionMatrixConfig(x_column=x_column, y_column=y_column),
    )


def metric(
    name: Optional[str] = None,
    metric: Optional[str] = None,
    columns: Optional[Union[str, Iterable[Optional[str]]]] = None,
) -> MetricWidget:
    """
    Add configured metric widget to Spotlight layout.
    """
    metric_columns: List[Optional[str]] = []
    if isinstance(columns, str):
        metric_columns.append(columns)
    elif columns is not None:
        metric_columns.extend(columns)
    return MetricWidget(
        name=name, config=MetricWidgetConfig(metric=metric, columns=metric_columns)
    )
