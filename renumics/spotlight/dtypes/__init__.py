"""
This module provides custom data types for Spotlight dataset.
"""

import io
import math
import os
from abc import ABC, abstractmethod
from typing import Dict, IO, List, Optional, Sequence, Tuple, Union
from urllib.parse import urlparse

import imageio.v3 as iio
import numpy as np
import pygltflib
import requests
import trimesh
import validators
from loguru import logger

from renumics.spotlight.requests import headers
from renumics.spotlight.typing import NumberType, PathType
from . import triangulation
from ..io import audio, gltf
from . import exceptions

Array1DLike = Union[Sequence[NumberType], np.ndarray]
Array2DLike = Union[Sequence[Sequence[NumberType]], np.ndarray]
ImageLike = Union[
    Sequence[Sequence[Union[NumberType, Sequence[NumberType]]]], np.ndarray
]


class _BaseData(ABC):
    """
    Base Spotlight dataset field data.
    """

    @classmethod
    @abstractmethod
    def decode(cls, value: Union[np.ndarray, np.void]) -> "_BaseData":
        """
        Restore class from its numpy representation.
        """
        raise NotImplementedError

    @abstractmethod
    def encode(self, target: Optional[str] = None) -> Union[np.ndarray, np.void]:
        """
        Convert to numpy for storing in dataset.

        Args:
            target: Optional target format.
        """
        raise NotImplementedError


class _BaseFileBasedData(_BaseData):
    """
    Spotlight dataset field data which can be read from a file.
    """

    @classmethod
    @abstractmethod
    def from_file(cls, filepath: PathType) -> "_BaseFileBasedData":
        """
        Read data from a file.
        """
        raise NotImplementedError


class Embedding(_BaseData):
    """
    Data sample projected onto a new space.

    Attributes:
        data: 1-dimensional array-like. Sample embedding.
        dtype: Optional data type of embedding. If `None`, data type inferred
            from data.

    Example:
        >>> import numpy as np
        >>> from renumics.spotlight import Dataset, Embedding
        >>> value = np.array(np.random.rand(2))
        >>> embedding = Embedding(value)
        >>> with Dataset("docs/example.h5", "w") as dataset:
        ...     dataset.append_embedding_column("embeddings", 5*[embedding])
        >>> with Dataset("docs/example.h5", "r") as dataset:
        ...     print(len(dataset["embeddings", 3].data))
        2
    """

    data: np.ndarray

    def __init__(
        self, data: Array1DLike, dtype: Optional[Union[str, np.dtype]] = None
    ) -> None:
        data_array = np.asarray(data, dtype)
        if data_array.ndim != 1 or data_array.size == 0:
            raise ValueError(
                f"`data` argument should an array-like with shape "
                f"`(num_features,)` with `num_features > 0`, but shape "
                f"{data_array.shape} received."
            )
        if data_array.dtype.str[1] not in "fiu":
            raise ValueError(
                f"`data` argument should be an array-like with integer or "
                f"float dtypes, but dtype {data_array.dtype.name} received."
            )
        self.data = data_array

    @classmethod
    def decode(cls, value: Union[np.ndarray, np.void]) -> "Embedding":
        if not isinstance(value, np.ndarray):
            raise TypeError(
                f"`value` argument should be a numpy array, but {type(value)} "
                f"received."
            )
        return cls(value)

    def encode(self, _target: Optional[str] = None) -> np.ndarray:
        return self.data


