"""
This module provides utilities for handling glTF format.
"""

from typing import List, Tuple

import numpy as np
import pygltflib


GLTF_DTYPES_CONVERSION = {
    "i1": "<i1",
    "i2": "<i2",
    "i4": "<i2",
    "i8": "<i2",
    "i16": "<i2",
    "u1": "<u1",
    "u2": "<u2",
    "u4": "<u4",
    "u8": "<u4",
    "u16": "<u4",
    "f2": "<f4",
    "f4": "<f4",
    "f8": "<f4",
    "f16": "<f4",
}

GLTF_DTYPES = {
    pygltflib.BYTE: "<i1",
    pygltflib.SHORT: "<i2",
    pygltflib.UNSIGNED_BYTE: "<u1",
    pygltflib.UNSIGNED_SHORT: "<u2",
    pygltflib.UNSIGNED_INT: "<u4",
    pygltflib.FLOAT: "<f4",
}

GLTF_DTYPES_LOOKUP = {v[1:]: k for k, v in GLTF_DTYPES.items()}

GLTF_SHAPES = {
    pygltflib.SCALAR: (),
    pygltflib.VEC2: (2,),
    pygltflib.VEC3: (3,),
    pygltflib.VEC4: (4,),
}  # MAT2, MAT3 and MAT4 are currently not supported.

GLTF_SHAPES_LOOKUP = {v: k for k, v in GLTF_SHAPES.items()}


def check_gltf(gltf: pygltflib.GLTF2) -> None:
    """
    Check whether a glTF mesh can be parsed.

    glTF mesh is required to have exactly one scene, one node, one mesh, one
    primitive with mode "TRIANGLES" (4) and one buffer.
    """
    if (
        len(gltf.scenes) != 1
        or len(gltf.nodes) != 1
        or len(gltf.meshes) != 1
        or len(gltf.meshes[0].primitives) != 1
    ):
        raise ValueError(
            f"glTF file with exactly one scene, one node, one mesh and one "
            f"primitive expected, but {len(gltf.scenes)} scenes, "
            f"{len(gltf.nodes)} nodes, {len(gltf.meshes)} meshes and "
            f"{len(gltf.meshes[0].primitives)} received."
        )
    if gltf.meshes[0].primitives[0].mode != pygltflib.TRIANGLES:
        raise ValueError(
            f"glTF mesh with primitive of mode TRIANGLES "
            f"({pygltflib.TRIANGLES}) expected, but mode "
            f"{gltf.meshes[0].primitives[0].mode} received."
        )
    if gltf.scene != 0 or gltf.scenes[0].nodes != [0] or gltf.nodes[0].mesh != 0:
        raise ValueError("Invalid glTF hierarchy.")
    if (
        len(gltf.buffers) != 1
        or gltf.buffers[0].uri not in [None, ""]
        or gltf.buffers[0].byteLength != len(gltf.binary_blob())
    ):
        raise ValueError("Invalid glTF buffer structure.")


def pad_bin_data(bin_data: bytes, bound: int = 4) -> bytes:
    """
    Pad binary data to the given bound.
    """
    bound = int(bound)
    if bound < 2:
        return bin_data
    data_length = len(bin_data)
    if data_length % bound == 0:
        return bin_data
    return bin_data + b"\0" * (bound - data_length % bound)


def encode_gltf_array(
    array: np.ndarray,
    bin_data: bytes,
    buffer_views: List[pygltflib.BufferView],
    accessors: List[pygltflib.Accessor],
    buffer_view_target: int = pygltflib.ARRAY_BUFFER,
) -> Tuple[bytes, List[pygltflib.BufferView], List[pygltflib.Accessor]]:
    """
    Encode a single array as expected by pygltflib, update binary blob, lists
    with buffer views and accessors.
    """
    array = array.squeeze().astype(GLTF_DTYPES_CONVERSION[array.dtype.str[1:]])
    array_bin_data = array.tobytes()
    if array.size > 0:
        if array.dtype.str[1] == "f":
            # For float arrays, do not count non-finite values.
            finite_mask = np.isfinite(array)
            max_list = array.max(axis=0, initial=-np.inf, where=finite_mask)
            min_list = array.min(axis=0, initial=np.inf, where=finite_mask)
            max_list = np.where(
                ~np.isfinite(max_list), np.array(None), max_list
            ).tolist()
            min_list = np.where(
                ~np.isfinite(min_list), np.array(None), min_list
            ).tolist()
        else:
            max_list = array.max(axis=0).tolist()
            min_list = array.min(axis=0).tolist()
        if len(array.shape) == 1:
            max_list = [max_list]
            min_list = [min_list]
    else:
        max_list = []
        min_list = []
    accessors.append(
        pygltflib.Accessor(
            bufferView=len(buffer_views),
            byteOffset=0,
            componentType=GLTF_DTYPES_LOOKUP[array.dtype.str[1:]],
            count=len(array),
            type=GLTF_SHAPES_LOOKUP[array.shape[1:]],
            max=max_list,
            min=min_list,
        )
    )
    buffer_views.append(
        pygltflib.BufferView(
            buffer=0,
            byteOffset=len(bin_data),
            byteLength=len(array_bin_data),
            target=buffer_view_target,
        )
    )
    return bin_data + pad_bin_data(array_bin_data), buffer_views, accessors


def decode_gltf_arrays(gltf: pygltflib.GLTF2) -> List[np.ndarray]:
    """
    Decode all arrays from glTF instance accessors.

    It is assumed that only one buffer is used (as it should be for glb format).
    """
    bin_data = gltf.binary_blob()

    buffer_views = []
    for buffer_view in gltf.bufferViews:
        buffer_views.append(
            bin_data[
                buffer_view.byteOffset : buffer_view.byteOffset + buffer_view.byteLength
            ]
        )

    arrays = []
    for accessor in gltf.accessors:
        accessor_bin_data = buffer_views[accessor.bufferView]
        shape = (accessor.count, *GLTF_SHAPES[accessor.type])
        array_flatten = np.frombuffer(
            accessor_bin_data[accessor.byteOffset :],
            dtype=GLTF_DTYPES[accessor.componentType],
            count=int(np.prod(shape)),
        )
        array = array_flatten.reshape(shape)
        arrays.append(array)
    return arrays
