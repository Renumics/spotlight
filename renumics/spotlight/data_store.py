import datetime
import hashlib
import io
import os
import statistics
from typing import Any, Dict, Iterable, List, Optional, Set, Union, cast

import filetype
import numpy as np
import PIL.Image
import requests
import trimesh
import validators

import renumics.spotlight.dtypes as spotlight_dtypes
from renumics.spotlight.backend.exceptions import ComputedColumnNotReady
from renumics.spotlight.cache import external_data_cache
from renumics.spotlight.data_source import DataSource
from renumics.spotlight.data_source.data_source import ColumnMetadata
from renumics.spotlight.dtypes.conversion import ConvertedValue, convert_to_dtype
from renumics.spotlight.io import audio
from renumics.spotlight.media.audio import Audio
from renumics.spotlight.media.embedding import Embedding
from renumics.spotlight.media.image import Image
from renumics.spotlight.media.mesh import Mesh
from renumics.spotlight.media.sequence_1d import Sequence1D
from renumics.spotlight.media.video import Video
from renumics.spotlight.typing import is_iterable, is_pathtype


class DataStore:
    _data_source: DataSource
    _user_dtypes: spotlight_dtypes.DTypeMap
    _dtypes: spotlight_dtypes.DTypeMap
    _embeddings: Dict[str, Optional[np.ndarray]]

    def __init__(
        self, data_source: DataSource, user_dtypes: spotlight_dtypes.DTypeMap
    ) -> None:
        self._embeddings = {}
        self._data_source = data_source
        self._user_dtypes = user_dtypes
        self._update_dtypes()

    def __len__(self) -> int:
        return len(self._data_source)

    @property
    def uid(self) -> str:
        return self._data_source.get_uid()

    @property
    def name(self) -> str:
        return self._data_source.get_name()

    @property
    def generation_id(self) -> int:
        return self._data_source.get_generation_id()

    @property
    def column_names(self) -> List[str]:
        return self._data_source.column_names + list(self._embeddings)

    @property
    def data_source(self) -> DataSource:
        return self._data_source

    @property
    def dtypes(self) -> spotlight_dtypes.DTypeMap:
        dtypes_ = self._dtypes.copy()
        for column, embeddings in self._embeddings.items():
            if embeddings is None:
                length = None
            else:
                try:
                    length = len(
                        next(
                            embedding
                            for embedding in embeddings
                            if embedding is not None
                        )
                    )
                except StopIteration:
                    length = None
            dtypes_[column] = spotlight_dtypes.EmbeddingDType(length=length)
        return dtypes_

    @property
    def embeddings(self) -> Dict[str, Optional[np.ndarray]]:
        return self._embeddings

    @embeddings.setter
    def embeddings(self, new_embeddings: Dict[str, Optional[np.ndarray]]) -> None:
        self._embeddings = new_embeddings

    def check_generation_id(self, generation_id: int) -> None:
        self._data_source.check_generation_id(generation_id)

    def get_column_metadata(self, column_name: str) -> ColumnMetadata:
        if column_name in self._embeddings:
            return ColumnMetadata(
                nullable=True,
                editable=False,
                hidden=True,
                description=None,
                tags=[],
                computed=True,
            )
        return self._data_source.get_column_metadata(column_name)

    def get_converted_values(
        self,
        column_name: str,
        indices: Union[List[int], np.ndarray, slice] = slice(None),
        simple: bool = False,
        check: bool = True,
    ) -> List[ConvertedValue]:
        dtype = self.dtypes[column_name]
        if column_name in self._embeddings:
            embeddings = self._embeddings[column_name]
            if embeddings is None:
                raise ComputedColumnNotReady(column_name)
            normalized_values: Iterable = embeddings[indices]
        else:
            normalized_values = self._data_source.get_column_values(
                column_name, indices
            )
        converted_values = [
            convert_to_dtype(value, dtype, simple=simple, check=check)
            for value in normalized_values
        ]
        return converted_values

    def get_converted_value(
        self, column_name: str, index: int, simple: bool = False, check: bool = True
    ) -> ConvertedValue:
        return self.get_converted_values(
            column_name, indices=[index], simple=simple, check=check
        )[0]

    def get_waveform(self, column_name: str, index: int) -> Optional[np.ndarray]:
        """
        return the waveform of an audio cell
        """
        assert spotlight_dtypes.is_audio_dtype(self._dtypes[column_name])

        blob = self.get_converted_value(column_name, index, simple=False)
        if blob is None:
            return None
        value_hash = hashlib.blake2b(blob).hexdigest()  # type: ignore
        cache_key = f"waveform-v2:{value_hash}"
        try:
            waveform = external_data_cache[cache_key]
            return waveform
        except KeyError:
            ...
        waveform = audio.get_waveform(io.BytesIO(blob))  # type: ignore
        external_data_cache[cache_key] = waveform
        return waveform

    def _update_dtypes(self) -> None:
        guessed_dtypes = self._data_source.semantic_dtypes.copy()

        # guess missing dtypes from intermediate dtypes
        for col, dtype in self._data_source.intermediate_dtypes.items():
            if col not in guessed_dtypes:
                guessed_dtypes[col] = self._guess_dtype(col)

        # merge guessed semantic dtypes with user dtypes
        dtypes = {
            **guessed_dtypes,
            **{
                column_name: dtype
                for column_name, dtype in self._user_dtypes.items()
                if column_name in guessed_dtypes
            },
        }

        # determine categories for _automatic_ CategoryDtypes
        for column_name, dtype in dtypes.items():
            if (
                spotlight_dtypes.is_category_dtype(dtype)
                and dtype.categories is None
                and spotlight_dtypes.is_str_dtype(guessed_dtypes[column_name])
            ):
                normalized_values = self._data_source.get_column_values(column_name)
                converted_values = [
                    convert_to_dtype(
                        value, spotlight_dtypes.str_dtype, simple=True, check=True
                    )
                    for value in normalized_values
                ]
                category_names = sorted(cast(Set[str], set(converted_values)))
                dtypes[column_name] = spotlight_dtypes.CategoryDType(category_names)

        self._dtypes = dtypes

    def _guess_dtype(self, col: str) -> spotlight_dtypes.DType:
        intermediate_dtype = self._data_source.intermediate_dtypes[col]
        semantic_dtype = _guess_dtype_from_intermediate(intermediate_dtype)

        if semantic_dtype is not None:
            return semantic_dtype

        sample_values = self._data_source.get_column_values(col, slice(10))
        sample_dtype = _guess_dtype_from_values(sample_values)
        return sample_dtype or spotlight_dtypes.str_dtype


