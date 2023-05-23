"""
access h5 table data
"""
import os
from hashlib import sha1
from pathlib import Path
from typing import Any, Dict, List, Optional, cast, Union, Type
from dataclasses import asdict

import h5py
import numpy as np

from renumics.spotlight.dtypes import Category, Embedding
from renumics.spotlight.dtypes.typing import (
    ColumnTypeMapping,
    get_column_type,
    FileBasedColumnType,
)
from renumics.spotlight.typing import PathType, IndexType
from renumics.spotlight.dataset import (
    Dataset,
    INTERNAL_COLUMN_NAMES,
    unescape_dataset_name,
)

from renumics.spotlight.backend.data_source import (
    DataSource,
    Attrs,
    Column,
    read_external_value,
)
from renumics.spotlight.backend.exceptions import (
    NoTableFileFound,
    CouldNotOpenTableFile,
    NoRowFound,
    InvalidExternalData,
)

from renumics.spotlight.backend import datasource


def unescape_dataset_names(refs: np.ndarray) -> np.ndarray:
    """
    Unescape multiple dataset names.
    """
    return np.array([unescape_dataset_name(value) for value in refs])


def decode_attrs(raw_attrs: h5py.AttributeManager) -> Attrs:
    """
    Get relevant subset of column attributes.
    """
    column_type_name = raw_attrs.get("type", "unknown")
    column_type = get_column_type(column_type_name)

    categories: Optional[Dict[str, int]] = None
    embedding_length: Optional[int] = None

    if column_type is Category:
        # If one of the attributes does not exist or is empty, an empty dict
        # will be created.
        categories = dict(
            zip(
                raw_attrs.get("category_keys", []),
                raw_attrs.get("category_values", []),
            )
        )
    elif column_type is Embedding:
        embedding_length = raw_attrs.get("value_shape", [0])[0]

    tags: List[str] = []
    if "tags" in raw_attrs:
        tags = raw_attrs["tags"].tolist()

    return Attrs(
        type_name=column_type_name,
        type=column_type,
        order=raw_attrs.get("order", None),
        hidden=raw_attrs.get("hidden", False),
        optional=raw_attrs.get("optional", False),
        description=raw_attrs.get("description", None),
        tags=tags,
        editable=raw_attrs.get("editable", False),
        categories=categories,
        x_label=raw_attrs.get("x_label", None),
        y_label=raw_attrs.get("y_label", None),
        embedding_length=embedding_length,
        has_lookup="lookup_keys" in raw_attrs,
        is_external=raw_attrs.get("external", False),
    )


def ref_placeholder_names(mask: np.ndarray) -> np.ndarray:
    """
    Generate placeholder names for a ref column based of the given mask.
    """
    return np.array(["..." if x else None for x in mask], dtype=object)


