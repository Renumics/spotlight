import io
import math
import os
from typing import IO, Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

import numpy as np
import pygltflib
import requests
import trimesh
import validators
from loguru import logger

from renumics.spotlight.media.base import Array2dLike, FileMediaType
from renumics.spotlight.requests import headers
from renumics.spotlight.typing import PathType

from ..io import gltf
from . import exceptions


class Mesh(FileMediaType):
    """
    Triangular 3D mesh with optional per-point and per-triangle attributes and
    optional per-point displacements over time.

    Example:
        >>> import numpy as np
        >>> from renumics.spotlight import Dataset, Mesh
        >>> points = np.array([[0,0,0],[1,1,1],[0,1,0],[-1,0,1]])
        >>> triangles = np.array([[0,1,2],[2,3,0]])
        >>> mesh = Mesh(points, triangles)
        >>> with Dataset("docs/example.h5", "w") as dataset:
        ...     dataset.append_mesh_column("meshes", 5*[mesh])
        >>> with Dataset("docs/example.h5", "r") as dataset:
        ...     print(dataset["meshes", 2].triangles)
        [[0 1 2]
         [2 3 0]]
    """

    _points: np.ndarray
    _triangles: np.ndarray
    _point_attributes: Dict[str, np.ndarray]
    _point_displacements: List[np.ndarray]

    _point_indices: np.ndarray
    _triangle_indices: np.ndarray
    _triangle_attribute_indices: np.ndarray

    def __init__(
        self,
        points: Array2dLike,
        triangles: Array2dLike,
        point_attributes: Optional[Dict[str, np.ndarray]] = None,
        triangle_attributes: Optional[Dict[str, np.ndarray]] = None,
        point_displacements: Optional[Union[np.ndarray, List[np.ndarray]]] = None,
    ):
        self._point_attributes = {}
        self._point_displacements = []
        self._set_points_triangles(points, triangles)

        if point_displacements is None:
            point_displacements = []
        self.point_displacements = point_displacements  # type: ignore
        self.update_attributes(point_attributes, triangle_attributes)

    @property
    def points(self) -> np.ndarray:
        """
        :code:`np.array` with shape `(num_points, 3)`. Mesh points.
        """
        return self._points

    @property
    def triangles(self) -> np.ndarray:
        """
        :code:`np.array` with shape `(num_triangles, 3)`. Mesh triangles stored as their
        CCW nodes referring to the `points` indices.
        """
        return self._triangles

    @property
    def point_attributes(self) -> Dict[str, np.ndarray]:
        """
        Mapping str -> :code:`np.array` with shape `(num_points, ...)`. Point-wise
        attributes corresponding to `points`. All possible shapes of a single
        attribute can be found in
        `renumics.spotlight.mesh_proc.gltf.GLTF_SHAPES`.
        """
        return self._point_attributes

    @property
    def point_displacements(self) -> List[np.ndarray]:
        """
        List of arrays with shape `(num_points, 3)`. Point-wise relative
        displacements (offsets) over the time corresponding to `points`.
        Timestep 0 is omitted since it is explicit stored as absolute values in
        `points`.
        """
        return self._point_displacements

    @point_displacements.setter
    def point_displacements(self, value: Union[np.ndarray, List[np.ndarray]]) -> None:
        array = attribute_to_array(value)
        if array.size == 0:
            self._point_displacements = []
        else:
            array = array.astype(np.float32)
            if array.shape[1] != len(self._points):
                array = array[:, self._point_indices]
            if array.shape[1:] != (len(self._points), 3):
                raise ValueError(
                    f"Point displacements should have the same shape as points "
                    f"({self._points.shape}), but shape {array.shape[1:]} "
                    f"received."
                )
            self._point_displacements = list(array)

    @classmethod
    def from_trimesh(cls, mesh: trimesh.Trimesh) -> "Mesh":
        """
        Import a `trimesh.Trimesh` mesh.
        """
        return cls(
            mesh.vertices, mesh.faces, mesh.vertex_attributes, mesh.face_attributes
        )

    @classmethod
    def from_file(cls, filepath: PathType) -> "Mesh":
        """
        Read mesh from a filepath or an URL.

        `trimesh` is used inside, so only supported formats are allowed.
        """
        file: Union[str, IO] = (
            str(filepath) if isinstance(filepath, os.PathLike) else filepath
        )
        extension = None
        if isinstance(file, str):
            if validators.url(file):
                response = requests.get(file, headers=headers, timeout=30)
                if not response.ok:
                    raise exceptions.InvalidFile(f"URL {file} does not exist.")
                extension = os.path.splitext(urlparse(file).path)[1]
                if extension == "":
                    raise exceptions.InvalidFile(f"URL {file} has no file extension.")
                file = io.BytesIO(response.content)
            elif not os.path.isfile(file):
                raise exceptions.InvalidFile(
                    f"File {file} is neither an existing file nor an existing URL."
                )
        try:
            mesh = trimesh.load(file, file_type=extension, force="mesh")
        except Exception as e:
            raise exceptions.InvalidFile(
                f"Mesh {filepath} does not exist or could not be read."
            ) from e
        return cls.from_trimesh(mesh)

    @classmethod
    def empty(cls) -> "Mesh":
        """
        Create an empty mesh.
        """
        return cls(np.empty((0, 3)), np.empty((0, 3), np.int64))

    @classmethod
    def decode(cls, value: Union[np.ndarray, np.void]) -> "Mesh":
        gltf_mesh = pygltflib.GLTF2.load_from_bytes(value.tobytes())
        gltf.check_gltf(gltf_mesh)
        arrays = gltf.decode_gltf_arrays(gltf_mesh)
        primitive = gltf_mesh.meshes[0].primitives[0]
        points = arrays[primitive.attributes.POSITION]
        triangles = arrays[primitive.indices].reshape((-1, 3))
        point_attributes = {
            k[1:]: arrays[v]
            for k, v in primitive.attributes.__dict__.items()
            if k.startswith("_")
        }
        point_displacements = [
            arrays[target["POSITION"]] for target in primitive.targets
        ]
        return cls(
            points, triangles, point_attributes, point_displacements=point_displacements
        )

    def encode(self, _target: Optional[str] = None) -> np.void:
        bin_data, buffer_views, accessors = gltf.encode_gltf_array(
            self._triangles.flatten(), b"", [], [], pygltflib.ELEMENT_ARRAY_BUFFER
        )
        mesh_primitive_attributes_kwargs = {"POSITION": 1}
        bin_data, buffer_views, accessors = gltf.encode_gltf_array(
            self._points, bin_data, buffer_views, accessors
        )
        for attr_name, point_attr in self._point_attributes.items():
            mesh_primitive_attributes_kwargs["_" + attr_name] = len(buffer_views)
            bin_data, buffer_views, accessors = gltf.encode_gltf_array(
                point_attr, bin_data, buffer_views, accessors
            )
        morph_targets = []
        for point_displacement in self._point_displacements:
            morph_targets.append(pygltflib.Attributes(POSITION=len(buffer_views)))
            bin_data, buffer_views, accessors = gltf.encode_gltf_array(
                point_displacement, bin_data, buffer_views, accessors
            )
        gltf_mesh = pygltflib.GLTF2(
            asset=pygltflib.Asset(),
            scene=0,
            scenes=[pygltflib.Scene(nodes=[0])],
            nodes=[pygltflib.Node(mesh=0)],
            meshes=[
                pygltflib.Mesh(
                    primitives=[
                        pygltflib.Primitive(
                            attributes=pygltflib.Attributes(
                                **mesh_primitive_attributes_kwargs
                            ),
                            indices=0,
                            mode=pygltflib.TRIANGLES,
                            targets=morph_targets,
                        )
                    ],
                )
            ],
            accessors=accessors,
            bufferViews=buffer_views,
            buffers=[pygltflib.Buffer(byteLength=len(bin_data))],
        )
        gltf_mesh.set_binary_blob(bin_data)
        return np.void(b"".join(gltf_mesh.save_to_bytes()))

    def update_attributes(
        self,
        point_attributes: Optional[Dict[str, np.ndarray]] = None,
        triangle_attributes: Optional[Dict[str, np.ndarray]] = None,
    ) -> None:
        """
        Update point and/or triangle attributes dict-like.
        """
        if point_attributes:
            point_attributes = self._sanitize_point_attributes(point_attributes)
            self._point_attributes.update(point_attributes)
        if triangle_attributes:
            triangle_attributes = self._sanitize_triangle_attributes(
                triangle_attributes
            )
            logger.info("Triangle attributes will be converted to point attributes.")
            self._point_attributes.update(
                self._triangle_attributes_to_point_attributes(triangle_attributes)
            )

    def interpolate_point_displacements(self, num_timesteps: int) -> None:
        """subsample time dependent attributes with new time step count"""
        if num_timesteps < 1:
            raise ValueError(
                f"`num_timesteps` argument should be non-negative, but "
                f"{num_timesteps} received."
            )
        current_num_timesteps = len(self._point_displacements)
        if current_num_timesteps == 0:
            logger.info("No displacements found, so cannot interpolate.")
            return
        if current_num_timesteps == num_timesteps:
            return

        def _interpolated_list_access(
            arrays: List[np.ndarray], index_float: float
        ) -> np.ndarray:
            """access a list equally sized numpy arrays with interpolation between two neighbors"""
            array_left = arrays[math.floor(index_float)]
            array_right = arrays[math.ceil(index_float)]
            weight_right = index_float - math.floor(index_float)
            return (array_left * (1 - weight_right)) + (array_right * weight_right)

        # simplification assumption : timesteps are equally sized
        timesteps = np.linspace(0, current_num_timesteps, num_timesteps + 1)[1:]

        # add implicit 0 displacement for t=0
        displacements = [
            np.zeros_like(self._point_displacements[0])
        ] + self._point_displacements
        self._point_displacements = [
            _interpolated_list_access(displacements, t) for t in timesteps
        ]

    def _set_points_triangles(
        self, points: Array2dLike, triangles: Array2dLike
    ) -> None:
        # Check points.
        points_array = np.asarray(points, np.float32)
        if points_array.ndim != 2 or points_array.shape[1] != 3:
            raise ValueError(
                f"`points` argument should be a numpy array with shape "
                f"`(num_points, 3)`, but shape {points_array.shape} received."
            )
        # Check triangles.
        triangles_array = np.asarray(triangles, np.uint32)
        if triangles_array.ndim != 2 or triangles_array.shape[1] != 3:
            raise ValueError(
                f"`triangles` argument should be a numpy array with shape "
                f"`(num_triangles, 3)`, but shape {triangles_array.shape} received."
            )
        # Subsample only valid points and triangles.
        point_ids = np.arange(len(points_array))
        valid_triangles_mask = (
            (triangles_array[:, 0] != triangles_array[:, 1])
            & (triangles_array[:, 0] != triangles_array[:, 2])
            & (triangles_array[:, 1] != triangles_array[:, 2])
            & np.isin(triangles_array, point_ids).all(axis=1)
        )
        self._triangle_indices = np.nonzero(valid_triangles_mask)[0]
        self._triangles = triangles_array[self._triangle_indices]
        valid_points_mask = np.isin(point_ids, self._triangles)
        self._point_indices = np.nonzero(valid_points_mask)[0]
        self._points = points_array[self._point_indices]
        # Reindex triangles since there can be fewer points than before.
        point_ids = point_ids[self._point_indices]
        self._triangles, *_ = reindex(point_ids, self._triangles)
        # Set indices for conversion of triangle attributes to point attributes.
        self._triangle_attribute_indices = np.full((len(self._points)), 0, np.uint32)
        triangle_indices = np.arange(len(self._triangles), dtype=np.uint32)
        self._triangle_attribute_indices[self._triangles[:, 0]] = triangle_indices
        self._triangle_attribute_indices[self._triangles[:, 1]] = triangle_indices
        self._triangle_attribute_indices[self._triangles[:, 2]] = triangle_indices

    def _triangle_attributes_to_point_attributes(
        self, triangle_attributes: Dict[str, np.ndarray]
    ) -> Dict[str, np.ndarray]:
        return {
            f"element_{attr_name}": triangle_attr[self._triangle_attribute_indices]
            for attr_name, triangle_attr in triangle_attributes.items()
        }

    def _sanitize_point_attributes(
        self, point_attributes: Dict[str, np.ndarray]
    ) -> Dict[str, np.ndarray]:
        if not isinstance(point_attributes, dict):
            raise TypeError(
                f"`point_attributes` argument should be a dict, but "
                f"{type(point_attributes)} received."
            )
        valid_point_attributes = {}
        for attr_name, point_attr in point_attributes.items():
            point_attr = np.asarray(point_attr)
            if len(point_attr) != len(self._points):
                point_attr = point_attr[self._point_indices]
            if point_attr.dtype.str[1] not in "fiu":
                raise ValueError(
                    f"Point attributes should have one of integer or float "
                    f'dtypes, but attribute "{attr_name}" of dtype '
                    f"{point_attr.dtype.name} received."
                )
            point_attr = point_attr.squeeze()
            if point_attr.shape[1:] not in gltf.GLTF_SHAPES_LOOKUP.keys():
                logger.warning(
                    f"Element shape {point_attr.shape[1:]} of the point "
                    f'attribute "{attr_name}" not supported, attribute will be '
                    f"removed."
                )
                continue
            valid_point_attributes[attr_name] = point_attr.astype(
                gltf.GLTF_DTYPES_CONVERSION[point_attr.dtype.str[1:]]
            )
        return valid_point_attributes

    def _sanitize_triangle_attributes(
        self, triangle_attributes: Dict[str, np.ndarray]
    ) -> Dict[str, np.ndarray]:
        if not isinstance(triangle_attributes, dict):
            raise TypeError(
                f"`triangle_attributes` argument should be a dict, but "
                f"{type(triangle_attributes)} received."
            )
        valid_triangle_attributes = {}
        for attr_name, triangle_attr in triangle_attributes.items():
            triangle_attr = np.asarray(triangle_attr)
            if len(triangle_attr) != len(self._triangles):
                triangle_attr = triangle_attr[self._triangle_indices]
            if triangle_attr.dtype.str[1] not in "fiu":
                raise ValueError(
                    f"Triangle attributes should have one of integer or float "
                    f'dtypes, but attribute "{attr_name}" of dtype '
                    f"{triangle_attr.dtype.name} received."
                )
            triangle_attr = triangle_attr.squeeze()
            if triangle_attr.shape[1:] not in gltf.GLTF_SHAPES_LOOKUP.keys():
                logger.warning(
                    f"Element shape {triangle_attr.shape[1:]} of the triangle "
                    f'attribute "{attr_name}" not supported, attribute will be '
                    f"removed."
                )
                continue
            valid_triangle_attributes[attr_name] = triangle_attr.astype(
                gltf.GLTF_DTYPES_CONVERSION[triangle_attr.dtype.str[1:]]
            )
        return valid_triangle_attributes


