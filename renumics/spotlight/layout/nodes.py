"""
Implementation of layout models and interfaces for layout creation.
"""

from typing import Any, List, Optional, Union

from pydantic import BaseModel, Field, SerializeAsAny, field_validator
from typing_extensions import Literal

from .widgets import Widget

Orientation = Optional[Literal["horizontal", "vertical"]]


def _validate_widget(value: Any) -> Widget:
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
                if subclass.model_fields["type"].default == widget_type:
                    return subclass(**value)
    return value


class Tab(BaseModel, extra="forbid"):
    """
    Tab with widgets.
    """

    children: List[SerializeAsAny[Widget]] = Field(default_factory=list)
    weight: Union[float, int] = 1
    kind: Literal["tab"] = "tab"

    @field_validator("children", mode="before")
    @classmethod
    def validate_children(cls, value: Any) -> Any:
        """
        Narrow the tabs children.
        """
        if isinstance(value, list):
            return [_validate_widget(x) for x in value]
        return value


class Split(BaseModel, extra="forbid"):
    """
    Horisontal or vertical split.
    Orientation `None` flips the previous orientation.
    """

    children: List[Union["Split", Tab]] = Field(default_factory=list)
    orientation: Orientation = None
    weight: Union[float, int] = 1
    kind: Literal["split"] = "split"


class Layout(BaseModel, extra="forbid"):
    """
    Root node of layout.
    """

    children: List[Union[Split, Tab]] = Field(default_factory=list)
    orientation: Orientation = None


Split.model_rebuild()
