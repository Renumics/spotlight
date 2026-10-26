"""
This module provides type annotation for Spotlight dataset.
"""

from collections.abc import Sequence
from datetime import datetime
from typing import TypeAlias

import numpy as np
import trimesh

from renumics.spotlight.media import (
    Array1dLike,
    Audio,
    Embedding,
    Image,
    ImageLike,
    Mesh,
    Sequence1D,
    Video,
)
from renumics.spotlight.typing import BoolType, IntType, NumberType, PathOrUrlType

OutputType: TypeAlias = (
    bool
    | int
    | float
    | str
    | datetime
    | np.ndarray
    | Sequence1D
    | Audio
    | Image
    | Mesh
    | Video
)
# Only pure types.
SimpleOutputType: TypeAlias = bool | int | float | str | datetime | Embedding
RefOutputType: TypeAlias = (
    np.ndarray | Embedding | Mesh | Sequence1D | Image | Audio | Video
)
FileBasedOutputType: TypeAlias = Audio | Image | Mesh | Video
ExternalOutputType: TypeAlias = FileBasedOutputType
ArrayBasedOutputType: TypeAlias = Embedding | Image | Sequence1D
# Pure types, compatible types and `None`.
BoolColumnInputType: TypeAlias = BoolType | None
IntColumnInputType: TypeAlias = IntType | None
FloatColumnInputType: TypeAlias = float | np.floating | None
StringColumnInputType: TypeAlias = str | None
DatetimeColumnInputType: TypeAlias = datetime | np.datetime64 | None
CategoricalColumnInputType: TypeAlias = str | None
WindowColumnInputType: TypeAlias = (
    list[NumberType] | tuple[NumberType, NumberType] | np.ndarray | None
)
BoundingBoxColumnInputType: TypeAlias = (
    list[NumberType]
    | tuple[NumberType, NumberType, NumberType, NumberType]
    | np.ndarray
    | None
)
ArrayColumnInputType: TypeAlias = np.ndarray | Sequence | None
EmbeddingColumnInputType: TypeAlias = Embedding | Array1dLike | None
AudioColumnInputType: TypeAlias = Audio | PathOrUrlType | bytes | None
ImageColumnInputType: TypeAlias = Image | ImageLike | PathOrUrlType | bytes | None
MeshColumnInputType: TypeAlias = Mesh | trimesh.Trimesh | PathOrUrlType | None
Sequence1DColumnInputType: TypeAlias = Sequence1D | Array1dLike | None
VideoColumnInputType: TypeAlias = Video | PathOrUrlType | bytes | None
# Aggregated input types.
SimpleColumnInputType: TypeAlias = (
    BoolColumnInputType
    | IntColumnInputType
    | FloatColumnInputType
    | StringColumnInputType
    | DatetimeColumnInputType
    | CategoricalColumnInputType
    | WindowColumnInputType
    | BoundingBoxColumnInputType
    | EmbeddingColumnInputType
)
RefColumnInputType: TypeAlias = (
    ArrayColumnInputType
    | EmbeddingColumnInputType
    | Sequence1DColumnInputType
    | AudioColumnInputType
    | ImageColumnInputType
    | MeshColumnInputType
    | VideoColumnInputType
)
ColumnInputType: TypeAlias = SimpleColumnInputType | RefColumnInputType
FileColumnInputType: TypeAlias = (
    AudioColumnInputType
    | ImageColumnInputType
    | MeshColumnInputType
    | VideoColumnInputType
)
ExternalColumnInputType: TypeAlias = PathOrUrlType | None
