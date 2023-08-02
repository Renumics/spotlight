"""
access h5 table data
"""
from functools import lru_cache
from hashlib import sha1
from pathlib import Path
from typing import Any, Dict, List, Optional, cast, Union, Type, Tuple
from dataclasses import asdict

import h5py
import numpy as np

from renumics.spotlight.dtypes import Category, Embedding
from renumics.spotlight.dtypes.typing import (
    ColumnType,
    ColumnTypeMapping,
    get_column_type,
)
from renumics.spotlight.typing import PathType, IndexType
from renumics.spotlight.dataset import (
    Dataset,
    INTERNAL_COLUMN_NAMES,
    unescape_dataset_name,
)

from renumics.spotlight.backend.data_source import DataSource, Attrs, Column
from renumics.spotlight.backend.exceptions import (
    NoTableFileFound,
    CouldNotOpenTableFile,
    NoRowFound,
)

from renumics.spotlight.backend import datasource

from renumics.spotlight.dtypes.conversion import (
    DTypeOptions,
    NormalizedValue,
    convert_to_dtype,
)


def unescape_dataset_names(refs: np.ndarray) -> np.ndarray:
    """
    Unescape multiple dataset names.
    """
    return np.array([unescape_dataset_name(value) for value in refs])


def _decode_attrs(raw_attrs: h5py.AttributeManager) -> Tuple[Attrs, bool, bool]:
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

    tags = raw_attrs.get("tags", np.array([])).tolist()

    has_lookup = "lookup_keys" in raw_attrs
    is_external = raw_attrs.get("external", False)

    return (
        Attrs(
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
        ),
        has_lookup,
        is_external,
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
        self, column_name: str, indices: Optional[List[int]] = None
    ) -> Union[list, np.ndarray]:
        """
        Get a decoded dataset column.
        """
        self._assert_column_exists(column_name, internal=True)

        column = cast(h5py.Dataset, self._h5_file[column_name])
        is_string_dtype = h5py.check_string_dtype(column.dtype)

        raw_values: np.ndarray
        if indices is None:
            raw_values = column[:]
        else:
            raw_values = column[indices]
        if is_string_dtype:
            raw_values = np.array([x.decode("utf-8") for x in raw_values])

        if self._is_ref_column(column):
            assert is_string_dtype, "Only new-style string h5 references supported."
            return [
                value.tolist() if isinstance(value, np.void) else value
                for value in self._resolve_refs(raw_values, column_name)
            ]
        if self._get_column_type(column.attrs) is Embedding:
            return [None if len(x) == 0 else x for x in raw_values]
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

    def __init__(self, source: PathType):
        self._table_file = Path(source)

    @property
    def column_names(self) -> List[str]:
        with self._open_table() as dataset:
            return dataset.keys()

    def __len__(self) -> int:
        with self._open_table() as dataset:
            return len(dataset)

    def guess_dtypes(self) -> ColumnTypeMapping:
        with self._open_table() as dataset:
            return {
                column_name: dataset.get_column_type(column_name)
                for column_name in self.column_names
            }

    def get_generation_id(self) -> int:
        with self._open_table() as dataset:
            return dataset.get_generation_id()

    def get_uid(self) -> str:
        return sha1(str(self._table_file.absolute()).encode("utf-8")).hexdigest()

    def get_name(self) -> str:
        return str(self._table_file.name)

    def get_internal_columns(self) -> List[Column]:
        with self._open_table() as dataset:
            return [
                self.get_column(column_name, dataset.get_column_type(column_name))
                for column_name in INTERNAL_COLUMN_NAMES
            ]

    def get_column(
        self,
        column_name: str,
        dtype: Type[ColumnType],
        indices: Optional[List[int]] = None,
        simple: bool = False,
    ) -> Column:
        with self._open_table() as dataset:
            normalized_values = dataset.read_column(column_name, indices=indices)
            if dtype is Category:
                categories = self._get_column_categories(column_name)
                values = [
                    convert_to_dtype(
                        value, dtype, DTypeOptions(categories=categories), simple
                    )
                    for value in normalized_values
                ]
            else:
                values = [
                    convert_to_dtype(value, dtype, simple=simple)
                    for value in normalized_values
                ]
            attrs, _, _ = _decode_attrs(dataset._h5_file[column_name].attrs)
            attrs.type = dtype
        return Column(name=column_name, values=values, **asdict(attrs))

    def get_cell_data(
        self, column_name: str, row_index: int, dtype: Type[ColumnType]
    ) -> Any:
        """
        return the value of a single cell
        """
        # read raw value from h5 table
        with self._open_table() as dataset:
            try:
                normalized_value = dataset.read_value(column_name, row_index)
            except IndexError as e:
                raise NoRowFound(row_index) from e

            # convert normalized value to requested dtype
            if dtype is Category:
                categories = self._get_column_categories(column_name)
                return convert_to_dtype(
                    normalized_value, dtype, DTypeOptions(categories=categories)
                )
            return convert_to_dtype(normalized_value, dtype)

    @lru_cache(maxsize=128)
    def _get_column_categories(self, column_name: str) -> Dict[str, int]:
        with self._open_table() as dataset:
            attrs = dataset.get_column_attributes(column_name)
            try:
                return cast(Dict[str, int], attrs["categories"])
            except KeyError:
                normalized_values = cast(
                    List[str],
                    [
                        convert_to_dtype(value, str, simple=True)
                        for value in dataset.read_column(column_name)
                    ],
                )
                category_names = sorted(set(normalized_values))
                return {
                    category_name: i for i, category_name in enumerate(category_names)
                }

    def _open_table(self, mode: str = "r") -> H5Dataset:
        try:
            return H5Dataset(self._table_file, mode)
        except FileNotFoundError as e:
            raise NoTableFileFound(self._table_file) from e
        except OSError as e:
            raise CouldNotOpenTableFile(self._table_file) from e
