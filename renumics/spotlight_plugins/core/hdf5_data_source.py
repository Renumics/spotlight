"""
access h5 table data
"""
from hashlib import sha1
from pathlib import Path
from typing import List, Union, cast

import h5py
import numpy as np

from renumics.spotlight.dataset import Dataset

from renumics.spotlight.data_source import DataSource, datasource
from renumics.spotlight.backend.exceptions import (
    NoTableFileFound,
    CouldNotOpenTableFile,
)
from renumics.spotlight.data_source.data_source import ColumnMetadata
from renumics.spotlight.dtypes import DTypeMap, create_dtype, is_embedding_dtype


class H5Dataset(Dataset):
    """
    A `spotlight.Dataset` class extension for better usage in Spotlight backend.
    """

    def get_generation_id(self) -> int:
        """
        Get the dataset's generation if set.
        """
        return int(self._h5_file.attrs.get("spotlight_generation_id", 0))

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
        if is_embedding_dtype(self._get_dtype(column)):
            normalized_values = np.empty(len(raw_values), dtype=object)
            normalized_values[:] = [None if len(x) == 0 else x for x in raw_values]
            return normalized_values
        return raw_values

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
        column_names = self._table.keys()
        orders = {
            name: self._table.get_column_attributes(name).get("order") or -1
            for name in column_names
        }
        column_names.sort(key=lambda name: orders[name], reverse=True)
        return column_names

    @property
    def intermediate_dtypes(self) -> DTypeMap:
        return self.semantic_dtypes

    def __len__(self) -> int:
        return len(self._table)

    @property
    def semantic_dtypes(self) -> DTypeMap:
        return {
            column_name: create_dtype(self._table.get_dtype(column_name))
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
            hidden=attributes.get("hidden", False),
            description=attributes.get("description"),
            tags=attributes.get("tags", []),
        )

    def get_column_values(
        self,
        column_name: str,
        indices: Union[List[int], np.ndarray, slice] = slice(None),
    ) -> np.ndarray:
        return self._table.read_column(column_name, indices=indices)
