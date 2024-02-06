"""
access h5 table data
"""

from hashlib import sha1
from pathlib import Path
from typing import Iterable, List, Union, cast

import h5py
import numpy as np

from renumics.spotlight import dtypes
from renumics.spotlight.backend.exceptions import (
    CouldNotOpenTableFile,
    H5DatasetOutdated,
    NoTableFileFound,
)
from renumics.spotlight.data_source import DataSource, datasource
from renumics.spotlight.data_source.data_source import ColumnMetadata
from renumics.spotlight.dataset import Dataset


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
        self._table = Dataset(self._path, "r")
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
    def intermediate_dtypes(self) -> dtypes.DTypeMap:
        return self.semantic_dtypes

    def __len__(self) -> int:
        return len(self._table)

    @property
    def semantic_dtypes(self) -> dtypes.DTypeMap:
        return {
            column_name: dtypes.create_dtype(self._table.get_dtype(column_name))
            for column_name in self.column_names
        }

    def get_generation_id(self) -> int:
        return int(self._table._h5_file.attrs.get("spotlight_generation_id", 0))

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
    ) -> Iterable:
        self._table._assert_column_exists(column_name, internal=True)

        column = cast(h5py.Dataset, self._table._h5_file[column_name])
        dtype = self._table._get_dtype(column)
        is_string_dtype = h5py.check_string_dtype(column.dtype)

        raw_values = column[indices]

        if is_string_dtype:
            raw_values = np.array([x.decode("utf-8") for x in raw_values])

        if self._table._is_ref_column(column):
            if column.attrs.get("external", False):
                yield from raw_values
            elif is_string_dtype:
                for ref in raw_values:
                    if not ref:
                        yield None
                    else:
                        value = self._table._resolve_ref(ref, column_name)[()]
                        yield value.tolist() if isinstance(value, np.void) else value
            else:
                raise H5DatasetOutdated()
        elif dtypes.is_window_dtype(dtype) or dtypes.is_bounding_box_dtype(dtype):
            for x in raw_values:
                yield None if np.isnan(x).all() else x
        elif dtypes.is_embedding_dtype(dtype):
            for x in raw_values:
                yield None if len(x) == 0 else x
        else:
            yield from raw_values
