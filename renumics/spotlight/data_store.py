import hashlib
import io
import os
import statistics
from typing import Any, List, Optional, Set, Union, cast
import numpy as np
import filetype
import trimesh
import PIL.Image

from renumics.spotlight.cache import external_data_cache
from renumics.spotlight.data_source import DataSource
from renumics.spotlight.dtypes.conversion import ConvertedValue, convert_to_dtype
from renumics.spotlight.data_source.data_source import ColumnMetadata
from renumics.spotlight.io import audio
from renumics.spotlight.dtypes import (
    ArrayDType,
    CategoryDType,
    DType,
    DTypeMap,
    EmbeddingDType,
    is_array_dtype,
    is_audio_dtype,
    is_category_dtype,
    is_file_dtype,
    is_str_dtype,
    is_mixed_dtype,
    is_bytes_dtype,
    str_dtype,
    audio_dtype,
    image_dtype,
    video_dtype,
    mesh_dtype,
    embedding_dtype,
    window_dtype,
    sequence_1d_dtype,
)

from renumics.spotlight.typing import is_iterable, is_pathtype
from renumics.spotlight.media.mesh import Mesh
from renumics.spotlight.media.video import Video
from renumics.spotlight.media.audio import Audio
from renumics.spotlight.media.image import Image
from renumics.spotlight.media.sequence_1d import Sequence1D
from renumics.spotlight.media.embedding import Embedding


class DataStore:
    _data_source: DataSource
    _user_dtypes: DTypeMap
    _dtypes: DTypeMap

    def __init__(self, data_source: DataSource, user_dtypes: DTypeMap) -> None:
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
        return self._data_source.column_names

    @property
    def data_source(self) -> DataSource:
        return self._data_source

    @property
    def dtypes(self) -> DTypeMap:
        return self._dtypes

    def check_generation_id(self, generation_id: int) -> None:
        self._data_source.check_generation_id(generation_id)

    def get_column_metadata(self, column_name: str) -> ColumnMetadata:
        return self._data_source.get_column_metadata(column_name)

    def get_converted_values(
        self,
        column_name: str,
        indices: Union[List[int], np.ndarray, slice] = slice(None),
        simple: bool = False,
        check: bool = True,
    ) -> List[ConvertedValue]:
        dtype = self._dtypes[column_name]
        normalized_values = self._data_source.get_column_values(column_name, indices)
        converted_values = [
            convert_to_dtype(value, dtype, simple=simple, check=check)
            for value in normalized_values
        ]
        return converted_values

    def get_converted_value(
        self, column_name: str, index: int, simple: bool = False
    ) -> ConvertedValue:
        return self.get_converted_values(column_name, indices=[index], simple=simple)[0]

    def get_waveform(self, column_name: str, index: int) -> Optional[np.ndarray]:
        """
        return the waveform of an audio cell
        """
        assert is_audio_dtype(self._dtypes[column_name])

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
                is_category_dtype(dtype)
                and dtype.categories is None
                and is_str_dtype(guessed_dtypes[column_name])
            ):
                normalized_values = self._data_source.get_column_values(column_name)
                converted_values = [
                    convert_to_dtype(value, str_dtype, simple=True, check=True)
                    for value in normalized_values
                ]
                category_names = sorted(cast(Set[str], set(converted_values)))
                dtypes[column_name] = CategoryDType(category_names)

        self._dtypes = dtypes

    def _guess_dtype(self, col: str) -> DType:
        intermediate_dtype = self._data_source.intermediate_dtypes[col]
        semantic_dtype = _intermediate_to_semantic_dtype(intermediate_dtype)

        if is_array_dtype(intermediate_dtype):
            return semantic_dtype

        sample_values = self._data_source.get_column_values(col, slice(10))
        sample_dtypes = [_guess_value_dtype(value) for value in sample_values]

        try:
            mode_dtype = statistics.mode(sample_dtypes)
        except statistics.StatisticsError:
            return semantic_dtype

        return mode_dtype or semantic_dtype


def _intermediate_to_semantic_dtype(intermediate_dtype: DType) -> DType:
    if is_array_dtype(intermediate_dtype):
        if intermediate_dtype.shape is None:
            return intermediate_dtype
        if intermediate_dtype.shape == (2,):
            return window_dtype
        if intermediate_dtype.ndim == 1 and intermediate_dtype.shape[0] is not None:
            return EmbeddingDType(intermediate_dtype.shape[0])
        if intermediate_dtype.ndim == 1 and intermediate_dtype.shape[0] is None:
            return sequence_1d_dtype
        if intermediate_dtype.ndim == 2 and (
            intermediate_dtype.shape[0] == 2 or intermediate_dtype.shape[1] == 2
        ):
            return sequence_1d_dtype
        if intermediate_dtype.ndim == 3 and intermediate_dtype.shape[-1] in (1, 3, 4):
            return image_dtype
        return intermediate_dtype
    if is_file_dtype(intermediate_dtype):
        return str_dtype
    if is_mixed_dtype(intermediate_dtype):
        return str_dtype
    if is_bytes_dtype(intermediate_dtype):
        return str_dtype
    else:
        return intermediate_dtype


def _guess_value_dtype(value: Any) -> Optional[DType]:
    """
    Infer dtype for value
    """
    if isinstance(value, Embedding):
        return embedding_dtype
    if isinstance(value, Sequence1D):
        return sequence_1d_dtype
    if isinstance(value, Image):
        return image_dtype
    if isinstance(value, Audio):
        return audio_dtype
    if isinstance(value, Video):
        return video_dtype
    if isinstance(value, Mesh):
        return mesh_dtype
    if isinstance(value, PIL.Image.Image):
        return image_dtype
    if isinstance(value, trimesh.Trimesh):
        return mesh_dtype
    if isinstance(value, np.ndarray):
        return ArrayDType(value.shape)

    if isinstance(value, bytes) or (is_pathtype(value) and os.path.isfile(value)):
        kind = filetype.guess(value)
        if kind is not None:
            mime_group = kind.mime.split("/")[0]
            if mime_group == "image":
                return image_dtype
            if mime_group == "audio":
                return audio_dtype
            if mime_group == "video":
                return video_dtype
        return str_dtype
    if is_iterable(value):
        try:
            value = np.asarray(value, dtype=float)
        except (TypeError, ValueError):
            pass
        else:
            return ArrayDType(value.shape)
    return None