def _guess_dtype_from_values(values: Iterable) -> Optional[spotlight_dtypes.DType]:
    dtypes: List[spotlight_dtypes.DType] = []
    for value in values:
        guessed_dtype = _guess_value_dtype(value)
        if guessed_dtype is not None:
            dtypes.append(guessed_dtype)
    if not dtypes:
        return None

    mode_dtype = statistics.mode(dtypes)

    if (
        spotlight_dtypes.is_window_dtype(mode_dtype)
        or spotlight_dtypes.is_bounding_box_dtype(mode_dtype)
        or spotlight_dtypes.is_embedding_dtype(mode_dtype)
    ):
        if any(dtype != mode_dtype for dtype in dtypes):
            return spotlight_dtypes.array_dtype
    return mode_dtype


def _guess_dtype_from_intermediate(
    intermediate_dtype: spotlight_dtypes.DType,
) -> Optional[spotlight_dtypes.DType]:
    if spotlight_dtypes.is_bool_dtype(intermediate_dtype):
        return intermediate_dtype
    if spotlight_dtypes.is_int_dtype(intermediate_dtype):
        return intermediate_dtype
    if spotlight_dtypes.is_float_dtype(intermediate_dtype):
        return intermediate_dtype
    if spotlight_dtypes.is_datetime_dtype(intermediate_dtype):
        return intermediate_dtype
    if spotlight_dtypes.is_category_dtype(intermediate_dtype):
        return intermediate_dtype
    if spotlight_dtypes.is_window_dtype(intermediate_dtype):
        return intermediate_dtype
    if spotlight_dtypes.is_bounding_box_dtype(intermediate_dtype):
        return intermediate_dtype
    if spotlight_dtypes.is_bounding_boxes_dtype(intermediate_dtype):
        return intermediate_dtype
    if spotlight_dtypes.is_embedding_dtype(intermediate_dtype):
        return intermediate_dtype
    if spotlight_dtypes.is_sequence_1d_dtype(intermediate_dtype):
        return intermediate_dtype
    if spotlight_dtypes.is_audio_dtype(intermediate_dtype):
        return intermediate_dtype
    if spotlight_dtypes.is_image_dtype(intermediate_dtype):
        return intermediate_dtype
    if spotlight_dtypes.is_mesh_dtype(intermediate_dtype):
        return intermediate_dtype
    if spotlight_dtypes.is_video_dtype(intermediate_dtype):
        return intermediate_dtype
    if spotlight_dtypes.is_array_dtype(intermediate_dtype):
        return _guess_array_dtype(intermediate_dtype)
    if spotlight_dtypes.is_sequence_dtype(intermediate_dtype):
        inner_dtype = intermediate_dtype.dtype
        if spotlight_dtypes.SequenceDType.is_supported_inner_dtype(inner_dtype):
            return intermediate_dtype
        return spotlight_dtypes.str_dtype
    return None