class Sequence1D(_BaseData):
    """
    One-dimensional ndarray with optional index values.

    Attributes:
        index: 1-dimensional array-like of length `num_steps`. Index values (x-axis).
        value: 1-dimensional array-like of length `num_steps`. Respective values (y-axis).
        dtype: Optional data type of sequence. If `None`, data type inferred
            from data.

    Example:
        >>> import numpy as np
        >>> from renumics.spotlight import Dataset, Sequence1D
        >>> index = np.arange(100)
        >>> value = np.array(np.random.rand(100))
        >>> sequence = Sequence1D(index, value)
        >>> with Dataset("docs/example.h5", "w") as dataset:
        ...     dataset.append_sequence_1d_column("sequences", 5*[sequence])
        >>> with Dataset("docs/example.h5", "r") as dataset:
        ...     print(len(dataset["sequences", 2].value))
        100
    """

    index: np.ndarray
    value: np.ndarray

    def __init__(
        self,
        index: Optional[Array1DLike],
        value: Optional[Array1DLike] = None,
        dtype: Optional[Union[str, np.dtype]] = None,
    ) -> None:
        if value is None:
            if index is None:
                raise ValueError(
                    "At least one of arguments `index` or `value` should be "
                    "set, but both `None` values received."
                )
            value = index
            index = None
        self.value = self._sanitize_data(value, dtype)
        if index is None:
            if dtype is None:
                dtype = self.value.dtype
            self.index = np.arange(len(self.value), dtype=dtype)
        else:
            self.index = self._sanitize_data(index, dtype)
        if len(self.value) != len(self.index):
            raise ValueError(
                f"Lengths of `index` and `value` should match, but lengths "
                f"{len(self.index)} and {len(self.value)} received."
            )

    @classmethod
    def decode(cls, value: Union[np.ndarray, np.void]) -> "Sequence1D":
        if not isinstance(value, np.ndarray):
            raise TypeError(
                f"`value` argument should be a numpy array, but {type(value)} "
                f"received."
            )
        if value.ndim != 2 or value.shape[1] != 2:
            raise ValueError(
                f"`value` argument should be a numpy array with shape "
                f"`(num_steps, 2)`, but shape {value.shape} received."
            )
        return cls(value[:, 0], value[:, 1])

    def encode(self, _target: Optional[str] = None) -> np.ndarray:
        return np.stack((self.index, self.value), axis=1)

    @classmethod
    def empty(cls) -> "Sequence1D":
        """
        Create an empty sequence.
        """
        return cls(np.empty(0), np.empty(0))

    @staticmethod
    def _sanitize_data(
        data: Array1DLike, dtype: Optional[Union[str, np.dtype]]
    ) -> np.ndarray:
        array = np.asarray(data, dtype)
        if array.ndim != 1:
            raise ValueError(
                f"Input values should be 1-dimensional array-likes, but shape "
                f"{array.shape} received."
            )
        if array.dtype.str[1] not in "fiu":
            raise ValueError(
                f"Input values should be array-likes with integer or float "
                f"dtype, but dtype {array.dtype.name} received."
            )
        return array


class Mesh(_BaseFileBasedData):
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

    # pylint: disable=too-many-instance-attributes

    _points: np.ndarray
    _triangles: np.ndarray
    _point_attributes: Dict[str, np.ndarray]
    _point_displacements: List[np.ndarray]

    _point_indices: np.ndarray
    _triangle_indices: np.ndarray
    _triangle_attribute_indices: np.ndarray

    def __init__(
        self,
        points: Array2DLike,
        triangles: Array2DLike,
        point_attributes: Optional[Dict[str, np.ndarray]] = None,
        triangle_attributes: Optional[Dict[str, np.ndarray]] = None,
        point_displacements: Optional[Union[np.ndarray, List[np.ndarray]]] = None,
    ):
        # pylint: disable=too-many-arguments
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
        array = triangulation.attribute_to_array(value)
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
        self, points: Array2DLike, triangles: Array2DLike
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
        self._triangles, *_ = triangulation.reindex(point_ids, self._triangles)
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


