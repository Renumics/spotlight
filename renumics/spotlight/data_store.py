import hashlib
import io
from typing import List, Optional, Set, Union, cast
import numpy as np

from renumics.spotlight.cache import external_data_cache
from renumics.spotlight.data_source import DataSource
from renumics.spotlight.dtypes.conversion import ConvertedValue, convert_to_dtype
from renumics.spotlight.data_source.data_source import ColumnMetadata
from renumics.spotlight.io import audio
from renumics.spotlight.dtypes import (
    CategoryDType,
    DTypeMap,
    is_audio_dtype,
    is_category_dtype,
    is_str_dtype,
    str_dtype,
)


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
        guessed_dtypes = self._data_source.guess_dtypes()
        dtypes = {
            **guessed_dtypes,
            **{
                column_name: dtype
                for column_name, dtype in self._user_dtypes.items()
                if column_name in guessed_dtypes
            },
        }
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
