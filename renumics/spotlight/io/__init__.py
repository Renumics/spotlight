"""
Reading and writing of different data formats.
"""

import ast
from contextlib import suppress
from typing import Any

from .audio import (
    get_format_codec,
    get_waveform,
    read_audio,
    transcode_audio,
    write_audio,
)
from .gltf import (
    GLTF_DTYPES,
    GLTF_DTYPES_CONVERSION,
    GLTF_DTYPES_LOOKUP,
    GLTF_SHAPES,
    GLTF_SHAPES_LOOKUP,
    check_gltf,
    decode_gltf_arrays,
    encode_gltf_array,
)
from .huggingface import prepare_hugging_face_dict

__all__ = [
    "get_format_codec",
    "get_waveform",
    "read_audio",
    "write_audio",
    "transcode_audio",
    "GLTF_DTYPES",
    "GLTF_DTYPES_CONVERSION",
    "GLTF_DTYPES_LOOKUP",
    "GLTF_SHAPES",
    "GLTF_SHAPES_LOOKUP",
    "check_gltf",
    "decode_gltf_arrays",
    "encode_gltf_array",
    "prepare_hugging_face_dict",
    "try_literal_eval",
]


def try_literal_eval(x: str) -> Any:
    """
    Try to evaluate a literal expression, otherwise return value as is.
    """
    with suppress(Exception):
        return ast.literal_eval(x)
    return x
