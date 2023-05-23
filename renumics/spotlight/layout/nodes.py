"""
Implementation of layout models and interfaces for layout creation.
"""

from typing import List, Optional, Union

from pydantic import BaseModel, Extra, Field  # pylint: disable=no-name-in-module
from typing_extensions import Literal

from .widgets import (
    AudioOverview,
    Histogram,
    Inspector,
    Scatterplot,
    ScatterplotGL,
    Similaritymap,
    Table,
)


Orientation = Optional[Literal["horizontal", "vertical"]]


class Tab(BaseModel, extra=Extra.forbid):
    """
    Tab with widgets.
    """

    # pylint: disable=too-few-public-methods
    children: List[
        Union[
            AudioOverview,
            Histogram,
            Inspector,
            Scatterplot,
            ScatterplotGL,
            Similaritymap,
            Table,
        ]
    ] = Field(default_factory=list)
    weight: Union[float, int] = 1
    kind: Literal["tab"] = "tab"


class Split(BaseModel, extra=Extra.forbid):
    """
    Horisontal or vertical split.
    Orientation `None` flips the previous orientation.
    """

    # pylint: disable=too-few-public-methods
    children: List[Union["Split", Tab]] = Field(default_factory=list)
    orientation: Orientation = None
    weight: Union[float, int] = 1
    kind: Literal["split"] = "split"


class Layout(BaseModel, extra=Extra.forbid):
    """
    Root node of layout.
    """

    # pylint: disable=too-few-public-methods
    children: List[Union[Split, Tab]] = Field(default_factory=list)
    orientation: Orientation = None


Split.update_forward_refs()