class Image(_BaseFileBasedData):
    """
    An RGB(A) or grayscale image that will be saved in encoded form.

    Attributes:
        data: Array-like with shape `(num_rows, num_columns)` or
            `(num_rows, num_columns, num_channels)` with `num_channels` equal to
            3, or 4; with dtype "uint8".

    Example:
        >>> import numpy as np
        >>> from renumics.spotlight import Dataset, Image
        >>> data = np.full([100,100,3], 255, dtype=np.uint8)  # white uint8 image
        >>> image = Image(data)
        >>> float_data = np.random.uniform(0, 1, (100, 100))  # random grayscale float image
        >>> float_image = Image(float_data)
        >>> with Dataset("docs/example.h5", "w") as dataset:
        ...     dataset.append_image_column("images", [image, float_image, data, float_data])
        >>> with Dataset("docs/example.h5", "r") as dataset:
        ...     print(dataset["images", 0].data[50][50])
        ...     print(dataset["images", 3].data.dtype)
        [255 255 255]
        uint8
    """

    data: np.ndarray

    def __init__(self, data: ImageLike) -> None:
        data_array = np.asarray(data)
        if (
            data_array.size == 0
            or data_array.ndim != 2
            and (data_array.ndim != 3 or data_array.shape[-1] not in (1, 3, 4))
        ):
            raise ValueError(
                f"`data` argument should be a numpy array with shape "
                f"`(num_rows, num_columns, num_channels)` or "
                f"`(num_rows, num_columns)` or with `num_rows > 0`, "
                f"`num_cols > 0` and `num_channels` equal to 1, 3, or 4, but "
                f"shape {data_array.shape} received."
            )
        if data_array.dtype.str[1] not in "fiu":
            raise ValueError(
                f"`data` argument should be a numpy array with integer or "
                f"float dtypes, but dtype {data_array.dtype.name} received."
            )
        if data_array.ndim == 3 and data_array.shape[2] == 1:
            data_array = data_array.squeeze(axis=2)
        if data_array.dtype.str[1] == "f":
            logger.info(
                'Image data converted to "uint8" dtype by multiplication with '
                "255 and rounding."
            )
            data_array = (255 * data_array).round()
        self.data = data_array.astype("uint8")

    @classmethod
    def from_file(cls, filepath: Union[str, os.PathLike, IO]) -> "Image":
        """
        Read image from a filepath, an URL, or a file-like object.

        `imageio` is used inside, so only supported formats are allowed.
        """
        file = str(filepath) if isinstance(filepath, os.PathLike) else filepath
        if isinstance(file, str):
            if validators.url(file):
                response = requests.get(file, headers=headers, timeout=30)
                if not response.ok:
                    raise exceptions.InvalidFile(f"URL {file} does not exist.")
                file = io.BytesIO(response.content)
            elif not os.path.isfile(file):
                raise exceptions.InvalidFile(
                    f"File {file} is neither an existing file nor an existing URL."
                )
        try:
            image_array = iio.imread(file, index=False)  # type: ignore
        except Exception as e:
            raise exceptions.InvalidFile(
                f"Image {filepath} does not exist or could not be read."
            ) from e
        return cls(image_array)

    @classmethod
    def empty(cls) -> "Image":
        """
        Create a transparent 1 x 1 image.
        """
        return cls(np.zeros((1, 1, 4), np.uint8))

    @classmethod
    def decode(cls, value: Union[np.ndarray, np.void]) -> "Image":
        if isinstance(value, np.void):
            buffer = io.BytesIO(value.tolist())
            return cls(iio.imread(buffer, extension=".png", index=False))
        raise TypeError(
            f"`value` should be a `numpy.void` instance, but {type(value)} "
            f"received."
        )

    def encode(self, _target: Optional[str] = None) -> np.void:
        buf = io.BytesIO()
        iio.imwrite(buf, self.data, extension=".png")
        return np.void(buf.getvalue())