class H5Dataset(Dataset):
    """
    A `spotlight.Dataset` class extension for better usage in Spotlight backend.
    """

    def __enter__(self) -> "H5Dataset":
        self.open()
        return self

    def get_generation_id(self) -> int:
        """
        Get the dataset's generation if set.
        """
        return int(self._h5_file.attrs.get("spotlight_generation_id", 0))

    def read_value(
        self, column_name: str, index: IndexType
    ) -> Optional[Union[np.generic, str, np.void, np.ndarray]]:
        """
        Get a dataset value as it is stored in the H5 dataset, resolve references.
        """
        self._assert_column_exists(column_name, internal=True)
        self._assert_index_exists(index)
        column = self._h5_file[column_name]
        value = column[index]
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        if column.attrs.get("external", False):
            column_type = self._get_column_type(column)
            target_format = column.attrs.get("format", None)
            try:
                column_type = cast(Type[FileBasedColumnType], column_type)
                return read_external_value(
                    value, column_type, target_format, os.path.dirname(self._filepath)
                )
            except Exception as e:
                raise InvalidExternalData(value) from e
        if self._is_ref_column(column):
            return self._resolve_ref(value, column_name)[()] if value else None
        return value

    def read_column(
        self,
        column_name: str,
        max_elements_per_cell: int = 2048,
        indices: Optional[List[int]] = None,
    ) -> Column:
        """
        Read a dataset column for serialization.
        """
        # pylint: disable=too-many-branches, too-many-nested-blocks
        self._assert_column_exists(column_name, internal=True)

        column = self._h5_file[column_name]
        attrs = decode_attrs(column.attrs)
        is_ref_column = self._is_ref_column(column)
        is_string_dtype = h5py.check_string_dtype(column.dtype)

        raw_values: np.ndarray
        if indices is None:
            raw_values = column[:]
        else:
            raw_values = column[indices]
        if is_string_dtype:
            raw_values = np.array([x.decode("utf-8") for x in raw_values])

        refs: Optional[np.ndarray] = None
        # Submit scalars, windows and small embeddings only
        if attrs.type is Embedding:
            # Handle embeddings first.
            if (
                attrs.embedding_length is not None
                and attrs.embedding_length <= max_elements_per_cell
            ):
                # Embeddings are small enough to send them.
                if not is_ref_column:
                    none_mask = [len(x) == 0 for x in raw_values]
                    raw_values[none_mask] = np.array(None)
                else:
                    raw_values = self._resolve_refs(raw_values, column_name)
            else:
                if not is_ref_column:
                    refs = np.array([len(x) != 0 for x in raw_values])
                else:
                    refs = raw_values.astype(bool)
                raw_values = ref_placeholder_names(refs)
        elif attrs.is_external:
            refs = raw_values != ""
        elif is_ref_column:
            if is_string_dtype:
                # New-style string references.
                raw_values = unescape_dataset_names(raw_values)
                refs = raw_values != ""
            else:
                # Old-style H5 references.
                # Invalid refs evaluated to `False`.
                refs = raw_values.astype(bool)
                if attrs.has_lookup:
                    values = []
                    for ref in raw_values:
                        if ref:
                            h5_dataset: h5py.Dataset = self._h5_file[ref]
                            try:
                                name = h5_dataset.attrs["key"]
                            except KeyError:
                                name = self._get_column_name(h5_dataset)
                            values.append(name)
                        else:
                            values.append(None)
                    raw_values = np.array(values, dtype=object)
                else:
                    raw_values = ref_placeholder_names(refs)

        return Column(
            name=column_name, values=raw_values, references=refs, **asdict(attrs)
        )

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
            column = self._h5_file[column_name]
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

    def read_attrs(self, column_name: str) -> Attrs:
        """
        Read relevant attributes of a column.
        """
        self._assert_column_exists(column_name, internal=True)
        raw_attrs = self._h5_file[column_name].attrs
        return decode_attrs(raw_attrs)

    def min_order(self) -> int:
        """
        Get minimum order over all columns, return 0 if no column has an order.
        One can use `dataset.min_order() - 1` as order for a new column.
        """
        return int(
            min(
                (
                    self._h5_file[name].attrs.get("order", 0)
                    for name in self._column_names
                ),
                default=0,
            )
        )

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

    def __init__(self, source: PathType, dtype: ColumnTypeMapping):
        self._table_file = Path(source)

    @property
    def column_names(self) -> List[str]:
        with self._open_table() as dataset:
            return dataset.keys()

    def __len__(self) -> int:
        with self._open_table() as dataset:
            return len(dataset)

    def get_generation_id(self) -> int:
        with self._open_table() as dataset:
            return dataset.get_generation_id()

    def get_uid(self) -> str:
        return sha1(str(self._table_file.absolute()).encode("utf-8")).hexdigest()

    def get_name(self) -> str:
        return str(self._table_file.name)

    def get_columns(self, column_names: Optional[List[str]] = None) -> List[Column]:
        with self._open_table() as dataset:
            if column_names is None:
                column_names = dataset.keys()
            return [dataset.read_column(column_name) for column_name in column_names]

    def get_internal_columns(self) -> List[Column]:
        with self._open_table() as dataset:
            return [
                dataset.read_column(column_name)
                for column_name in INTERNAL_COLUMN_NAMES
            ]

    def get_column(self, column_name: str, indices: Optional[List[int]]) -> Column:
        with self._open_table() as dataset:
            return dataset.read_column(column_name, indices=indices)

    def get_cell_data(self, column_name: str, row_index: int) -> Any:
        """
        return the value of a single cell
        """
        with self._open_table() as dataset:
            try:
                return dataset.read_value(column_name, row_index)
            except IndexError as e:
                raise NoRowFound(row_index) from e

    def _open_table(self, mode: str = "r") -> H5Dataset:
        try:
            return H5Dataset(self._table_file, mode)
        except FileNotFoundError as e:
            raise NoTableFileFound(self._table_file) from e
        except OSError as e:
            raise CouldNotOpenTableFile(self._table_file) from e