def reindex(point_ids: np.ndarray, *elements: np.ndarray) -> Tuple[np.ndarray, ...]:
    """
    Reindex elements which refer to the non-negative unique point ids so that
    they refer to the indices of point ids (`np.arange(len(point_ids))`) in the
    same way.
    """
    if elements:
        inverse_point_ids = np.full(
            max((x.max(initial=0) for x in (point_ids, *elements))) + 1,
            -1,
            np.int64,
        )
        inverse_point_ids[point_ids] = np.arange(len(point_ids))
        return tuple(inverse_point_ids[x].astype(x.dtype) for x in elements)
    return ()


def attribute_to_array(attribute: Union[np.ndarray, List[np.ndarray]]) -> np.ndarray:
    """
    Encode a single attribute or a list of attribute steps as array with shape
    `(num_steps, n, ...)` and squeeze all dimensions except for 0 and 1.
    """
    if not isinstance(attribute, list):
        attribute = [attribute]
    attribute = np.asarray(attribute)
    attribute = attribute.reshape(
        (*attribute.shape[:2], *(x for x in attribute.shape[2:] if x != 1))
    )
    return attribute


def triangulate(
    triangles: Optional[np.ndarray] = None,
    triangle_attributes: Optional[
        Dict[str, Union[np.ndarray, List[np.ndarray]]]
    ] = None,
    quadrangles: Optional[np.ndarray] = None,
    quadrangle_attributes: Optional[
        Dict[str, Union[np.ndarray, List[np.ndarray]]]
    ] = None,
) -> Tuple[np.ndarray, Dict[str, Union[np.ndarray, List[np.ndarray]]]]:
    """
    Triangulate quadrangles and respective attributes and append them to the
    given triangles/attributes.
    """

    attrs = {}
    if triangles is None:
        trias = np.empty((0, 3), np.uint32)
        if triangle_attributes:
            raise ValueError(
                f"`triangles` not given, but `triangle_attributes` have "
                f"{len(triangle_attributes)} items."
            )
    else:
        trias = triangles
        if triangle_attributes is not None:
            for attr_name, triangle_attr in triangle_attributes.items():
                attrs[attr_name] = attribute_to_array(triangle_attr)

    if quadrangles is None:
        if quadrangle_attributes is not None and len(quadrangle_attributes) != 0:
            raise ValueError(
                f"`quadrangles` not given, but `quadrangle_attributes` have "
                f"{len(quadrangle_attributes)} items."
            )
    else:
        trias = np.concatenate(
            (trias, quadrangles[:, [0, 1, 2]], quadrangles[:, [0, 2, 3]])
        )
        for attr_name, quadrangle_attr in (quadrangle_attributes or {}).items():
            quadrangle_attr = attribute_to_array(quadrangle_attr)
            try:
                attr = attrs[attr_name]
            except KeyError:
                attrs[attr_name] = np.concatenate(
                    (quadrangle_attr, quadrangle_attr), axis=1
                )
            else:
                attrs[attr_name] = np.concatenate(
                    (attr, quadrangle_attr, quadrangle_attr), axis=1
                )

    for attr_name, attr in attrs.items():
        if attr.shape[1] != len(trias):
            raise ValueError(
                f"Values of attributes should have the same length as "
                f"triangles ({len(trias)}), but length {attr.shape[1]} "
                f"received."
            )
    return (
        trias,
        {
            attr_name: attr[0] if len(attr) == 1 else list(attr)
            for attr_name, attr in attrs.items()
        },
    )