class Audio(_BaseFileBasedData):
    """
    An Audio Signal that will be saved in encoded form.

    All formats and codecs supported by AV are supported for read.

    Attributes:
        data: Array-like with shape `(num_samples, num_channels)`
            with `num_channels` <= 5.
            If `data` has a float dtype, its values should be between -1 and 1.
            If `data` has an int dtype, its values should be between minimum and
            maximum possible values for the particular int dtype.
            If `data` has an unsigned int dtype, ist values should be between 0
            and maximum possible values for the particular unsigned int dtype.
        sampling_rate: Sampling rate (samples per seconds)

    Example:
        >>> import numpy as np
        >>> from renumics.spotlight import Dataset, Audio
        >>> samplerate = 44100
        >>> fs = 100 # 100 Hz audio signal
        >>> time = np.linspace(0.0, 1.0, samplerate)
        >>> amplitude = np.iinfo(np.int16).max * 0.4
        >>> data = np.array(amplitude * np.sin(2.0 * np.pi * fs * time), dtype=np.int16)
        >>> audio = Audio(samplerate, np.array([data, data]).T)  # int16 stereo signal
        >>> float_data = 0.5 * np.cos(2.0 * np.pi * fs * time).astype(np.float32)
        >>> float_audio = Audio(samplerate, float_data)  # float32 mono signal
        >>> with Dataset("docs/example.h5", "w") as dataset:
        ...     dataset.append_audio_column("audio", [audio, float_audio])
        ...     dataset.append_audio_column("lossy_audio", [audio, float_audio], lossy=True)
        >>> with Dataset("docs/example.h5", "r") as dataset:
        ...     print(dataset["audio", 0].data[100])
        ...     print(f"{dataset['lossy_audio', 1].data[0, 0]:.5g}")
        [12967 12967]
        0.4596
    """

    data: np.ndarray
    sampling_rate: int

    def __init__(self, sampling_rate: int, data: Array2DLike) -> None:
        data_array = np.asarray(data)
        is_valid_multi_channel = (
            data_array.size > 0 and data_array.ndim == 2 and data_array.shape[1] <= 5
        )
        is_valid_mono = data_array.size > 0 and data_array.ndim == 1
        if not (is_valid_multi_channel or is_valid_mono):
            raise ValueError(
                f"`data` argument should be a 1D array for mono data"
                f" or a 2D numpy array with shape "
                f"`(num_samples, num_channels)` and with num_channels <= 5, "
                f"but shape {data_array.shape} received."
            )
        if data_array.dtype not in [np.float32, np.int32, np.int16, np.uint8]:
            raise ValueError(
                f"`data` argument should be a numpy array with "
                f"dtype np.float32, np.int32, np.int16 or np.uint8, "
                f"but dtype {data_array.dtype.name} received."
            )
        self.data = data_array
        self.sampling_rate = sampling_rate

    @classmethod
    def from_file(cls, filepath: Union[str, os.PathLike, IO]) -> "Audio":
        """
        Read audio file from a filepath, an URL, or a file-like object.

        `pyav` is used inside, so only supported formats are allowed.
        """
        try:
            data, sampling_rate = audio.read_audio(filepath)
        except Exception as e:
            raise exceptions.InvalidFile(
                f"Audio file {filepath} does not exist or could not be read."
            ) from e
        return Audio(sampling_rate, data)

    @classmethod
    def empty(cls) -> "Audio":
        """
        Create a single zero-value sample stereo audio signal.
        """
        return cls(1, np.zeros((1, 2), np.int16))

    @classmethod
    def decode(cls, value: Union[np.ndarray, np.void]) -> "Audio":
        if isinstance(value, np.void):
            buffer = io.BytesIO(value.tolist())
            data, sampling_rate = audio.read_audio(buffer)
            return cls(sampling_rate, data)
        raise TypeError(
            f"`value` should be a `numpy.void` instance, but {type(value)} "
            f"received."
        )

    def encode(self, target: Optional[str] = None) -> np.void:
        format_, codec = self.get_format_codec(target)
        buffer = io.BytesIO()
        audio.write_audio(buffer, self.data, self.sampling_rate, format_, codec)
        return np.void(buffer.getvalue())

    @staticmethod
    def get_format_codec(target: Optional[str] = None) -> Tuple[str, str]:
        """
        Get an audio format and an audio codec by an `target`.
        """
        format_ = "wav" if target is None else target.lstrip(".").lower()
        codec = {"wav": "pcm_s16le", "ogg": "libvorbis", "mp3": "libmp3lame"}.get(
            format_, format_
        )
        return format_, codec


class Category(str):
    """
    A string value that takes only a limited number of possible values (categories).

    The corresponding categories can be got and set with get/set_column_attributes['categories'].

    Dummy class for window column creation, should not be explicitly used as
    input data.

    Example:
        >>> import numpy as np
        >>> from renumics.spotlight import Dataset
        >>> with Dataset("docs/example.h5", "w") as dataset:
        ...     dataset.append_categorical_column("my_new_cat",
        ...         categories=["red", "green", "blue"],)
        ...     dataset.append_row(my_new_cat="blue")
        ...     dataset.append_row(my_new_cat="green")
        >>> with Dataset("docs/example.h5", "r") as dataset:
        ...     print(dataset["my_new_cat", 1])
        green

    Example:
        >>> import numpy as np
        >>> import datetime
        >>> from renumics.spotlight import Dataset
        >>> with Dataset("docs/example.h5", "w") as dataset:
        ...     dataset.append_categorical_column("my_new_cat",
        ...         categories=["red", "green", "blue"],)
        ...     current_categories = dataset.get_column_attributes("my_new_cat")["categories"]
        ...     dataset.set_column_attributes("my_new_cat", categories={**current_categories,
        ...         "black":100})
        ...     dataset.append_row(my_new_cat="black")
        >>> with Dataset("docs/example.h5", "r") as dataset:
        ...     print(dataset["my_new_cat", 0])
        black
    """


