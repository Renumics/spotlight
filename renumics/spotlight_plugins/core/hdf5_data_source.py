"""
access h5 table data
"""
from hashlib import sha1
from pathlib import Path
from typing import List, Union, cast

import h5py
import numpy as np

from renumics.spotlight.dtypes import Embedding
from renumics.spotlight.typing import IndexType
from renumics.spotlight.dataset import Dataset, INTERNAL_COLUMN_NAMES

from renumics.spotlight.data_source import DataSource, datasource
from renumics.spotlight.backend.exceptions import (
    NoTableFileFound,
    CouldNotOpenTableFile,
)
from renumics.spotlight.dtypes.conversion import NormalizedValue
from renumics.spotlight.data_source.data_source import ColumnMetadata
from renumics.spotlight.dtypes.v2 import DTypeMap, create_dtype


class H5Dataset(Dataset):
    """
    A `spotlight.Dataset` class extension for better usage in Spotlight backend.
    """

    def get_generation_id(self) -> int:
        """
        Get the dataset's generation if set.
        """
        return int(self._h5_file.attrs.get("spotlight_generation_id", 0))

    def read_value(self, column_name: str, index: IndexType) -> NormalizedValue:
        """
        Get a dataset value as it is stored in the H5 dataset, resolve references.
        """

        self._assert_column_exists(column_name, internal=True)
        self._assert_index_exists(index)
        column = cast(h5py.Dataset, self._h5_file[column_name])
        value = column[index]
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        if self._is_ref_column(column):
            if value:
                value = self._resolve_ref(value, column_name)[()]
                return value.tolist() if isinstance(value, np.void) else value
            return None
        if self._get_column_type(column.attrs) is Embedding and len(value) == 0:
            return None
        return value

    def read_column(
        self,
        column_name: str,
        indices: Union[List[int], np.ndarray, slice] = slice(None),
    ) -> np.ndarray:
        """
        Get a decoded dataset column.
        """
        self._assert_column_exists(column_name, internal=True)

        column = cast(h5py.Dataset, self._h5_file[column_name])
        is_string_dtype = h5py.check_string_dtype(column.dtype)

        raw_values = column[indices]

        if is_string_dtype:
            raw_values = np.array([x.decode("utf-8") for x in raw_values])

        if self._is_ref_column(column):
            assert is_string_dtype, "Only new-style string h5 references supported."
            normalized_values = np.empty(len(raw_values), dtype=object)
            normalized_values[:] = [
                value.tolist() if isinstance(value, np.void) else value
                for value in self._resolve_refs(raw_values, column_name)
            ]
            return normalized_values
        if self._get_column_type(column.attrs) is Embedding:
            normalized_values = np.empty(len(raw_values), dtype=object)
            normalized_values[:] = [None if len(x) == 0 else x for x in raw_values]
            return normalized_values
        return raw_values

    def duplicate_row(self, from_index: IndexType, to_index: IndexType) -> None:
        """
        Duplicate a dataset's row. Increases the dataset's length by 1.
        """
        self._assert_is_writable()
        self._assert_index_exists(from_index)
        length = self._length
        if from_index < 0:
            from_index += length
        if to_index < 0:
            to_index += length
        if to_index != length:
            self._assert_index_exists(to_index)
        for column_name in self.keys() + INTERNAL_COLUMN_NAMES:
            column = cast(h5py.Dataset, self._h5_file[column_name])
            column.resize(length + 1, axis=0)
            if to_index != length:
                # Shift all values after the insertion position by one.
                raw_values = column[int(to_index) : -1]
                if self._get_column_type(column) is Embedding:
                    raw_values = list(raw_values)
                column[int(to_index) + 1 :] = raw_values
            column[int(to_index)] = column[from_index]
        self._length += 1
        self._update_generation_id()

    def _resolve_refs(self, refs: np.ndarray, column_name: str) -> np.ndarray:
        raw_values = np.empty(len(refs), dtype=object)
        raw_values[:] = [
            self._resolve_ref(ref, column_name)[()] if ref else None for ref in refs
        ]
        return raw_values


@datasource(".h5")
class Hdf5DataSource(DataSource):
    """
    access h5 table data
    """

    def __init__(self, source: Path):
        self._path = source
        self._open()

    def __getstate__(self) -> dict:
        return {
            "path": self._path,
        }

    def __setstate__(self, state: dict) -> None:
        self._path = state["path"]
        self._open()

    def _open(self) -> None:
        self._table = H5Dataset(self._path, "r")
        try:
            self._table.open()
        except FileNotFoundError as e:
            raise NoTableFileFound(self._path) from e
        except OSError as e:
            raise CouldNotOpenTableFile(self._path) from e

    def __del__(self) -> None:
        self._table.close()

    @property
    def column_names(self) -> List[str]:
        return self._table.keys()

    def __len__(self) -> int:
        return len(self._table)

    def guess_dtypes(self) -> DTypeMap:
        return {
            column_name: create_dtype(self._table.get_column_type(column_name))
            for column_name in self.column_names
        }

    def get_generation_id(self) -> int:
        return self._table.get_generation_id()

    def get_uid(self) -> str:
        return sha1(str(self._path.absolute()).encode("utf-8")).hexdigest()

    def get_name(self) -> str:
        return str(self._path.name)

    def get_column_metadata(self, column_name: str) -> ColumnMetadata:
        attributes = cast(dict, self._table.get_column_attributes(column_name))
        return ColumnMetadata(
            nullable=attributes.get("optional", False),
            editable=attributes.get("editable", True),
            description=attributes.get("description"),
            tags=attributes.get("tags", []),
        )

    def get_column_values(
        self,
        column_name: str,
        indices: Union[List[int], np.ndarray, slice] = slice(None),
    ) -> np.ndarray:
        return self._table.read_column(column_name, indices=indices)
