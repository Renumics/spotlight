import hashlib
import io
from typing import List, Optional, Union
import numpy as np

from renumics.spotlight.cache import external_data_cache
from renumics.spotlight.dtypes.typing import ColumnTypeMapping
from renumics.spotlight.data_source import DataSource
from renumics.spotlight.dtypes import Audio, Category
from renumics.spotlight.dtypes.conversion import (
    ConvertedValue,
    DTypeOptions,
    convert_to_dtype,
)
from renumics.spotlight.data_source.data_source import ColumnMetadata

from renumics.spotlight.io import audio


class DataStore:
    _dtypes: ColumnTypeMapping
    _data_source: DataSource

    def __init__(self, data_source: DataSource, user_dtypes: ColumnTypeMapping) -> None:
        self._data_source = data_source
        dtypes = self._data_source.guess_dtypes()
        dtypes.update(
            {
                column_name: column_type
                for column_name, column_type in user_dtypes.items()
                if column_name in dtypes
            }
        )
        self._dtypes = dtypes

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
    def dtypes(self) -> ColumnTypeMapping:
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
    ) -> List[ConvertedValue]:
        dtype = self._dtypes[column_name]
        normalized_values = self._data_source.get_column_values(column_name, indices)
        if dtype is Category:
            dtype_options = DTypeOptions(
                categories=self._data_source.get_column_categories(column_name)
            )
        else:
            dtype_options = DTypeOptions()
        converted_values = [
            convert_to_dtype(value, dtype, dtype_options=dtype_options, simple=simple)
            for value in normalized_values
        ]
        return converted_values

    def get_converted_value(
        self, column_name: str, index: int, simple: bool = False
    ) -> ConvertedValue:
        dtype = self._dtypes[column_name]
        normalized_value = self._data_source.get_cell_value(column_name, index)

        if dtype is Category:
            dtype_options = DTypeOptions(
                categories=self._data_source.get_column_categories(column_name)
            )
        else:
            dtype_options = DTypeOptions()

        converted_value = convert_to_dtype(
            normalized_value, dtype=dtype, dtype_options=dtype_options, simple=simple
        )
        return converted_value

    def get_waveform(self, column_name: str, index: int) -> Optional[np.ndarray]:
        """
        return the waveform of an audio cell
        """
        assert self._dtypes[column_name] is Audio

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