class Video(_BaseFileBasedData):
    """
    A video object. No encoding or decoding is currently performed on the python
    side, so all formats will be saved into dataset without compatibility check,
    but only the formats supported by your browser (apparently .mp4, .ogg,
    .webm, .mov etc.) can be played in Spotlight.
    """

    data: bytes

    def __init__(self, data: bytes) -> None:
        if not isinstance(data, bytes):
            raise TypeError(
                f"`data` argument should be video bytes, but type {type(data)} "
                f"received."
            )
        self.data = data

    @classmethod
    def from_file(cls, filepath: PathType) -> "Video":
        """
        Read video from a filepath or an URL.
        """
        prepared_file = str(filepath) if isinstance(filepath, os.PathLike) else filepath
        if not isinstance(prepared_file, str):
            raise TypeError(
                "`filepath` should be a string or an `os.PathLike` instance, "
                f"but value {prepared_file} or type {type(prepared_file)} "
                f"received."
            )
        if validators.url(prepared_file):
            response = requests.get(
                prepared_file, headers=headers, stream=True, timeout=10
            )
            if not response.ok:
                raise exceptions.InvalidFile(f"URL {prepared_file} does not exist.")
            return cls(response.raw.data)
        if os.path.isfile(prepared_file):
            with open(filepath, "rb") as f:
                return cls(f.read())
        raise exceptions.InvalidFile(
            f"File {prepared_file} is neither an existing file nor an existing URL."
        )

    @classmethod
    def empty(cls) -> "Video":
        """
        Create an empty video instance.
        """
        return cls(b"\x00")

    @classmethod
    def decode(cls, value: Union[np.ndarray, np.void]) -> "Video":
        if isinstance(value, np.void):
            return cls(value.tolist())
        raise TypeError(
            f"`value` should be a `numpy.void` instance, but {type(value)} "
            f"received."
        )

    def encode(self, _target: Optional[str] = None) -> np.void:
        return np.void(self.data)


class Window:
    # pylint: disable=too-few-public-methods
    """
    A pair of two timestamps in seconds which can be later projected onto
    continuous data (only :class:`Audio <renumics.spotlight.dtypes.Audio>`
    is currently supported).

    Dummy class for window column creation
    (see :func:`Dataset.append_column <renumics.spotlight.dataset.Dataset.append_column>`),
    should not be explicitly used as input data.

    To create a window column, use
    :func:`Dataset.append_window_column <renumics.spotlight.dataset.Dataset.append_window_column>`
    method.

    Examples:

        >>> import numpy as np
        >>> from renumics.spotlight import Dataset
        >>> with Dataset("docs/example.h5", "w") as dataset:
        ...     dataset.append_window_column("window", [[1, 2]] * 4)
        ...     dataset.append_row(window=(0, 1))
        ...     dataset.append_row(window=np.array([-1, 0]))
        >>> with Dataset("docs/example.h5", "r") as dataset:
        ...     print(dataset["window"])
        [[ 1.  2.]
         [ 1.  2.]
         [ 1.  2.]
         [ 1.  2.]
         [ 0.  1.]
         [-1.  0.]]


        >>> import numpy as np
        >>> from renumics.spotlight import Dataset
        >>> with Dataset("docs/example.h5", "w") as dataset:
        ...     dataset.append_int_column("start", range(5))
        ...     dataset.append_float_column("end", dataset["start"] + 2)
        ...     print(dataset["start"])
        ...     print(dataset["end"])
        [0 1 2 3 4]
        [2. 3. 4. 5. 6.]
        >>> with Dataset("docs/example.h5", "a") as dataset:
        ...     dataset.append_window_column("window", zip(dataset["start"], dataset["end"]))
        >>> with Dataset("docs/example.h5", "r") as dataset:
        ...     print(dataset["window"])
        [[0. 2.]
         [1. 3.]
         [2. 4.]
         [3. 5.]
         [4. 6.]]
    """