def clean(
    points: np.ndarray,
    triangles: np.ndarray,
    point_attributes: Optional[Dict[str, np.ndarray]] = None,
    triangle_attributes: Optional[Dict[str, np.ndarray]] = None,
    point_displacements: Optional[List[np.ndarray]] = None,
) -> Tuple[
    np.ndarray,
    np.ndarray,
    Dict[str, np.ndarray],
    Dict[str, np.ndarray],
    List[np.ndarray],
]:
    """
    Remove:
        degenerated triangles and respective attributes;
        invalid triangles and respective attributes;
        invalid points and respective attributes;
        empty attributes and point displacements.
    """
    point_ids = np.arange(len(points))
    valid_triangles_mask = (
        (triangles[:, 0] != triangles[:, 1])
        & (triangles[:, 0] != triangles[:, 2])
        & (triangles[:, 1] != triangles[:, 2])
        & np.isin(triangles, point_ids).all(axis=1)
    )
    triangles = triangles[valid_triangles_mask]
    triangle_attributes = {
        k: (
            [x[valid_triangles_mask] for x in v]
            if isinstance(v, list)
            else v[valid_triangles_mask]
        )
        for k, v in (triangle_attributes or {}).items()
    }

    valid_points_mask = np.isin(point_ids, triangles)
    points = points[valid_points_mask]
    point_attributes = {
        k: (
            [x[valid_points_mask] for x in v]
            if isinstance(v, list)
            else v[valid_points_mask]
        )
        for k, v in (point_attributes or {}).items()
    }
    point_displacements = [x[valid_points_mask] for x in point_displacements or []]
    point_ids = point_ids[valid_points_mask]
    triangles, *_ = reindex(point_ids, triangles)

    return (
        points,
        triangles,
        {k: v for k, v in point_attributes.items() if len(v) > 0},
        {k: v for k, v in triangle_attributes.items() if len(v) > 0},
        [x for x in point_displacements if len(x) > 0],
    )
