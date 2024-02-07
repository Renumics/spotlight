"""
This module provides type annotation for Spotlight dataset.
"""

from datetime import datetime
from typing import List, Optional, Sequence, Tuple, Union

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

OutputType = Union[
    bool, int, float, str, datetime, np.ndarray, Sequence1D, Audio, Image, Mesh, Video
]
# Only pure types.
SimpleOutputType = Union[bool, int, float, str, datetime, Embedding]
RefOutputType = Union[np.ndarray, Embedding, Mesh, Sequence1D, Image, Audio, Video]
FileBasedOutputType = Union[Audio, Image, Mesh, Video]
ExternalOutputType = FileBasedOutputType
ArrayBasedOutputType = Union[Embedding, Image, Sequence1D]
# Pure types, compatible types and `None`.
BoolColumnInputType = Optional[BoolType]
IntColumnInputType = Optional[IntType]
FloatColumnInputType = Optional[Union[float, np.floating]]
StringColumnInputType = Optional[str]
DatetimeColumnInputType = Optional[Union[datetime, np.datetime64]]
CategoricalColumnInputType = Optional[str]
WindowColumnInputType = Optional[
    Union[List[NumberType], Tuple[NumberType, NumberType], np.ndarray]
]
BoundingBoxColumnInputType = Optional[
    Union[
        List[NumberType],
        Tuple[NumberType, NumberType, NumberType, NumberType],
        np.ndarray,
    ]
]
ArrayColumnInputType = Optional[Union[np.ndarray, Sequence]]
EmbeddingColumnInputType = Optional[Union[Embedding, Array1dLike]]
AudioColumnInputType = Optional[Union[Audio, PathOrUrlType, bytes]]
ImageColumnInputType = Optional[Union[Image, ImageLike, PathOrUrlType, bytes]]
MeshColumnInputType = Optional[Union[Mesh, trimesh.Trimesh, PathOrUrlType]]
Sequence1DColumnInputType = Optional[Union[Sequence1D, Array1dLike]]
VideoColumnInputType = Optional[Union[Video, PathOrUrlType, bytes]]
# Aggregated input types.
SimpleColumnInputType = Union[
    BoolColumnInputType,
    IntColumnInputType,
    FloatColumnInputType,
    StringColumnInputType,
    DatetimeColumnInputType,
    CategoricalColumnInputType,
    WindowColumnInputType,
    BoundingBoxColumnInputType,
    EmbeddingColumnInputType,
]
RefColumnInputType = Union[
    ArrayColumnInputType,
    EmbeddingColumnInputType,
    Sequence1DColumnInputType,
    AudioColumnInputType,
    ImageColumnInputType,
    MeshColumnInputType,
    VideoColumnInputType,
]
ColumnInputType = Union[SimpleColumnInputType, RefColumnInputType]
FileColumnInputType = Union[
    AudioColumnInputType,
    ImageColumnInputType,
    MeshColumnInputType,
    VideoColumnInputType,
]
ExternalColumnInputType = Optional[PathOrUrlType]
