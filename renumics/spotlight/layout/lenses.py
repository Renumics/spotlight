"""
Viewers (lenses) for Spotlight inspector widget.

For usage examples, see `renumics.spotlight.layout.inspector`.
"""

import uuid
from typing import List, Optional, Union

from pydantic import BaseModel, Field
from typing_extensions import Literal


class Lens(BaseModel, populate_by_name=True):
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
    settings: Optional[dict] = None
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), alias="key")


def lens(
    internal_type: str,
    columns: Union[str, List[str]],
    name: Optional[str] = None,
    settings: Optional[dict] = None,
) -> Lens:
    """
    Add a viewer to Spotlight inspector widget.

    `internal_type` should be set exactly as expected if the frontend. For
    supported lens types and respective column types, see `Lens` class.

    Prefer to use explicit lens functions defined below.
    """
    return Lens(
        type=internal_type,
        columns=[columns] if isinstance(columns, str) else columns,
        name=name,
        settings=settings,
    )


def scalar(column: str, name: Optional[str] = None) -> Lens:
    """
    Add scalar value viewer to Spotlight inspector widget.

    Supports a single column of type `bool`, `int`, `float`, `str`,
    `datetime.datetime` or `spotlight.Category`.
    """
    return Lens(type="ScalarView", columns=[column], name=name)


def text(column: str, name: Optional[str] = None) -> Lens:
    """
    Add text viewer to Spotlight inspector widget.

    Supports a single column of type `str`.
    """
    return Lens(type="TextLens", columns=[column], name=name)


def html(column: str, name: Optional[str] = None, unsafe: bool = False) -> Lens:
    """
    Add HTML viewer to Spotlight inspector widget.

    Supports a single column of type `str`.
    """
    if unsafe:
        return Lens(type="HtmlLens", columns=[column], name=name)
    return Lens(type="SafeHtmlLens", columns=[column], name=name)


def markdown(column: str, name: Optional[str] = None) -> Lens:
    """
    Add markdown viewer to Spotlight inspector widget.

    Supports a single column of type `str`.
    """
    return Lens(type="MarkdownLens", columns=[column], name=name)


def array(column: str, name: Optional[str] = None) -> Lens:
    """
    Add array viewer to Spotlight inspector widget.

    Supports a single column of type `np.ndarray`, `spotlight.Embedding` or
    `spotlight.Window`.
    """
    return Lens(type="ArrayLens", columns=[column], name=name)


def sequences(
    columns: Union[str, List[str]],
    name: Optional[str] = None,
    *,
    multiple_y_axes: bool = False,
) -> Lens:
    """
    Add sequence viewer to Spotlight inspector widget.

    Supports one or multiple columns of type `spotlight.Sequence1D`.
    """
    return Lens(
        type="SequenceView",
        columns=[columns] if isinstance(columns, str) else columns,
        name=name,
        settings={"yAxisMultiple": multiple_y_axes},
    )


MeshAnimation = Literal["loop", "oscillate"]


def mesh(
    column: str,
    name: Optional[str] = None,
    *,
    color_attribute: Optional[str] = None,
    wireframe: bool = False,
    transparency: float = 0,
    animation: MeshAnimation = "loop",
    animation_scale: float = 1.0,
    synchronize: bool = True,
) -> Lens:
    """
    Add mesh viewer to Spotlight inspector widget.

    Supports a single column of type `spotlight.Mesh`.
    """
    settings: dict = {
        "isSynchronized": synchronize,
        "showWireframe": wireframe,
        "transparency": transparency,
        "morphStyle": animation,
        "morphScale": animation_scale,
    }
    if color_attribute is not None:
        settings["colorAttribute"] = color_attribute
    return Lens(
        type="MeshView",
        columns=[column],
        name=name,
        settings=settings,
    )


def image(column: str, name: Optional[str] = None) -> Lens:
    """
    Add image viewer to Spotlight inspector widget.

    Supports a single column of type `spotlight.Image`.
    """
    return Lens(type="ImageView", columns=[column], name=name)


def video(column: str, name: Optional[str] = None) -> Lens:
    """
    Add video viewer to Spotlight inspector widget.

    Supports a single column of type `spotlight.Video`.
    """
    return Lens(type="VideoView", columns=[column], name=name)


def audio(
    column: str,
    window_column: Optional[str] = None,
    name: Optional[str] = None,
    *,
    repeat: bool = False,
    autoplay: bool = False,
) -> Lens:
    """
    Add audio viewer to Spotlight inspector widget.

    Supports a single column of type `spotlight.Audio` with optional second
    column of type `spotlight.Window`.
    """
    return Lens(
        type="AudioView",
        columns=[column] if window_column is None else [column, window_column],
        name=name,
        settings={"repeat": repeat, "autoplay": autoplay},
    )


SpectrogramFrequencyScale = Literal["linear", "logarithmic"]
SpectrogramAmplitudeScale = Literal["decibel", "linear"]


def spectrogram(
    column: str,
    window_column: Optional[str] = None,
    name: Optional[str] = None,
    *,
    frequency_scale: SpectrogramFrequencyScale = "linear",
    amplitude_scale: SpectrogramAmplitudeScale = "decibel",
) -> Lens:
    """
    Add audio spectrogram viewer to Spotlight inspector widget.

    Supports a single column of type `spotlight.Audio` with optional second
    column of type `spotlight.Window`.
    """
    return Lens(
        type="SpectrogramView",
        columns=[column] if window_column is None else [column, window_column],
        name=name,
        settings={"freqScale": frequency_scale, "ampScale": amplitude_scale},
    )


def rouge_score(column: str, reference_column: str, name: Optional[str] = None) -> Lens:
    """
    Add ROUGE score viewer to Spotlight inspector widget.

    Supports a pair of string columns.
    """
    return Lens(type="RougeScore", columns=[column, reference_column], name=name)