def _guess_value_dtype(value: Any) -> Optional[spotlight_dtypes.DType]:
    """
    Infer dtype for value
    """
    if isinstance(value, bool):
        return spotlight_dtypes.bool_dtype
    if isinstance(value, int):
        return spotlight_dtypes.int_dtype
    if isinstance(value, float):
        return spotlight_dtypes.float_dtype
    if isinstance(value, (datetime.datetime, np.datetime64)):
        return spotlight_dtypes.datetime_dtype
    if isinstance(value, Embedding):
        return spotlight_dtypes.embedding_dtype
    if isinstance(value, Sequence1D):
        return spotlight_dtypes.sequence_1d_dtype
    if isinstance(value, Image):
        return spotlight_dtypes.image_dtype
    if isinstance(value, Audio):
        return spotlight_dtypes.audio_dtype
    if isinstance(value, Video):
        return spotlight_dtypes.video_dtype
    if isinstance(value, Mesh):
        return spotlight_dtypes.mesh_dtype
    if isinstance(value, PIL.Image.Image):
        return spotlight_dtypes.image_dtype
    if isinstance(value, trimesh.Trimesh):
        return spotlight_dtypes.mesh_dtype

    if isinstance(value, bytes) or is_pathtype(value):
        mimetype: Optional[str] = None
        if isinstance(value, bytes) or (is_pathtype(value) and os.path.isfile(value)):
            kind = filetype.guess(value)
            if kind is not None:
                mimetype = kind.mime
        elif isinstance(value, str) and validators.url(value):
            try:
                response = requests.head(value, timeout=1)
            except requests.ReadTimeout:
                ...
            else:
                if response.ok:
                    mimetype = response.headers.get("Content-Type")
        if mimetype is not None:
            mime_group = mimetype.split("/")[0]
            if mime_group == "image":
                return spotlight_dtypes.image_dtype
            if mime_group == "audio":
                return spotlight_dtypes.audio_dtype
            if mime_group == "video":
                return spotlight_dtypes.video_dtype
        return spotlight_dtypes.str_dtype
    if is_iterable(value):
        if isinstance(value, np.ndarray) and value.dtype.str in "fiu":
            # Array is float-compatible.
            return _guess_array_dtype(spotlight_dtypes.ArrayDType(value.shape))
        try:
            value = np.asarray(value, dtype=float)
        except (TypeError, ValueError):
            pass
        else:
            return _guess_array_dtype(spotlight_dtypes.ArrayDType(value.shape))
        inner_dtype = _guess_dtype_from_values(value)
        if (
            inner_dtype is not None
            and spotlight_dtypes.SequenceDType.is_supported_inner_dtype(inner_dtype)
        ):
            return spotlight_dtypes.SequenceDType(inner_dtype)
        return None
    return None


def _guess_array_dtype(
    dtype: spotlight_dtypes.ArrayDType,
) -> Optional[spotlight_dtypes.DType]:
    if dtype.shape is None:
        return None
    if dtype.ndim == 1:
        length = dtype.shape[0]
        if length == 2:
            return spotlight_dtypes.window_dtype
        if length == 4:
            return spotlight_dtypes.bounding_box_dtype
        if length is not None:
            return spotlight_dtypes.EmbeddingDType(length)
        return spotlight_dtypes.sequence_1d_dtype
    if dtype.ndim == 2:
        if dtype.shape[1] == 2:  # (n, 2)
            return spotlight_dtypes.SequenceDType(
                spotlight_dtypes.window_dtype, dtype.shape[0]
            )
        if dtype.shape[1] == 4:  # (n, 4)
            return spotlight_dtypes.SequenceDType(
                spotlight_dtypes.bounding_box_dtype, dtype.shape[0]
            )
        if dtype.shape[0] == 2:  # (2, n)
            return spotlight_dtypes.sequence_1d_dtype
    if dtype.ndim == 3 and dtype.shape[-1] in (1, 3, 4):
        return spotlight_dtypes.image_dtype
    if all(dim is None for dim in dtype.shape):
        return None
    return dtype
