"""
Spotlight data types.

The most dtypes are non-customazable and can be used through simple importing
the respective module variables (e.g. [`float_dtype`](#float_dtype),
[`image_dtype`](#image_dtype)).

Some dtypes are customazable and only their default versions can be defined
through the respective module variables (e.g. [`category_dtype`](#category_dtype),
[`embedding_dtype`](#embedding_dtype)). For more info, see the module classes.

In the most usage cases string or object aliases can be used instead of the
default dtypes. For more info, see the module classes.

The main usage of the dtypes is customizing the [`spotlight.show`](../#show()).
"""


from datetime import datetime
from typing import Any, Dict, Iterable, Optional, Tuple, Union

import numpy as np
from typing_extensions import TypeGuard

from .legacy import Audio, Category, Embedding, Image, Mesh, Sequence1D, Video, Window


__all__ = [
    "CategoryDType",
    "ArrayDType",
    "EmbeddingDType",
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

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, DType):
            return other._name == self._name
        return False

    def __hash__(self) -> int:
        return hash(self._name)

    @property
    def name(self) -> str:
        return self._name


class CategoryDType(DType):
    """
    Categorical dtype with predefined categories.

    Category names and codes are assured to be unique. Empty categories mean to
    be defined later (in this case, equivalent to the
    [`category_dtype`](#category_dtype) module variable).

    Using with category names:
        >>> from renumics.spotlight import dtypes
        >>> dtype = dtypes.CategoryDType(["cat", "dog"])
        >>> str(dtype)
        'Category'
        >>> dtype.categories
        {'cat': 0, 'dog': 1}
        >>> dtype.inverted_categories
        {0: 'cat', 1: 'dog'}

    Example of usage with category mapping:
        >>> from renumics.spotlight import dtypes
        >>> dtype = dtypes.CategoryDType({"four": 4, "two": 2})
        >>> dtype.categories
        {'two': 2, 'four': 4}

    Example of usage with empty categories:
        >>> from renumics.spotlight import dtypes
        >>> dtype = dtypes.CategoryDType()
        >>> dtype == dtypes.category_dtype
        True
    """

    _categories: Optional[Dict[str, int]]
    _inverted_categories: Optional[Dict[int, str]]

    def __init__(
        self, categories: Optional[Union[Iterable[str], Dict[str, int]]] = None
    ):
        super().__init__("Category")
        if isinstance(categories, dict):
            self._categories = dict(sorted(categories.items(), key=lambda x: x[1]))
        elif categories is None:
            self._categories = None
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

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, CategoryDType):
            return other._categories == self._categories
        return False

    def __hash__(self) -> int:
        if self._categories is None:
            return hash(self._name) ^ hash(None)
        return (
            hash(self._name)
            ^ hash(tuple(self._categories.keys()))
            ^ hash(tuple(self._categories.values()))
        )

    @property
    def categories(self) -> Optional[Dict[str, int]]:
        """
        Category mapping (string category -> integer code).
        """
        return self._categories

    @property
    def inverted_categories(self) -> Optional[Dict[int, str]]:
        """
        Inverted Category mapping (integer code -> string category).
        """
        return self._inverted_categories


class ArrayDType(DType):
    """
    Array dtype with optional shape.

    Attributes:
        shape: Array dimensions. Can be fully or partially defined. No shape
            means to be defined later.

    Example of usage with defined shape:
        >>> from renumics.spotlight import dtypes
        >>> dtype = dtypes.ArrayDType((10, None, 4))
        >>> str(dtype)
        'array'
        >>> dtype.shape
        (10, None, 4)
        >>> dtype.ndim
        3

    Example of usage with empty shape:
        >>> from renumics.spotlight import dtypes
        >>> dtype = dtypes.ArrayDType()
        >>> dtype.ndim
        0
        >>> dtype == dtypes.array_dtype
        True
    """

    shape: Optional[Tuple[Optional[int], ...]]

    def __init__(self, shape: Optional[Tuple[Optional[int], ...]] = None):
        super().__init__("array")
        self.shape = shape

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ArrayDType):
            return other.shape == self.shape
        return False

    def __hash__(self) -> int:
        return hash(self._name) ^ hash(self.shape)

    @property
    def ndim(self) -> int:
        """
        Number of array dimensions.
        """
        if self.shape is None:
            return 0
        return len(self.shape)


class EmbeddingDType(DType):
    """
    Embedding dtype with optional length.

    Attributes:
        length: Embedding length. No length means to be defined later.

    Example of usage with defined length:
        >>> from renumics.spotlight import dtypes
        >>> dtype = dtypes.EmbeddingDType(8)
        >>> str(dtype)
        'Embedding'
        >>> dtype.length
        8

    Example of usage with empty length:
        >>> from renumics.spotlight import dtypes
        >>> dtype = dtypes.EmbeddingDType()
        >>> dtype == dtypes.embedding_dtype
        True
    """

    length: Optional[int]

    def __init__(self, length: Optional[int] = None):
        super().__init__("Embedding")
        if length is not None and length < 0:
            raise ValueError(f"Length must be non-negative, but {length} received.")
        self.length = length

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, EmbeddingDType):
            return other.length == self.length
        return False

    def __hash__(self) -> int:
        return hash(self._name) ^ hash(self.length)


