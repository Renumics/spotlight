"""
This module provides type annotation for Spotlight dataset.
"""

from datetime import datetime
from typing import (
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

import numpy as np
import trimesh
from typing_extensions import get_args

from renumics.spotlight.typing import BoolType, IntType, NumberType, PathOrURLType
from renumics.spotlight.dtypes import (
    Array1DLike,
    Embedding,
    Mesh,
    Sequence1D,
    Image,
    ImageLike,
    Audio,
    Category,
    Video,
    Window,
)
from renumics.spotlight.dtypes.typing import FileBasedColumnType, NAME_BY_COLUMN_TYPE


# Only pure types.
SimpleColumnType = Union[bool, int, float, str, datetime, Category, Window, Embedding]
RefColumnType = Union[np.ndarray, Embedding, Mesh, Sequence1D, Image, Audio, Video]
ExternalColumnType = FileBasedColumnType
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
ArrayColumnInputType = Optional[Union[np.ndarray, Sequence]]
EmbeddingColumnInputType = Optional[Union[Embedding, Array1DLike]]
AudioColumnInputType = Optional[Union[Audio, PathOrURLType]]
ImageColumnInputType = Optional[Union[Image, ImageLike, PathOrURLType]]
MeshColumnInputType = Optional[Union[Mesh, trimesh.Trimesh, PathOrURLType]]
Sequence1DColumnInputType = Optional[Union[Sequence1D, Array1DLike]]
VideoColumnInputType = Optional[Union[Video, PathOrURLType]]
# Aggregated input types.
SimpleColumnInputType = Union[
    BoolColumnInputType,
    IntColumnInputType,
    FloatColumnInputType,
    StringColumnInputType,
    DatetimeColumnInputType,
    CategoricalColumnInputType,
    WindowColumnInputType,
    EmbeddingColumnInputType,
]
RefColumnInputType = Union[
    ArrayColumnInputType,
    EmbeddingColumnInputType,
    AudioColumnInputType,
    ImageColumnInputType,
    MeshColumnInputType,
    Sequence1DColumnInputType,
    VideoColumnInputType,
]
ColumnInputType = Union[SimpleColumnInputType, RefColumnInputType]
ExternalColumnInputType = Optional[PathOrURLType]

REF_COLUMN_TYPE_NAMES = [
    NAME_BY_COLUMN_TYPE[column_type] for column_type in get_args(RefColumnType)
]
SIMPLE_COLUMN_TYPE_NAMES = [
    NAME_BY_COLUMN_TYPE[column_type] for column_type in get_args(SimpleColumnType)
]
