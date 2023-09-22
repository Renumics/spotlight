from datetime import datetime
from typing import Any, Dict, Iterable, Optional, Tuple, Union

import numpy as np
from typing_extensions import TypeGuard

from .legacy import Audio, Category, Embedding, Image, Mesh, Sequence1D, Video, Window


__all__ = [
    "CategoryDType",
    "Sequence1DDType",
    "bool_dtype",
    "int_dtype",
    "float_dtype",
    "str_dtype",
    "datetime_dtype",
    "category_dtype",
    "window_dtype",
    "embedding_dtype",
    "array_dtype",
    "image_dtype",
    "audio_dtype",
    "mesh_dtype",
    "sequence_1d_dtype",
    "video_dtype",
]


class DType:
    _name: str

    def __init__(self, name: str):
        self._name = name

    def __str__(self) -> str:
        return self.name

    @property
    def name(self) -> str:
        return self._name


class CategoryDType(DType):
    """
    Categorical dtype with predefined categories.
    """

    _categories: Optional[Dict[str, int]]
    _inverted_categories: Optional[Dict[int, str]]

    def __init__(
        self, categories: Optional[Union[Iterable[str], Dict[str, int]]] = None
    ):
        super().__init__("Category")
        if isinstance(categories, dict) or categories is None:
            self._categories = categories
        else:
            self._categories = {
                category: code for code, category in enumerate(categories)
            }

        if self._categories is None:
            self._inverted_categories = None
        else:
            self._inverted_categories = {
                code: category for category, code in self._categories.items()
            }
            # invert again to remove duplicate codes
            self._categories = {
                category: code for code, category in self._inverted_categories.items()
            }

    @property
    def categories(self) -> Optional[Dict[str, int]]:
        return self._categories

    @property
    def inverted_categories(self) -> Optional[Dict[int, str]]:
        return self._inverted_categories


class ArrayDType(DType):
    """
    Array dtype with optional shape.
    """

    shape: Optional[Tuple[Optional[int], ...]]

    def __init__(self, shape: Optional[Tuple[Optional[int], ...]] = None):
        super().__init__("array")
        self.shape = shape

    @property
    def ndim(self) -> int:
        if self.shape is None:
            return 0
        return len(self.shape)


class EmbeddingDType(DType):
    """
    Embedding dtype with optional length.
    """

    length: Optional[int]

    def __init__(self, length: Optional[int] = None):
        super().__init__("Embedding")
        if length is not None and length < 0:
            raise ValueError(f"Length must be non-negative, but {length} received.")
        self.length = length


class Sequence1DDType(DType):
    """
    1D-sequence dtype with predefined axis labels.
    """

    x_label: str
    y_label: str

    def __init__(self, x_label: str = "x", y_label: str = "y"):
        super().__init__("Sequence1D")
        self.x_label = x_label
        self.y_label = y_label


ALIASES: Dict[Any, DType] = {}


def register_dtype(dtype: DType, aliases: Optional[list] = None) -> None:
    assert dtype.name.lower() not in ALIASES
    ALIASES[dtype.name.lower()] = dtype

    if aliases is not None:
        for alias in aliases:
            assert alias not in ALIASES
            ALIASES[alias] = dtype


bool_dtype = DType("bool")
"""Bool dtype"""
register_dtype(bool_dtype, [bool])
int_dtype = DType("int")
"""Integer dtype"""
register_dtype(int_dtype, [int])
float_dtype = DType("float")
"""Float dtype"""
register_dtype(float_dtype, [float])
bytes_dtype = DType("bytes")
"""Bytes dtype"""
register_dtype(bytes_dtype, [bytes])
str_dtype = DType("str")
"""String dtype"""
register_dtype(str_dtype, [str])
datetime_dtype = DType("datetime")
"""Datetime dtype"""
register_dtype(datetime_dtype, [datetime])
category_dtype = CategoryDType()
"""Categorical dtype with arbitraty categories"""
register_dtype(category_dtype, [Category])
window_dtype = DType("Window")
"""Window dtype"""
register_dtype(window_dtype, [Window])
embedding_dtype = EmbeddingDType()
"""Embedding dtype"""
register_dtype(embedding_dtype, [Embedding])
array_dtype = ArrayDType()
"""numpy array dtype"""
register_dtype(array_dtype, [np.ndarray])
image_dtype = DType("Image")
"""Image dtype"""
register_dtype(image_dtype, [Image])
audio_dtype = DType("Audio")
"""Audio dtype"""
register_dtype(audio_dtype, [Audio])
mesh_dtype = DType("Mesh")
"""Mesh dtype"""
register_dtype(mesh_dtype, [Mesh])
sequence_1d_dtype = Sequence1DDType()
"""1D-sequence dtype with arbitraty axis labels"""
register_dtype(sequence_1d_dtype, [Sequence1D])
video_dtype = DType("Video")
"""Video dtype"""
register_dtype(video_dtype, [Video])

mixed_dtype = DType("mixed")
"""Unknown or mixed dtype"""

file_dtype = DType("file")
"""File Dtype (bytes or str(path))"""


DTypeMap = Dict[str, DType]


def create_dtype(x: Any) -> DType:
    if isinstance(x, DType):
        return x
    if isinstance(x, str):
        return ALIASES[x.lower()]
    return ALIASES[x]


def is_bool_dtype(dtype: DType) -> bool:
    return dtype.name == "bool"


def is_int_dtype(dtype: DType) -> bool:
    return dtype.name == "int"


def is_float_dtype(dtype: DType) -> bool:
    return dtype.name == "float"


def is_str_dtype(dtype: DType) -> bool:
    return dtype.name == "str"


def is_datetime_dtype(dtype: DType) -> bool:
    return dtype.name == "datetime"


def is_category_dtype(dtype: DType) -> TypeGuard[CategoryDType]:
    return dtype.name == "Category"


def is_array_dtype(dtype: DType) -> TypeGuard[ArrayDType]:
    return dtype.name == "array"


def is_window_dtype(dtype: DType) -> bool:
    return dtype.name == "Window"


def is_embedding_dtype(dtype: DType) -> TypeGuard[EmbeddingDType]:
    return dtype.name == "Embedding"


def is_sequence_1d_dtype(dtype: DType) -> TypeGuard[Sequence1DDType]:
    return dtype.name == "Sequence1D"


def is_audio_dtype(dtype: DType) -> bool:
    return dtype.name == "Audio"


def is_image_dtype(dtype: DType) -> bool:
    return dtype.name == "Image"


def is_mesh_dtype(dtype: DType) -> bool:
    return dtype.name == "Mesh"


def is_video_dtype(dtype: DType) -> bool:
    return dtype.name == "Video"


def is_bytes_dtype(dtype: DType) -> bool:
    return dtype.name == "bytes"


def is_mixed_dtype(dtype: DType) -> bool:
    return dtype.name == "mixed"


def is_scalar_dtype(dtype: DType) -> bool:
    return dtype.name in ("bool", "int", "float")


def is_file_dtype(dtype: DType) -> bool:
    return dtype.name == "file"


def is_filebased_dtype(dtype: DType) -> bool:
    return dtype.name in ("Audio", "Image", "Video", "Mesh", "file")
