"""
Implementation of layout models and interfaces for layout creation.
"""

from typing import Any, Literal, TypeAlias

from pydantic import BaseModel, Field, SerializeAsAny, field_validator

from .widgets import Widget

Orientation: TypeAlias = Literal["horizontal", "vertical"] | None


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

    children: list[SerializeAsAny[Widget]] = Field(default_factory=list)
    weight: float | int = 1
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

    children: "list[Split | Tab]" = Field(default_factory=list)
    orientation: Orientation = None
    weight: float | int = 1
    kind: Literal["split"] = "split"


class Layout(BaseModel, extra="forbid"):
    """
    Root node of layout.
    """

    children: list[Split | Tab] = Field(default_factory=list)
    orientation: Orientation = None


Split.model_rebuild()
