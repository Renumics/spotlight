"""
This module allows user customize layout to start Spotlight from a python script/notebook.

A Spotlight layout consists of multiple widgets, grouped into tabs and splits.
"""
import os
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Union, cast, overload

from typing_extensions import Literal, get_args

from .nodes import (
    Layout as _Layout,
    Orientation as _Orientation,
    Split as _Split,
    Tab as _Tab,
)
from .widgets import (
    AudioOverview as _AudioOverview,
    AudioOverviewConfig as _AudioOverviewConfig,
    Histogram as _Histogram,
    HistogramConfig as _HistogramConfig,
    Inspector as _Inspector,
    InspectorConfig as _InspectorConfig,
    PCANormalization as _PCANormalization,
    ReductionMethod as _ReductionMethod,
    Scatterplot as _Scatterplot,
    ScatterplotGL as _ScatterplotGL,
    Similaritymap as _Similaritymap,
    SimilaritymapConfig as _SimilaritymapConfig,
    Table as _Table,
    TableConfig as _TableConfig,
    TableView as _TableView,
    UmapMetric as _UmapMetric,
    Widget as _Widget,
    WidgetName as _WidgetName,
)


_WidgetLike = Union[_Widget, _WidgetName]
_NodeLike = Union[_Split, _Tab, _WidgetLike, List]
_LayoutLike = Union[str, os.PathLike, _Layout, _NodeLike]


def _clean_nodes(nodes: Iterable[_NodeLike]) -> List[Union[_Split, _Tab]]:
    """
    Wrap standalone widgets into tabs with a single widget inside and
    lists of widgets into common tabs. Pass splits and tabs as is.
    """
    if all(isinstance(node, (_Widget, str)) for node in nodes):
        nodes = cast(Iterable[_WidgetLike], nodes)
        return [tab(*nodes)]
    cleaned_nodes = []
    for node in nodes:
        if isinstance(node, (_Split, _Tab)):
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
    return cleaned_nodes


def layout(*nodes: _NodeLike, orientation: _Orientation = None) -> _Layout:
    """
    Create a new layout with the given orientation and given nodes inside.
    """
    return _Layout(children=_clean_nodes(nodes), orientation=orientation)


def split(
    *nodes: _NodeLike, weight: Union[float, int] = 1, orientation: _Orientation = None
) -> _Split:
    """
    Create a new split with the given weight, orientation and given nodes inside.
    """
    return _Split(children=_clean_nodes(nodes), weight=weight, orientation=orientation)


def tab(*widgets: _WidgetLike, weight: Union[float, int] = 1) -> _Tab:
    """
    Create a new tab with the given weight and given widgets inside.
    """
    return _Tab(
        children=[_Widget(type=x) if isinstance(x, str) else x for x in widgets],
        weight=weight,
    )


def parse(layout_: _LayoutLike) -> _Layout:
    """
    Parse layout from a file, layout or given nodes.
    """
    if isinstance(layout_, _Layout):
        return layout_
    if (
        isinstance(layout_, os.PathLike)
        or isinstance(layout_, str)
        and layout_ not in get_args(_WidgetName)
    ):
        if os.path.isfile(layout_):
            return _Layout.parse_file(Path(layout_))
        raise FileNotFoundError(f"Path {layout_} does not exist or is not a file.")
    layout_ = cast(_NodeLike, layout_)
    return layout(layout_)


def audio_overview(
    name: Optional[str] = None,
    audio_column: Optional[str] = None,
    window_column: Optional[str] = None,
) -> _AudioOverview:
    """
    Add configured audio overview to Spotlight layout.
    """
    return _AudioOverview(
        name=name,
        config=_AudioOverviewConfig(
            audio_column=audio_column, window_column=window_column
        ),
    )


def histogram(
    name: Optional[str] = None,
    column: Optional[str] = None,
    stack_by_column: Optional[str] = None,
    filter: bool = False,
) -> _Histogram:
    """
    Add configured histogram to Spotlight layout.
    """
    # pylint: disable=redefined-builtin
    return _Histogram(
        name=name,
        config=_HistogramConfig(
            column=column,
            stack_by_column=stack_by_column,
            filter=filter,
        ),
    )


def inspector(
    name: Optional[str] = None, num_columns: Literal[1, 2, 4, 6, 8] = 4
) -> _Inspector:
    """
    Add (unconfigured) inspector widget to Spotlight layout.
    """
    return _Inspector(name=name, config=_InspectorConfig(num_columns=num_columns))


def scatterplot(
    name: Optional[str] = None,
    x_column: Optional[str] = None,
    y_column: Optional[str] = None,
    color_by_column: Optional[str] = None,
    size_by_column: Optional[str] = None,
    filter: bool = False,
    use_gl: bool = False,
) -> Union[_Scatterplot, _ScatterplotGL]:
    """
    Add configured scatter plot to Spotlight layout.
    """
    # pylint: disable=too-many-arguments,redefined-builtin
    config = {
        "x_column": x_column,
        "y_column": y_column,
        "color_by_column": color_by_column,
        "size_by_column": size_by_column,
        "filter": filter,
    }
    if use_gl:
        return _ScatterplotGL(name=name, config=config)
    return _Scatterplot(name=name, config=config)


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
) -> _Similaritymap:
    # pylint: disable=too-many-arguments,redefined-builtin
    ...


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
) -> _Similaritymap:
    # pylint: disable=too-many-arguments,redefined-builtin
    ...


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
) -> _Similaritymap:
    # pylint: disable=too-many-arguments,redefined-builtin
    ...


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
) -> _Similaritymap:
    """
    Add configured similarity map to Spotlight layout.
    """
    # pylint: disable=too-many-arguments,redefined-builtin
    umap_balance_float = None
    if reduction_method == "umap":
        pca_normalization = None
        if umap_balance is not None:
            umap_balance_float = _UMAP_BALANCE_TO_FLOAT[umap_balance]
    elif reduction_method == "pca":
        umap_metric = None
        umap_balance = None
    return _Similaritymap(
        name=name,
        config=_SimilaritymapConfig(
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


def table(
    name: Optional[str] = None,
    active_view: _TableTab = "all",
    visible_columns: Optional[List[str]] = None,
    sort_by_columns: Optional[List[str]] = None,
    order_by_relevance: bool = False,
) -> _Table:
    """
    Add configured table to Spotlight layout.
    """
    return _Table(
        name=name,
        config=_TableConfig(
            active_view=_TABLE_TAB_TO_TABLE_VIEW[active_view],
            visible_columns=visible_columns,
            sort_by_columns=sort_by_columns,
            order_by_relevance=order_by_relevance,
        ),
    )