class Sequence1DDType(DType):
    """
    1D-sequence dtype with optional axis names.

    Attributes:
        x_label: Optional name of the x axis.
        y_label: Optional name of the y axis.

    Example of usage with defined labels:
        >>> from renumics.spotlight import dtypes
        >>> dtype = dtypes.Sequence1DDType("time", "acceleration")
        >>> str(dtype)
        'Sequence1D'
        >>> dtype.x_label
        'time'
        >>> dtype.y_label
        'acceleration'

    Example of usage with empty labels:
        >>> from renumics.spotlight import dtypes
        >>> dtype = dtypes.Sequence1DDType()
        >>> dtype == dtypes.sequence_1d_dtype
        True
    """

    x_label: str
    y_label: str

    def __init__(self, x_label: str = "x", y_label: str = "y"):
        super().__init__("Sequence1D")
        self.x_label = x_label
        self.y_label = y_label

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Sequence1DDType):
            return other.x_label == self.x_label and other.y_label == self.y_label
        return False

    def __hash__(self) -> int:
        return hash(self._name) ^ hash(self.x_label) ^ hash(self.y_label)


ALIASES: Dict[Any, DType] = {}


def register_dtype(dtype: DType, aliases: Optional[list] = None) -> None:
    assert dtype.name.lower() not in ALIASES
    ALIASES[dtype.name.lower()] = dtype

    if aliases is not None:
        for alias in aliases:
            assert alias not in ALIASES
            ALIASES[alias] = dtype


bool_dtype = DType("bool")
"""
Bool dtype. Aliases: `"bool"`, `bool`.
"""
register_dtype(bool_dtype, [bool])

int_dtype = DType("int")
"""
Integer dtype. Aliases: `"int"`, `int`.
"""
register_dtype(int_dtype, [int])

float_dtype = DType("float")
"""
Float dtype. Aliases: `"float"`, `float`.
"""
register_dtype(float_dtype, [float])

bytes_dtype = DType("bytes")
"""
Bytes dtype. Aliases: `"bytes"`, `bytes`.
"""
register_dtype(bytes_dtype, [bytes])

str_dtype = DType("str")
"""
String dtype. Aliases: `"str"`, `str`.
"""
register_dtype(str_dtype, [str])

datetime_dtype = DType("datetime")
"""
Datetime dtype. Aliases: `"datetime"`, `datetime.datetime`.
"""
register_dtype(datetime_dtype, [datetime])

category_dtype = CategoryDType()
"""
Categorical dtype with arbitraty categories. Aliases: `"Category"`.
"""
register_dtype(category_dtype, [Category])

window_dtype = DType("Window")
"""
Window dtype. Aliases: `"Window"`.
"""
register_dtype(window_dtype, [Window])

embedding_dtype = EmbeddingDType()
"""
Embedding dtype. Aliases: `"Embedding"`, `renumics.spotlight.media.Embedding`.
"""
register_dtype(embedding_dtype, [Embedding])

array_dtype = ArrayDType()
"""
numpy array dtype. Aliases: `"array"`, `np.ndarray`.
"""
register_dtype(array_dtype, [np.ndarray])

image_dtype = DType("Image")
"""
Image dtype. Aliases: `"Image"`, `renumics.spotlight.media.Image`.
"""
register_dtype(image_dtype, [Image])

audio_dtype = DType("Audio")
"""
Audio dtype. Aliases: `"Audio"`, `renumics.spotlight.media.Audio`.
"""
register_dtype(audio_dtype, [Audio])

mesh_dtype = DType("Mesh")
"""
Mesh dtype. Aliases: `"Mesh"`, `renumics.spotlight.media.Mesh`.
"""
register_dtype(mesh_dtype, [Mesh])

sequence_1d_dtype = Sequence1DDType()
"""
1D-sequence dtype with arbitraty axis labels. Aliases: `"Sequence1D"`,
`renumics.spotlight.media.Sequence1D`.
"""
register_dtype(sequence_1d_dtype, [Sequence1D])

video_dtype = DType("Video")
"""
Video dtype. Aliases: `"video"`, `renumics.spotlight.media.Video`.
"""
register_dtype(video_dtype, [Video])

mixed_dtype = DType("mixed")
"""
Unknown or mixed dtype. Aliases: `"mixed"`.
"""

file_dtype = DType("file")
"""
File Dtype (bytes or str(path)). Aliases: `"file"`.
"""


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
