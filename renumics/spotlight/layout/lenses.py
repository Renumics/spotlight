"""
Viewers (lenses) for Spotlight inspector widget.

For usage examples, see `renumics.spotlight.layout.inspector`.
"""

import uuid
from typing import List, Optional, Union

from pydantic import BaseModel, Field


class Lens(BaseModel, allow_population_by_field_name=True):
    """
    Inspector lens configuration model.

    Following combinations of lens types and column types are supported by
    default (but can be further extended):
        "ScalarView": single column of type `bool`, `int`, `float`, `str`,
            `datetime.datetime` or `spotlight.Category`
        "TextLens": single column of type `str`
        "HtmlLens": single column of type `str`
        "SafeHtmlLens": single column of type `str`
        "MarkdownLens": single column of type `str`
        "ArrayLens": single column of type `np.ndarray`,
            `spotlight.Embedding` or `spotlight.Window`
        "SequenceView": single or multiple columns of type `spotlight.Sequence1D`
        "MeshView": single column of type `spotlight.Mesh`
        "ImageView": single column of type `spotlight.Image`
        "VideoView": single column of type `spotlight.Video`
        "AudioView": single column of type `spotlight.Audio`, optional
            single column of type `spotlight.Window`
        "SpectrogramView": single column of type `spotlight.Audio`, optional
            single column of type `spotlight.Window`
    """

    type: str = Field(..., alias="view")
    columns: List[str] = Field(..., alias="columns")
    name: Optional[str] = Field(None, alias="name")
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), alias="key")


def lens(
    internal_type: str, columns: Union[str, List[str]], name: Optional[str] = None
) -> Lens:
    """
    Add a viewer to Spotlight inspector widget.

    `internal_type` should be set exactly as expected if the frontend. For
    supported lens types and respective column types, see `Lens` class.

    Prefer to use explicit lens functions defined below.
    """
    return Lens(
        type=internal_type,  # type: ignore
        columns=[columns] if isinstance(columns, str) else columns,
        name=name,
    )


def scalar(column: str, name: Optional[str] = None) -> Lens:
    """
    Add scalar value viewer to Spotlight inspector widget.

    Supports a single column of type `bool`, `int`, `float`, `str`,
    `datetime.datetime` or `spotlight.Category`.
    """
    return Lens(type="ScalarView", columns=[column], name=name)  # type: ignore


def text(column: str, name: Optional[str] = None) -> Lens:
    """
    Add text viewer to Spotlight inspector widget.

    Supports a single column of type `str`.
    """
    return Lens(type="TextLens", columns=[column], name=name)  # type: ignore


def html(column: str, name: Optional[str] = None, unsafe: bool = False) -> Lens:
    """
    Add HTML viewer to Spotlight inspector widget.

    Supports a single column of type `str`.
    """
    if unsafe:
        return Lens(type="HtmlLens", columns=[column], name=name)  # type: ignore
    return Lens(type="SafeHtmlLens", columns=[column], name=name)  # type: ignore


def markdown(column: str, name: Optional[str] = None) -> Lens:
    """
    Add markdown viewer to Spotlight inspector widget.

    Supports a single column of type `str`.
    """
    return Lens(type="MarkdownLens", columns=[column], name=name)  # type: ignore


def array(column: str, name: Optional[str] = None) -> Lens:
    """
    Add array viewer to Spotlight inspector widget.

    Supports a single column of type `np.ndarray`, `spotlight.Embedding` or
    `spotlight.Window`.
    """
    return Lens(type="ArrayLens", columns=[column], name=name)  # type: ignore


def sequences(columns: Union[str, List[str]], name: Optional[str] = None) -> Lens:
    """
    Add sequence viewer to Spotlight inspector widget.

    Supports one or multiple columns of type `spotlight.Sequence1D`.
    """
    return Lens(
        type="SequenceView",  # type: ignore
        columns=[columns] if isinstance(columns, str) else columns,
        name=name,
    )


def mesh(column: str, name: Optional[str] = None) -> Lens:
    """
    Add mesh viewer to Spotlight inspector widget.

    Supports a single column of type `spotlight.Mesh`.
    """
    return Lens(type="MeshView", columns=[column], name=name)  # type: ignore


def image(column: str, name: Optional[str] = None) -> Lens:
    """
    Add image viewer to Spotlight inspector widget.

    Supports a single column of type `spotlight.Image`.
    """
    return Lens(type="ImageView", columns=[column], name=name)  # type: ignore


def video(column: str, name: Optional[str] = None) -> Lens:
    """
    Add video viewer to Spotlight inspector widget.

    Supports a single column of type `spotlight.Video`.
    """
    return Lens(type="VideoView", columns=[column], name=name)  # type: ignore


def audio(
    column: str, window_column: Optional[str] = None, name: Optional[str] = None
) -> Lens:
    """
    Add audio viewer to Spotlight inspector widget.

    Supports a single column of type `spotlight.Audio` with optional second
    column of type `spotlight.Window`.
    """
    return Lens(
        type="AudioView",  # type: ignore
        columns=[column] if window_column is None else [column, window_column],
        name=name,
    )


def spectrogram(
    column: str, window_column: Optional[str] = None, name: Optional[str] = None
) -> Lens:
    """
    Add audio spectrogram viewer to Spotlight inspector widget.

    Supports a single column of type `spotlight.Audio` with optional second
    column of type `spotlight.Window`.
    """
    return Lens(
        type="SpectrogramView",  # type: ignore
        columns=[column] if window_column is None else [column, window_column],
        name=name,
    )
