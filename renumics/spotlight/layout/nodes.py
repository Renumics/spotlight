"""
Implementation of layout models and interfaces for layout creation.
"""

from typing import Any, List, Optional, Union

from pydantic import (
    BaseModel,
    Extra,
    Field,
    validator,
)
from typing_extensions import Literal

from .widgets import Widget


Orientation = Optional[Literal["horizontal", "vertical"]]


class Tab(BaseModel, extra=Extra.forbid):
    """
    Tab with widgets.
    """

    children: List[Widget] = Field(default_factory=list)
    weight: Union[float, int] = 1
    kind: Literal["tab"] = "tab"

    @validator("children", pre=True, each_item=True)
    @classmethod
    def validate_widget(cls, value: Any) -> Widget:
        """
        Narrow the widget object's class based on its type.
        """
        if isinstance(value, dict):
            try:
                widget_type = value["type"]
            except KeyError:
                pass
            else:
                for subclass in Widget.__subclasses__():
                    if subclass.__fields__["type"].default == widget_type:
                        return subclass(**value)
        return value


class Split(BaseModel, extra=Extra.forbid):
    """
    Horisontal or vertical split.
    Orientation `None` flips the previous orientation.
    """

    children: List[Union["Split", Tab]] = Field(default_factory=list)
    orientation: Orientation = None
    weight: Union[float, int] = 1
    kind: Literal["split"] = "split"


class Layout(BaseModel, extra=Extra.forbid):
    """
    Root node of layout.
    """

    children: List[Union[Split, Tab]] = Field(default_factory=list)
    orientation: Orientation = None


Split.update_forward_refs()
