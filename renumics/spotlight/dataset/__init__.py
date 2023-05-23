"""
This module provides Spotlight dataset.
"""
# pylint: disable=too-many-lines
import getpass
import os
import shutil
import uuid
from datetime import datetime
from tempfile import TemporaryDirectory
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    overload,
    Set,
    Tuple,
    Type,
    Union,
    cast,
)

import h5py
import numpy as np
import pandas as pd
import prettytable
import trimesh
import validators
from loguru import logger
from typing_extensions import Literal, TypeGuard

from renumics.spotlight import __version__
from renumics.spotlight.io.pandas import (
    infer_dtypes,
    prepare_column,
    is_string_mask,
    stringify_columns,
)
from renumics.spotlight.typing import (
    BoolType,
    IndexType,
    Indices1DType,
    PathOrURLType,
    PathType,
    is_integer,
    is_iterable,
)
from renumics.spotlight.dtypes import (
    _BaseData,
    _BaseFileBasedData,
    Embedding,
    Mesh,
    Sequence1D,
    Image,
    Audio,
    Category,
    Video,
    Window,
)
from renumics.spotlight.dtypes.typing import (
    ColumnType,
    ColumnTypeMapping,
    FileBasedColumnType,
    get_column_type,
    get_column_type_name,
    is_file_based_column_type,
)
from . import exceptions
from .typing import (
    REF_COLUMN_TYPE_NAMES,
    SimpleColumnType,
    RefColumnType,
    ExternalColumnType,
    BoolColumnInputType,
    IntColumnInputType,
    FloatColumnInputType,
    StringColumnInputType,
    DatetimeColumnInputType,
    CategoricalColumnInputType,
    WindowColumnInputType,
    ArrayColumnInputType,
    EmbeddingColumnInputType,
    AudioColumnInputType,
    ImageColumnInputType,
    MeshColumnInputType,
    Sequence1DColumnInputType,
    VideoColumnInputType,
    SimpleColumnInputType,
    RefColumnInputType,
    ColumnInputType,
)

INTERNAL_COLUMN_NAMES = ["__last_edited_by__", "__last_edited_at__"]

_EncodedColumnType = Optional[Union[bool, int, float, str, np.ndarray, h5py.Reference]]


def get_current_datetime() -> datetime:
    """
    Get current datetime with timezone.
    """
    return datetime.now().astimezone()


def prepare_path_or_url(path_or_url: PathOrURLType, workdir: PathType) -> str:
    """
    For a relative path, prefix it with the `workdir`.
    For an absolute path or an URL, do nothing.
    """
    path_or_url_str = str(path_or_url)
    if validators.url(path_or_url_str):
        return path_or_url_str
    return os.path.join(workdir, path_or_url_str)


def escape_dataset_name(name: str) -> str:
    r"""
    Replace "\" with "\\" and "/" with "\s".
    """
    return name.replace("\\", "\\\\").replace("/", r"\s")


def unescape_dataset_name(escaped_name: str) -> str:
    r"""
    Replace "\\" with "\" and "\s" with "/".
    """
    name = ""
    i = 0
    while i < len(escaped_name):
        char = escaped_name[i]
        i += 1
        if char == "\\":
            next_char = escaped_name[i]
            i += 1
            if next_char == "\\":
                name += "\\"
            elif next_char == "s":
                name += "/"
            else:
                raise RuntimeError
        else:
            name += char
    return name


_ALLOWED_COLUMN_TYPES: Dict[Type[ColumnType], Tuple[Type, ...]] = {
    bool: (np.bool_,),
    int: (np.integer,),
    float: (np.floating,),
    datetime: (np.datetime64,),
}
_ALLOWED_COLUMN_DTYPES: Dict[Type[ColumnType], Tuple[Type, ...]] = {
    bool: (np.bool_,),
    int: (np.integer,),
    float: (np.floating,),
    datetime: (np.datetime64,),
    Window: (np.floating,),
    Embedding: (np.floating,),
}


def _check_valid_value_type(value: Any, column_type: Type[ColumnType]) -> bool:
    """
    Check if a value is suitable for the given column type. Instances of the
    given type are always suitable for its type, but extra types from
    `_ALLOWED_COLUMN_TYPES` are also checked.
    """
    allowed_types = (column_type,) + _ALLOWED_COLUMN_TYPES.get(column_type, ())
    return isinstance(value, allowed_types)


def _check_valid_value_dtype(dtype: np.dtype, column_type: Type[ColumnType]) -> bool:
    """
    Check if an array with the given dtype is suitable for the given column type.
    Only types from `_ALLOWED_COLUMN_DTYPES` are checked. All other column types
    are assumed to have no dtype equivalent.
    """
    allowed_dtypes = _ALLOWED_COLUMN_DTYPES.get(column_type, ())
    return any(np.issubdtype(dtype, allowed_dtype) for allowed_dtype in allowed_dtypes)


def _check_valid_array(
    value: Any, column_type: Type[ColumnType]
) -> TypeGuard[np.ndarray]:
    """
    Check if a value is an array and its type is suitable for the given column type.
    """
    return isinstance(value, np.ndarray) and _check_valid_value_dtype(
        value.dtype, column_type
    )


class Dataset:
    # pylint: disable=too-many-public-methods
    """
    Spotlight dataset.
    """

    _filepath: str
    _mode: str
    _h5_file: h5py.File
    _closed: bool
    _column_names: Set[str]
    _length: int

    @staticmethod
    def _user_column_attributes(column_type: Type[ColumnType]) -> Dict[str, Type]:
        attribute_names = {
            "order": int,
            "hidden": bool,
            "optional": bool,
            "default": object,
            "description": str,
            "tags": list,
        }
        if column_type in {
            bool,
            int,
            float,
            str,
            Category,
            Window,
        }:
            attribute_names["editable"] = bool
        if column_type is Category:
            attribute_names["categories"] = dict
        if column_type is Sequence1D:
            attribute_names["x_label"] = str
            attribute_names["y_label"] = str
        if issubclass(column_type, _BaseFileBasedData):
            attribute_names["lookup"] = dict
            attribute_names["external"] = bool
        if column_type is Audio:
            attribute_names["lossy"] = bool
        return attribute_names

    @classmethod
    def _default_default(cls, column_type: Type[ColumnType]) -> Any:
        if column_type is datetime:
            return np.datetime64("NaT")
        if column_type in (str, Category):
            return ""
        if column_type is float:
            return float("nan")
        if column_type is Window:
            return [np.nan, np.nan]
        if column_type is np.ndarray or issubclass(column_type, _BaseData):
            return None
        raise exceptions.InvalidAttributeError(
            f"`default` argument for optional column of type "
            f"{get_column_type_name(column_type)} should be set, but `None` received."
        )

    def __init__(self, filepath: PathType, mode: str):
        self._filepath = os.path.abspath(filepath)
        self._check_mode(mode)
        self._mode = mode
        dirpath = os.path.dirname(self._filepath)
        if self._mode in ("w", "w-", "x", "a"):
            os.makedirs(dirpath, exist_ok=True)
        elif not os.path.isdir(dirpath):
            raise FileNotFoundError(f"File {filepath} does not exist.")
        self._closed = True
        self._column_names = set()
        self._length = 0

    @property
    def filepath(self) -> str:
        """
        Dataset file name.
        """
        return self._filepath

    @property
    def mode(self) -> str:
        """
        Dataset file open mode.
        """
        return self._mode

    def __enter__(self) -> "Dataset":
        self.open()
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def __delitem__(self, item: Union[str, IndexType, Indices1DType]) -> None:
        """
        Delete a dataset column or row.

        Example:
            >>> from renumics.spotlight import Dataset
            >>> with Dataset("docs/example.h5", "w") as dataset:
            ...     dataset.append_bool_column("bools", [True, False, False, True])
            ...     dataset.append_int_column("ints", [-1, 0, 1, 2])
            ...     dataset.append_float_column("floats", [-1.0, 0.0, 1.0, float("nan")])
            ...     print(len(dataset))
            ...     print(sorted(dataset.keys()))
            4
            ['bools', 'floats', 'ints']
            >>> with Dataset("docs/example.h5", "a") as dataset:
            ...     del dataset[-1]
            ...     print(len(dataset))
            ...     print(sorted(dataset.keys()))
            3
            ['bools', 'floats', 'ints']
            >>> with Dataset("docs/example.h5", "a") as dataset:
            ...     del dataset["bools"]
            ...     del dataset["floats"]
            ...     print(len(dataset))
            ...     print(sorted(dataset.keys()))
            3
            ['ints']
        """
        self._assert_is_writable()
        if isinstance(item, str):
            self._assert_column_exists(item)
            del self._h5_file[item]
            try:
                del self._h5_file[f"__group__/{item}"]
            except KeyError:
                pass
            self._column_names.discard(item)
            if not self._column_names:
                self._length = 0
                self._update_internal_columns()
        elif isinstance(item, (slice, list, np.ndarray)):
            mask = np.full(self._length, True)
            try:
                mask[item] = False
            except Exception as e:
                raise exceptions.InvalidIndexError(
                    f"Indices {item} of type `{type(item)}` do not match "
                    f"to the dataset with the length {self._length}."
                ) from e
            keep_indices = np.nonzero(mask)[0]
            length = len(keep_indices)
            if length == self._length:
                logger.warning(
                    "No rows removed because the given indices reference no elements."
                )
                return
            start = (~mask).argmax() if length else 0
            start = cast(int, start)
            keep_indices = keep_indices[start:]
            for column_name in self.keys() + INTERNAL_COLUMN_NAMES:
                column = self._h5_file[column_name]
                column[start:length] = column[keep_indices]
                column.resize(length, axis=0)
            self._length = length
        elif is_integer(item):
            self._assert_index_exists(item)
            item = cast(int, item)
            if item < 0:
                item += self._length
            for column_name in self.keys() + INTERNAL_COLUMN_NAMES:
                column = self._h5_file[column_name]
                raw_values = column[item + 1 :]
                if self._get_column_type(column) is Embedding:
                    raw_values = list(raw_values)
                column[item:-1] = raw_values
                column.resize(self._length - 1, axis=0)
            self._length -= 1
        else:
            raise exceptions.InvalidIndexError(
                f"`item` argument should be a string or an index/indices, but"
                f"value {item} of type `{type(item)}` received.`"
            )
        self._update_generation_id()

    @overload
    def __getitem__(
        self, item: Union[str, Tuple[str, Indices1DType], Tuple[Indices1DType, str]]
    ) -> np.ndarray:
        ...

    @overload
    def __getitem__(self, item: IndexType) -> Dict[str, Optional[ColumnType]]:
        ...

    @overload
    def __getitem__(
        self, item: Union[Tuple[str, IndexType], Tuple[IndexType, str]]
    ) -> Optional[ColumnType]:
        ...

    def __getitem__(
        self,
        item: Union[
            str,
            IndexType,
            Tuple[str, Union[IndexType, Indices1DType]],
            Tuple[Union[IndexType, Indices1DType], str],
        ],
    ) -> Union[np.ndarray, Dict[str, Optional[ColumnType]], Optional[ColumnType],]:
        """
        Get a dataset column, row or value.

        Example:
            >>> from renumics.spotlight import Dataset
            >>> with Dataset("docs/example.h5", "w") as dataset:
            ...     dataset.append_bool_column("bools", [True, False, False])
            ...     dataset.append_int_column("ints", [-1, 0, 1])
            ...     dataset.append_float_column("floats", [-1.0, 0.0, 1.0])
            >>> with Dataset("docs/example.h5", "r") as dataset:
            ...     print("bools:", dataset["bools"])
            ...     print("ints:", dataset["ints"])
            ...     row = dataset[0]
            ...     print("0th row:", [(key, row[key]) for key in sorted(row.keys())])
            ...     row = dataset[1]
            ...     print("1th row:", [(key, row[key]) for key in sorted(row.keys())])
            ...     print(dataset["ints", 2])
            ...     print(dataset[2, "floats"])
            bools: [ True False False]
            ints: [-1  0  1]
            0th row: [('bools', True), ('floats', -1.0), ('ints', -1)]
            1th row: [('bools', False), ('floats', 0.0), ('ints', 0)]
            1
            1.0
        """
        self._assert_is_opened()
        if is_integer(item):
            self._assert_index_exists(item)
            return {
                column_name: self._get_value(self._h5_file[column_name], item)
                for column_name in self._column_names
            }
        column_name, index = self._prepare_item(item)  # type: ignore
        self._assert_column_exists(column_name, internal=True)
        column = self._h5_file[column_name]
        if is_integer(index):
            return self._get_value(column, index, check_index=True)
        if index is None or isinstance(index, (slice, list, np.ndarray)):
            return self._get_column(column, index)
        raise exceptions.InvalidIndexError(
            f"Invalid index {index} of type `{type(index)}` received."
        )

    @overload
    def __setitem__(
        self,
        item: Union[str, Tuple[str, Indices1DType], Tuple[Indices1DType, str]],
        value: Union[ColumnInputType, Iterable[ColumnInputType]],
    ) -> None:
        ...

    @overload
    def __setitem__(self, item: IndexType, value: Dict[str, ColumnInputType]) -> None:
        ...

    @overload
    def __setitem__(
        self,
        item: Union[Tuple[str, IndexType], Tuple[IndexType, str]],
        value: ColumnInputType,
    ) -> None:
        ...

    def __setitem__(
        self,
        item: Union[
            str,
            IndexType,
            Tuple[str, Union[IndexType, Indices1DType]],
            Tuple[Union[IndexType, Indices1DType], str],
        ],
        value: Union[
            ColumnInputType, Iterable[ColumnInputType], Dict[str, ColumnInputType]
        ],
    ) -> None:
        """
        Set a dataset column, row or value.

        Example:
            >>> from renumics.spotlight import Dataset
            >>> with Dataset("docs/example.h5", "w") as dataset:
            ...     dataset.append_bool_column("bools", [True, False, False])
            ...     dataset.append_int_column("ints", [-1, 0, 1])
            ...     dataset.append_float_column("floats", [-1.0, 0.0, 1.0])
            >>> with Dataset("docs/example.h5", "a") as dataset:
            ...     row = dataset[0]
            ...     print("0th row before:", [(key, row[key]) for key in sorted(row.keys())])
            ...     dataset[0] = {"bools": True, "ints": 5, "floats": float("inf")}
            ...     row = dataset[0]
            ...     print("0th row after:", [(key, row[key]) for key in sorted(row.keys())])
            0th row before: [('bools', True), ('floats', -1.0), ('ints', -1)]
            0th row after: [('bools', True), ('floats', inf), ('ints', 5)]
            >>> with Dataset("docs/example.h5", "a") as dataset:
            ...     print(dataset["bools", 2])
            ...     dataset["bools", 2] = True
            ...     print(dataset["bools", 2])
            False
            True
            >>> with Dataset("docs/example.h5", "a") as dataset:
            ...     print(dataset["floats", 0])
            ...     dataset[0, "floats"] = -5.0
            ...     print(dataset["floats", 0])
            inf
            -5.0
        """
        # pylint: disable=too-many-branches
        self._assert_is_writable()
        if is_integer(item):
            self._assert_index_exists(item)
            if not isinstance(value, dict):
                raise exceptions.InvalidDTypeError(
                    f"Dataset row should be a dict, but value {value} of type "
                    f"`{type(value)}` received.`"
                )
            self._set_row(item, value)
        else:
            column_name, index = self._prepare_item(item)  # type: ignore
            self._assert_column_exists(column_name)
            column = self._h5_file[column_name]
            if is_integer(index):
                self._set_value(column, index, value, check_index=True)  # type: ignore
            elif index is None or isinstance(index, (slice, list, np.ndarray)):
                self._set_column(column, value, index, preserve_values=True)  # type: ignore
            else:
                raise exceptions.InvalidIndexError(
                    f"Invalid index {index} of type `{type(index)}` received."
                )
        self._update_generation_id()

    @staticmethod
    def _prepare_item(
        item: Union[
            str,
            Tuple[str, Union[IndexType, Indices1DType]],
            Tuple[Union[IndexType, Indices1DType], str],
        ],
    ) -> Tuple[str, Optional[Union[IndexType, Indices1DType]]]:
        if isinstance(item, str):
            return item, None
        if isinstance(item, tuple) and len(item) == 2:
            if isinstance(item[0], str):
                return item
            if isinstance(item[1], str):
                return item[1], item[0]
        raise exceptions.InvalidIndexError(
            f"dataset index should be a string, an index or a pair of a string "
            f"and an index/indices, but value {item} of type `{type(item)}` received."
        )

    def __iadd__(
        self, other: Union[Dict[str, ColumnInputType], "Dataset"]
    ) -> "Dataset":
        if isinstance(other, dict):
            self.append_row(**other)
            return self
        if isinstance(other, Dataset):
            self.append_dataset(other)
            return self
        raise TypeError(
            f"`other` argument should be a dict or an `Dataset` instance, "
            f"but value {other} of type `{type(other)}` received.`"
        )

    def __len__(self) -> int:
        return self._length

    def __str__(self) -> str:
        return self._pretty_table().get_string()

    def open(self, mode: Optional[str] = None) -> None:
        """
        Open previously closed file or reopen file with another mode.

        Args:
            mode: Optional open mode. If not given, use `self.mode`.
        """
        if mode is not None and mode != self._mode:
            self._check_mode(mode)
            self.close()
            self._mode = mode
        if self._closed:
            self._h5_file = h5py.File(self._filepath, self._mode)
            self._closed = False
            self._column_names, self._length = self._get_column_names_and_length()
            if self._is_writable():
                if "spotlight_generation_id" not in self._h5_file.attrs:
                    self._h5_file.attrs["spotlight_generation_id"] = np.uint64(0)
                self._append_internal_columns()
            self._column_names.difference_update(set(INTERNAL_COLUMN_NAMES))

    def close(self) -> None:
        """
        Close file.
        """
        if not self._closed:
            if self._is_writable():
                current_time = get_current_datetime().isoformat()
                raw_attrs = self._h5_file.attrs
                # Version could be `None`, but *shouldn't* be.
                raw_attrs["version"] = __version__
                raw_attrs["last_edited_by"] = self._get_username()
                raw_attrs["last_edited_at"] = current_time
                if "created" not in raw_attrs:
                    raw_attrs["created"] = __version__
                if "created_by" not in raw_attrs:
                    raw_attrs["created_by"] = self._get_username()
                if "created_at" not in raw_attrs:
                    raw_attrs["created_at"] = current_time
            self._h5_file.close()
            self._closed = True
            self._column_names = set()
            self._length = 0

    def keys(self) -> List[str]:
        """
        Get dataset column names.
        """
        return list(self._column_names)

    @overload
    def iterrows(self) -> Iterable[Dict[str, Optional[ColumnType]]]:
        ...

    @overload
    def iterrows(
        self, column_names: Union[str, Iterable[str]]
    ) -> Union[
        Iterable[Dict[str, Optional[ColumnType]]], Iterable[Optional[ColumnType]]
    ]:
        ...

    def iterrows(
        self, column_names: Optional[Union[str, Iterable[str]]] = None
    ) -> Union[
        Iterable[Dict[str, Optional[ColumnType]]], Iterable[Optional[ColumnType]]
    ]:
        """
        Iterate through dataset rows.
        """
        self._assert_is_opened()
        if isinstance(column_names, str):
            self._assert_column_exists(column_names)
            column = self._h5_file[column_names]
            column_type = self._get_column_type(column)
            if column.attrs.get("external", False):
                for value in column:
                    column_type = cast(Type[ExternalColumnType], column_type)
                    yield self._decode_external_value(value, column_type)
            elif self._is_ref_column(column):
                for ref in column:
                    column_type = cast(Type[RefColumnType], column_type)
                    yield self._decode_ref_value(ref, column_type, column_names)
            else:
                for value in column:
                    column_type = cast(Type[SimpleColumnType], column_type)
                    yield self._decode_simple_value(value, column, column_type)
        else:
            if column_names is None:
                column_names = self._column_names
            else:
                column_names = set(column_names)
                if column_names.difference(self._column_names):
                    raise exceptions.ColumnNotExistsError(
                        'Columns "'
                        + '", "'.join(column_names.difference(self._column_names))
                        + '" do not exist.'
                    )
            columns = {
                column_name: self._h5_file[column_name] for column_name in column_names
            }
            for i in range(self._length):
                yield {
                    column_name: self._get_value(column, i)
                    for column_name, column in columns.items()
                }

    def from_pandas(
        self,
        df: pd.DataFrame,
        index: bool = False,
        dtype: Optional[ColumnTypeMapping] = None,
        workdir: Optional[PathType] = None,
    ) -> None:
        """
        Import a pandas dataframe to the dataset.

        Only scalar types supported by the Spotlight dataset are imported, the
        other are printed in a warning message.

        Args:
            df: `pandas.DataFrame` to import.
            index: Whether to import index of the dataframe as regular dataset
                column.
            dtype: Optional dict with mapping `column name -> column type` with
                column types allowed by Spotlight.
            workdir: Optional folder where audio/images/meshes are stored. If
                `None`, current folder is used.

        Example:
            >>> from datetime import datetime
            >>> import pandas as pd
            >>> from renumics.spotlight import Dataset
            >>> df = pd.DataFrame(
            ...     {
            ...         "bools": [True, False, False],
            ...         "ints": [-1, 0, 1],
            ...         "floats": [-1.0, 0.0, 1.0],
            ...         "strings": ["a", "b", "c"],
            ...         "datetimes": datetime.now().astimezone(),
            ...     }
            ... )
            >>> with Dataset("docs/example.h5", "w") as dataset:
            ...     dataset.from_pandas(df, index=False)
            >>> with Dataset("docs/example.h5", "r") as dataset:
            ...     print(len(dataset))
            ...     print(sorted(dataset.keys()))
            3
            ['bools', 'datetimes', 'floats', 'ints', 'strings']
        """
        self._assert_is_writable()

        if not df.columns.is_unique:
            raise exceptions.DatasetColumnsNotUnique(
                "DataFrame's columns are not unique"
            )

        if index:
            df = df.reset_index(level=df.index.names)
        else:
            df = df.copy()
        df.columns = stringify_columns(df)

        inferred_dtype = infer_dtypes(df, dtype)

        for column_name in df.columns:
            try:
                column = df[column_name]
                column_type = inferred_dtype[column_name]

                column = prepare_column(column, column_type)

                if workdir is not None and is_file_based_column_type(dtype):
                    # For file-based data types, relative paths should be resolved.
                    str_mask = is_string_mask(column)
                    column[str_mask] = column[str_mask].apply(
                        lambda x: prepare_path_or_url(x, workdir)
                    )

                attrs = {}

                if column_type is Category:
                    attrs["categories"] = column.cat.categories.to_list()
                    values = column.to_numpy()
                    # `pandas` uses `NaN`s for unknown values, we use `None`.
                    values = np.where(pd.isna(values), np.array(None), values)
                elif column_type is datetime:
                    values = column.to_numpy("datetime64[us]")
                else:
                    values = column.to_numpy()

                if is_file_based_column_type(column_type):
                    attrs["external"] = False
                    attrs["lookup"] = False

                self.append_column(
                    column_name,
                    column_type,
                    values,
                    hidden=column_name.startswith("_"),
                    optional=column_type not in (bool, int),
                    **attrs,
                )
            except Exception as e:  # pylint: disable=broad-except
                if column_name in (dtype or {}):
                    raise e
                logger.warning(
                    f"Column '{column_name}' not imported from "
                    f"`pandas.DataFrame` because of the following error:\n{e}"
                )

    def from_csv(
        self,
        filepath: PathType,
        dtype: Optional[ColumnTypeMapping] = None,
        columns: Optional[Iterable[str]] = None,
        workdir: Optional[PathType] = None,
    ) -> None:
        """
        Args:
            filepath: Path of csv file to read.
            dtype: Optional dict with mapping `column name -> column type` with
                column types allowed by Spotlight.
            columns: Optional columns to read from csv. If not set, read all
                columns.
            workdir: Optional folder where audio/images/meshes are stored. If
                `None`, csv folder is used.
        """
        if columns is not None:
            columns = list(set(columns))
        df: pd.DataFrame = pd.read_csv(filepath, usecols=columns or None)
        if workdir is None:
            workdir = os.path.dirname(filepath)
        self.from_pandas(df, index=False, dtype=dtype, workdir=workdir)

    def to_pandas(self) -> pd.DataFrame:
        """
        Export the dataset to pandas dataframe.

        Only scalar types of the Spotlight dataset are exported, the others are
        printed in a warning message.

        Returns:
            `pandas.DataFrame` filled with the data of the Spotlight dataset.

        Example:
            >>> import pandas as pd
            >>> from renumics.spotlight import Dataset
            >>> with Dataset("docs/example.h5", "w") as dataset:
            ...     dataset.append_bool_column("bools", [True, False, False])
            ...     dataset.append_int_column("ints", [-1, 0, 1])
            ...     dataset.append_float_column("floats", [-1.0, 0.0, 1.0])
            ...     dataset.append_string_column("strings", ["a", "b", "c"])
            ...     dataset.append_datetime_column("datetimes", optional=True)
            >>> with Dataset("docs/example.h5", "r") as dataset:
            ...     df = dataset.to_pandas()
            >>> print(len(df))
            3
            >>> print(df.columns.sort_values())
            Index(['bools', 'datetimes', 'floats', 'ints', 'strings'], dtype='object')
        """
        self._assert_is_opened()
        df = pd.DataFrame()
        for column_name in self._column_names:
            column_type = self.get_column_type(column_name)
            if column_type in (bool, int, float, str, datetime):
                df[column_name] = self[column_name]
            elif column_type is Category:
                df[column_name] = pd.Categorical.from_codes(
                    self._h5_file[column_name],
                    self._h5_file[column_name].attrs["category_keys"],  # type: ignore
                )

        not_exported_columns = self._column_names.difference(df.columns)
        if len(not_exported_columns) > 0:
            logger.warning(
                'Columns "'
                + '", "'.join(not_exported_columns)
                + '" not appended to the dataframe. Please export them manually.'
            )
        return df

    def append_bool_column(
        self,
        name: str,
        values: Union[BoolColumnInputType, Iterable[BoolColumnInputType]] = None,
        order: Optional[int] = None,
        hidden: bool = False,
        optional: bool = False,
        default: BoolColumnInputType = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        editable: bool = True,
    ) -> None:
        # pylint: disable=too-many-arguments
        """
        Create and optionally fill a boolean column.

        Args:
            name: Column name.
            values: Optional column values. If a single value, the whole column
                filled with this value.
            order: Optional Spotlight priority order value. `None` means the
                lowest priority.
            hidden: Whether column is hidden in Spotlight.
            optional: Whether column is optional.
            default: Value to use by default if column is optional and no value
                or `None` is given. If `optional` is `True`, should be
                explicitly set to `True` or `False`.
            description: Optional column description.
            tags: Optional tags for the column.
            editable: Whether column is editable in Spotlight.

        Example:
            >>> from renumics.spotlight import Dataset
            >>> value = False
            >>> with Dataset("docs/example.h5", "w") as dataset:
            ...     dataset.append_bool_column("bool_values", 5*[value])
            >>> with Dataset("docs/example.h5", "r") as dataset:
            ...     print(dataset["bool_values", 2])
            False
        """
        self._append_column(
            name,
            bool,
            values,
            np.dtype(bool),
            order,
            hidden,
            optional,
            default,
            description,
            tags,
            editable=editable,
        )

    def append_int_column(
        self,
        name: str,
        values: Union[IntColumnInputType, Iterable[IntColumnInputType]] = None,
        order: Optional[int] = None,
        hidden: bool = False,
        optional: bool = False,
        default: IntColumnInputType = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        editable: bool = True,
    ) -> None:
        # pylint: disable=too-many-arguments
        """
        Create and optionally fill an integer column.

        Args:
            name: Column name.
            values: Optional column values. If a single value, the whole column
                filled with this value.
            order: Optional Spotlight priority order value. `None` means the
                lowest priority.
            hidden: Whether column is hidden in Spotlight.
            optional: Whether column is optional. If `default` other than `None`
                is specified, `optional` is automatically set to `True`.
            default: Value to use by default if column is optional and no value
                or `None` is given. If `optional` is `True`, should be
                explicitly set.
            description: Optional column description.
            tags: Optional tags for the column.
            editable: Whether column is editable in Spotlight.

        Example:
            Find a similar example usage in
            :func:`renumics.spotlight.dataset.Dataset.append_bool_column`.
        """
        self._append_column(
            name,
            int,
            values,
            np.dtype(int),
            order,
            hidden,
            optional,
            default,
            description,
            tags,
            editable=editable,
        )

    def append_float_column(
        self,
        name: str,
        values: Union[FloatColumnInputType, Iterable[FloatColumnInputType]] = None,
        order: Optional[int] = None,
        hidden: bool = False,
        optional: bool = False,
        default: FloatColumnInputType = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        editable: bool = True,
    ) -> None:
        # pylint: disable=too-many-arguments
        """
        Create and optionally fill a float column.

        Args:
            name: Column name.
            values: Optional column values. If a single value, the whole column
                filled with this value.
            order: Optional Spotlight priority order value. `None` means the
                lowest priority.
            hidden: Whether column is hidden in Spotlight.
            optional: Whether column is optional. If `default` other than NaN is
                specified, `optional` is automatically set to `True`.
            default: Value to use by default if column is optional and no value
                or `None` is given.
            description: Optional column description.
            tags: Optional tags for the column.
            editable: Whether column is editable in Spotlight.

        Example:
            Find a similar example usage in
            :func:`renumics.spotlight.dataset.Dataset.append_bool_column`.
        """
        self._append_column(
            name,
            float,
            values,
            np.dtype(float),
            order,
            hidden,
            optional,
            default,
            description,
            tags,
            editable=editable,
        )

    def append_string_column(
        self,
        name: str,
        values: Union[StringColumnInputType, Iterable[StringColumnInputType]] = None,
        order: Optional[int] = None,
        hidden: bool = False,
        optional: bool = False,
        default: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        editable: bool = True,
    ) -> None:
        # pylint: disable=too-many-arguments
        """
        Create and optionally fill a float column.

        Args:
            name: Column name.
            values: Optional column values. If a single value, the whole column
                filled with this value.
            order: Optional Spotlight priority order value. `None` means the
                lowest priority.
            hidden: Whether column is hidden in Spotlight.
            optional: Whether column is optional. If `default` other than empty
                string is specified, `optional` is automatically set to `True`.
            default: Value to use by default if column is optional and no value
                or `None` is given.
            description: Optional column description.
            tags: Optional tags for the column.
            editable: Whether column is editable in Spotlight.

        Example:
            Find a similar example usage in
            :func:`renumics.spotlight.dataset.Dataset.append_bool_column`.
        """
        self._append_column(
            name,
            str,
            values,
            h5py.string_dtype(),
            order,
            hidden,
            optional,
            default,
            description,
            tags,
            editable=editable,
        )

    def append_datetime_column(
        self,
        name: str,
        values: Union[
            DatetimeColumnInputType, Iterable[DatetimeColumnInputType]
        ] = None,
        order: Optional[int] = None,
        hidden: bool = False,
        optional: bool = False,
        default: DatetimeColumnInputType = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> None:
        # pylint: disable=too-many-arguments
        """
        Create and optionally fill a datetime column.

        Args:
            name: Column name.
            values: Optional column values. If a single value, the whole column
                filled with this value.
            order: Optional Spotlight priority order value. `None` means the
                lowest priority.
            hidden: Whether column is hidden in Spotlight.
            optional: Whether column is optional. If `default` other than `None`
                is specified, `optional` is automatically set to `True`.
            default: Value to use by default if column is optional and no value
                or `None` is given.
            description: Optional column description.
            tags: Optional tags for the column.

        Example:
            >>> import numpy as np
            >>> import datetime
            >>> from renumics.spotlight import Dataset
            >>> date = datetime.datetime.now()
            >>> with Dataset("docs/example.h5", "w") as dataset:
            ...     dataset.append_datetime_column("dates", 5*[date])
            >>> with Dataset("docs/example.h5", "r") as dataset:
            ...     print(dataset["dates", 2] < datetime.datetime.now())
            True
        """
        self._append_column(
            name,
            datetime,
            values,
            h5py.string_dtype(),
            order,
            hidden,
            optional,
            default,
            description,
            tags,
        )

    def append_array_column(
        self,
        name: str,
        values: Union[ArrayColumnInputType, Iterable[ArrayColumnInputType]] = None,
        order: Optional[int] = None,
        hidden: bool = False,
        optional: bool = False,
        default: ArrayColumnInputType = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> None:
        # pylint: disable=too-many-arguments
        """
        Create and optionally fill a numpy array column.

        Args:
            name: Column name.
            values: Optional column values. If a single value, the whole column
                filled with this value.
            order: Optional Spotlight priority order value. `None` means the
                lowest priority.
            hidden: Whether column is hidden in Spotlight.
            optional: Whether column is optional. If `default` other than `None`
                is specified, `optional` is automatically set to `True`.
            default: Value to use by default if column is optional and no value
                or `None` is given.
            description: Optional column description.
            tags: Optional tags for the column.

        Example:
            >>> import numpy as np
            >>> from renumics.spotlight import Dataset
            >>> array_data = np.random.rand(5,3)
            >>> with Dataset("docs/example.h5", "w") as dataset:
            ...     dataset.append_array_column("arrays", 5*[array_data])
            >>> with Dataset("docs/example.h5", "r") as dataset:
            ...     print(dataset["arrays", 2].shape)
            (5, 3)
        """
        self._append_column(
            name,
            np.ndarray,
            values,
            h5py.string_dtype(),
            order,
            hidden,
            optional,
            default,
            description,
            tags,
        )

    def append_categorical_column(
        self,
        name: str,
        values: Union[
            CategoricalColumnInputType, Iterable[CategoricalColumnInputType]
        ] = None,
        order: Optional[int] = None,
        hidden: bool = False,
        optional: bool = False,
        default: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        editable: bool = True,
        categories: Optional[Union[Iterable[str], Dict[str, int]]] = None,
    ) -> None:
        # pylint: disable=too-many-arguments
        """
        Create and optionally fill a categorical column.

        Args:
            name: Column name.
            categories: The allowed categories for this column ("" is not allowed)
            values: Optional column values. If a single value, the whole column
                filled with this value.
            order: Optional Spotlight priority order value. `None` means the
                lowest priority.
            hidden: Whether column is hidden in Spotlight.
            optional: Whether column is optional. If `default` other than empty
                string is specified, `optional` is automatically set to `True`.
            default: Value to use by default if column is optional and no value
                or `None` is given.
            description: Optional column description.
            tags: Optional tags for the column.
            editable: Whether column is editable in Spotlight.

        Example:
            Find an example usage in  :class:`renumics.spotlight.dtypes'.Category`.
        """
        self._append_column(
            name,
            Category,
            values,
            np.dtype("int32"),
            order,
            hidden,
            optional,
            default,
            description,
            tags,
            editable=editable,
            categories=categories,
        )

    def append_embedding_column(
        self,
        name: str,
        values: Union[
            EmbeddingColumnInputType, Iterable[EmbeddingColumnInputType]
        ] = None,
        order: Optional[int] = None,
        hidden: bool = False,
        optional: bool = False,
        default: EmbeddingColumnInputType = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        dtype: Union[str, np.dtype] = "float32",
    ) -> None:
        # pylint: disable=too-many-arguments
        """
        Create and optionally fill a mesh column.

        Args:
            name: Column name.
            values: Optional column values. If a single value, the whole column
                filled with this value.
            order: Optional Spotlight priority order value. `None` means the
                lowest priority.
            hidden: Whether column is hidden in Spotlight.
            optional: Whether column is optional. If `default` other than `None`
                is specified, `optional` is automatically set to `True`.
            default: Value to use by default if column is optional and no value
                or `None` is given.
            description: Optional column description.
            tags: Optional tags for the column.
            dtype: A valid float numpy dtype. Default is "float32".

        Example:
            Find an example usage in  :class:`renumics.spotlight.dtypes'.Embedding`.
        """
        np_dtype = np.dtype(dtype)
        if np_dtype.str[1] != "f":
            raise ValueError(
                f'A float `dtype` expected, but dtype "{np_dtype.name}" received.'
            )
        self._append_column(
            name,
            Embedding,
            values,
            h5py.vlen_dtype(np_dtype),
            order,
            hidden,
            optional,
            default,
            description,
            tags,
        )

    def append_sequence_1d_column(
        self,
        name: str,
        values: Union[
            Sequence1DColumnInputType, Iterable[Sequence1DColumnInputType]
        ] = None,
        order: Optional[int] = None,
        hidden: bool = False,
        optional: bool = False,
        default: Sequence1DColumnInputType = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
    ) -> None:
        # pylint: disable=too-many-arguments
        """
        Create and optionally fill a 1d-sequence column.

        Args:
            name: Column name.
            values: Optional column values. If a single value, the whole column
                filled with this value.
            order: Optional Spotlight priority order value. `None` means the
                lowest priority.
            hidden: Whether column is hidden in Spotlight.
            optional: Whether column is optional. If `default` other than `None`
                is specified, `optional` is automatically set to `True`.
            default: Value to use by default if column is optional and no value
                or `None` is given.
            description: Optional column description.
            tags: Optional tags for the column.
            x_label: Optional x-axis label.
            y_label: Optional y-axis label. If `None`, column name is taken.

        Example:
            Find an example usage in  :class:`renumics.spotlight.dtypes'.Sequence1D`.
        """
        if y_label is None:
            y_label = name
        self._append_column(
            name,
            Sequence1D,
            values,
            h5py.string_dtype(),
            order,
            hidden,
            optional,
            default,
            description,
            tags,
            x_label=x_label,
            y_label=y_label,
        )

    def append_mesh_column(
        self,
        name: str,
        values: Optional[
            Union[MeshColumnInputType, Iterable[Optional[MeshColumnInputType]]]
        ] = None,
        order: Optional[int] = None,
        hidden: bool = False,
        optional: bool = False,
        default: Optional[MeshColumnInputType] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        lookup: Optional[
            Union[
                BoolType, Iterable[MeshColumnInputType], Dict[str, MeshColumnInputType]
            ]
        ] = None,
        external: bool = False,
    ) -> None:
        # pylint: disable=too-many-arguments
        """
        Create and optionally fill a mesh column.

        Args:
            name: Column name.
            values: Optional column values. If a single value, the whole column
                filled with this value.
            order: Optional Spotlight priority order value. `None` means the
                lowest priority.
            hidden: Whether column is hidden in Spotlight.
            optional: Whether column is optional. If `default` other than `None`
                is specified, `optional` is automatically set to `True`.
            default: Value to use by default if column is optional and no value
                or `None` is given.
            description: Optional column description.
            tags: Optional tags for the column.
            lookup: Optional data lookup/flag for automatic lookup creation.
                If `False` (default if `external` is `True`), never add data to
                lookup.
                If `True` (default if `external` is `False`), add all given
                files to the lookup, do nothing for explicitly given data.
                If lookup is given, store it explicit, further behaviour is as
                for `True`. If lookup is not a dict, keys are created automatically.
            external: Whether column should only contain paths/URLs to data and
                load it on demand.

        Example:
            Find an example usage in  :class:`renumics.spotlight.dtypes'.Mesh`.
        """
        self._append_column(
            name,
            Mesh,
            values,
            h5py.string_dtype(),
            order,
            hidden,
            optional,
            default,
            description,
            tags,
            lookup=not external if lookup is None else lookup,
            external=external,
        )

    def append_image_column(
        self,
        name: str,
        values: Union[ImageColumnInputType, Iterable[ImageColumnInputType]] = None,
        order: Optional[int] = None,
        hidden: bool = False,
        optional: bool = False,
        default: ImageColumnInputType = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        lookup: Optional[
            Union[
                BoolType, Iterable[MeshColumnInputType], Dict[str, MeshColumnInputType]
            ]
        ] = None,
        external: bool = False,
    ) -> None:
        # pylint: disable=too-many-arguments
        """
        Create and optionally fill an image column.

        Args:
            name: Column name.
            values: Optional column values. If a single value, the whole column
                filled with this value.
            order: Optional Spotlight priority order value. `None` means the
                lowest priority.
            hidden: Whether column is hidden in Spotlight.
            optional: Whether column is optional. If `default` other than `None`
                is specified, `optional` is automatically set to `True`.
            default: Value to use by default if column is optional and no value
                or `None` is given.
            description: Optional column description.
            tags: Optional tags for the column.
            lookup: Optional data lookup/flag for automatic lookup creation.
                If `False` (default if `external` is `True`), never add data to
                lookup.
                If `True` (default if `external` is `False`), add all given
                files to the lookup, do nothing for explicitly given data.
                If lookup is given, store it explicit, further behaviour is as
                for `True`. If lookup is not a dict, keys are created automatically.
            external: Whether column should only contain paths/URLs to data and
                load it on demand.

        Example:
            Find an example usage in  :class:`renumics.spotlight.dtypes'.Image`.
        """
        self._append_column(
            name,
            Image,
            values,
            h5py.string_dtype(),
            order,
            hidden,
            optional,
            default,
            description,
            tags,
            lookup=not external if lookup is None else lookup,
            external=external,
        )

    def append_audio_column(
        self,
        name: str,
        values: Optional[
            Union[AudioColumnInputType, Iterable[AudioColumnInputType]]
        ] = None,
        order: Optional[int] = None,
        hidden: bool = False,
        optional: bool = False,
        default: ImageColumnInputType = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        lookup: Optional[
            Union[
                BoolType, Iterable[MeshColumnInputType], Dict[str, MeshColumnInputType]
            ]
        ] = None,
        external: bool = False,
        lossy: Optional[bool] = None,
    ) -> None:
        # pylint: disable=too-many-arguments
        """
        Create and optionally fill an audio column.

        Args:
            name: Column name.
            values: Optional column values. If a single value, the whole column
                filled with this value.
            order: Optional Spotlight priority order value. `None` means the
                lowest priority.
            hidden: Whether column is hidden in Spotlight.
            optional: Whether column is optional. If `default` other than `None`
                is specified, `optional` is automatically set to `True`.
            default: Value to use by default if column is optional and no value
                or `None` is given.
            description: Optional column description.
            tags: Optional tags for the column.
            lookup: Optional data lookup/flag for automatic lookup creation.
                If `False` (default if `external` is `True`), never add data to
                lookup.
                If `True` (default if `external` is `False`), add all given
                files to the lookup, do nothing for explicitly given data.
                If lookup is given, store it explicit, further behaviour is as
                for `True`. If lookup is not a dict, keys are created automatically.
            external: Whether column should only contain paths/URLs to data and
                load it on demand.
            lossy: Whether to store data lossy or lossless (default if
                `external` is `False`). Not recomended to use with
                `external=True` since it requires on demand transcoding which
                slows down the execution.

        Example:
            Find an example usage in :class:`renumics.spotlight.dtypes'.Audio`.
        """
        attrs = {}
        if lossy is None and external is False:
            lossy = False
        if lossy is not None:
            attrs["lossy"] = lossy
        self._append_column(
            name,
            Audio,
            values,
            h5py.string_dtype(),
            order,
            hidden,
            optional,
            default,
            description,
            tags,
            lookup=not external if lookup is None else lookup,
            external=external,
            **attrs,
        )

    def append_video_column(
        self,
        name: str,
        values: Optional[
            Union[VideoColumnInputType, Iterable[VideoColumnInputType]]
        ] = None,
        order: Optional[int] = None,
        hidden: bool = False,
        optional: bool = False,
        default: VideoColumnInputType = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        lookup: Optional[
            Union[
                BoolType, Iterable[MeshColumnInputType], Dict[str, MeshColumnInputType]
            ]
        ] = None,
        external: bool = False,
    ) -> None:
        # pylint: disable=too-many-arguments
        """
        Create and optionally fill an video column.

        Args:
            name: Column name.
            values: Optional column values. If a single value, the whole column
                filled with this value.
            order: Optional Spotlight priority order value. `None` means the
                lowest priority.
            hidden: Whether column is hidden in Spotlight.
            optional: Whether column is optional. If `default` other than `None`
                is specified, `optional` is automatically set to `True`.
            default: Value to use by default if column is optional and no value
                or `None` is given.
            description: Optional column description.
            tags: Optional tags for the column.
            lookup: Optional data lookup/flag for automatic lookup creation.
                If `False` (default if `external` is `True`), never add data to
                lookup.
                If `True` (default if `external` is `False`), add all given
                files to the lookup, do nothing for explicitly given data.
                If lookup is given, store it explicit, further behaviour is as
                for `True`. If lookup is not a dict, keys are created automatically.
            external: Whether column should only contain paths/URLs to data and
                load it on demand.
        """
        self._append_column(
            name,
            Video,
            values,
            h5py.string_dtype(),
            order,
            hidden,
            optional,
            default,
            description,
            tags,
            lookup=not external if lookup is None else lookup,
            external=external,
        )

    def append_window_column(
        self,
        name: str,
        values: Optional[
            Union[WindowColumnInputType, Iterable[WindowColumnInputType]]
        ] = None,
        order: Optional[int] = None,
        hidden: bool = False,
        optional: bool = False,
        default: WindowColumnInputType = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        editable: bool = True,
    ) -> None:
        # pylint: disable=too-many-arguments
        """
        Create and optionally fill window column.

        Args:
            name: Column name.
            values: Optional column values. If a single value, the whole column
                filled with this value.
            order: Optional Spotlight priority order value. `None` means the
                lowest priority.
            hidden: Whether column is hidden in Spotlight.
            optional: Whether column is optional. If `default` other than `None`
                is specified, `optional` is automatically set to `True`.
            default: Value to use by default if column is optional and no value
                or `None` is given.
            description: Optional column description.
            tags: Optional tags for the column.
            editable: Whether column is editable in Spotlight.

        Example:
            Find an example usage in :class:`renumics.spotlight.dtypes'.Window`.
        """
        self._append_column(
            name,
            Window,
            values,
            np.dtype("float32"),
            order,
            hidden,
            optional,
            default,
            description,
            tags,
            editable=editable,
        )

    def append_column(
        self,
        name: str,
        column_type: Type[ColumnType],
        values: Union[ColumnInputType, Iterable[ColumnInputType]] = None,
        order: Optional[int] = None,
        hidden: bool = False,
        optional: bool = False,
        default: ColumnInputType = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        **attrs: Optional[Union[str, bool]],
    ) -> None:
        """
        Create and optionally fill a dataset column of the given type.

        Args:
            name: Column name.
            column_type: Column type.
            values: Optional column values. If a single value, the whole column
                filled with this value.
            order: Optional Spotlight priority order value. `None` means the
                lowest priority.
            hidden: Whether column is hidden in Spotlight.
            optional: Whether column is optional. If `default` other than `None`
                is specified, `optional` is automatically set to `True`.
            default: Value to use by default if column is optional and no value
                or `None` is given.
            description: Optional column description.
            tags: Optional tags for the column.
            attrs: Optional arguments for the respective append column method.

        Example:
            >>> from renumics.spotlight import Dataset
            >>> with Dataset("docs/example.h5", "w") as dataset:
            ...     dataset.append_column("int", int, range(5))
            ...     dataset.append_column("float", float, 1.0)
            ...     dataset.append_column("bool", bool, True)
            >>> with Dataset("docs/example.h5", "r") as dataset:
            ...     print(len(dataset))
            ...     print(sorted(dataset.keys()))
            5
            ['bool', 'float', 'int']
            >>> with Dataset("docs/example.h5", "r") as dataset:
            ...     print(dataset["int"])
            ...     print(dataset["bool"])
            ...     print(dataset["float"])
            [0 1 2 3 4]
            [ True  True  True  True  True]
            [1. 1. 1. 1. 1.]
        """
        # pylint: disable=too-many-arguments, too-many-branches
        if column_type is bool:
            append_column_fn: Callable = self.append_bool_column
        elif column_type is int:
            append_column_fn = self.append_int_column
        elif column_type is float:
            append_column_fn = self.append_float_column
        elif column_type is str:
            append_column_fn = self.append_string_column
        elif column_type is datetime:
            append_column_fn = self.append_datetime_column
        elif column_type is np.ndarray:
            append_column_fn = self.append_array_column
        elif column_type is Embedding:
            append_column_fn = self.append_embedding_column
        elif column_type is Image:
            append_column_fn = self.append_image_column
        elif column_type is Mesh:
            append_column_fn = self.append_mesh_column
        elif column_type is Sequence1D:
            append_column_fn = self.append_sequence_1d_column
        elif column_type is Audio:
            append_column_fn = self.append_audio_column
        elif column_type is Category:
            append_column_fn = self.append_categorical_column
        elif column_type is Video:
            append_column_fn = self.append_video_column
        elif column_type is Window:
            append_column_fn = self.append_window_column
        else:
            raise exceptions.InvalidDTypeError(f"Unknown column type: {column_type}.")
        append_column_fn(
            name=name,
            values=values,
            order=order,
            hidden=hidden,
            optional=optional,
            default=default,
            description=description,
            tags=tags,
            **attrs,
        )

    def append_row(self, **values: ColumnInputType) -> None:
        """
        Append a row to the dataset.

        Args:
            values: A mapping column name -> value. Keys of `values` should
                match dataset column names exactly except for optional columns.

        Example:
            >>> from renumics.spotlight import Dataset
            >>> with Dataset("docs/example.h5", "w") as dataset:
            ...     dataset.append_bool_column("bool_values")
            ...     dataset.append_float_column("float_values")
            >>> data = {"bool_values":True, "float_values":0.2}
            >>> with Dataset("docs/example.h5", "a") as dataset:
            ...     dataset.append_row(**data)
            ...     dataset.append_row(**data)
            ...     print(dataset["float_values", 1])
            0.2
        """
        self._assert_is_writable()

        if not self._column_names:
            raise exceptions.InvalidRowError(
                "Cannot write a row, dataset has no columns."
            )
        values = self._encode_row(values)

        try:
            for column_name, value in values.items():
                column = self._h5_file[column_name]
                column.resize(self._length + 1, axis=0)
                column[-1] = value
        except Exception as e:
            self._rollback(self._length)
            raise e

        self._length += 1
        self._update_internal_columns(index=-1)
        self._update_generation_id()

    def append_dataset(self, dataset: "Dataset") -> None:
        """
        Append a dataset to the current dataset row-wise.
        """
        length = self._length
        try:
            for row in dataset.iterrows():
                self.append_row(**row)
        except Exception as e:
            if self._length > length:
                self._rollback(length)
                self._length = length
                self._update_internal_columns()
            raise e

    def insert_row(self, index: IndexType, values: Dict[str, ColumnInputType]) -> None:
        """
        Insert a row into the dataset at the given index.

        Example:
            >>> from renumics.spotlight import Dataset
            >>> with Dataset("example.h5", "w") as dataset:
            ...     dataset.append_float_column("floats", [-1.0, 0.0, 1.0])
            ...     dataset.append_int_column("ints", [-1, 0, 2])
            ...     print(len(dataset))
            ...     print(dataset["floats"])
            ...     print(dataset["ints"])
            3
            [-1.  0.  1.]
            [-1  0  2]
            >>> with Dataset("example.h5", "a") as dataset:
            ...     dataset.insert_row(2, {"floats": float("nan"), "ints": 1000})
            ...     dataset.insert_row(-3, {"floats": 3.14, "ints": -1000})
            ...     print(len(dataset))
            ...     print(dataset["floats"])
            ...     print(dataset["ints"])
            5
            [-1.    3.14  0.     nan  1.  ]
            [   -1 -1000     0  1000     2]
        """
        self._assert_is_writable()
        self._assert_index_exists(index, check_type=True)
        index = cast(int, index)
        length = len(self)
        if index < 0:
            index += length
        for column_name in self.keys() + INTERNAL_COLUMN_NAMES:
            column = self._h5_file[column_name]
            column.resize(length + 1, axis=0)
            raw_values = column[index:-1]
            if self._get_column_type(column) is Embedding:
                raw_values = list(raw_values)
            column[index + 1 :] = raw_values
        self._length += 1
        try:
            self._set_row(index, values)
        except Exception as e:
            del self[index]
            raise e
        self._update_generation_id()

    @overload
    def pop(self, item: str) -> np.ndarray:
        ...

    @overload
    def pop(self, item: IndexType) -> Dict[str, Optional[ColumnType]]:
        ...

    def pop(
        self, item: Union[str, IndexType]
    ) -> Union[np.ndarray, Dict[str, Optional[ColumnType]]]:
        """
        Delete a dataset column or row and return it.
        """
        x = self[item]
        del self[item]
        return x

    def isnull(self, column_name: str) -> np.ndarray:
        """
        Get missing values mask for the given column.

        `None`, `NaN` and category "" values are mapped to `True`. So null-mask
        for columns of type `bool`, `int` and `string` always has only `False` values.
        A `Window` is mapped on `True` only if both start and end are `NaN`.
        """
        # pylint: disable=too-many-return-statements
        self._assert_is_opened()
        self._assert_column_exists(column_name, internal=True)
        column = self._h5_file[column_name]
        raw_values = column[()]

        column_type = self._get_column_type(column)
        if self._is_ref_column(column):
            return ~raw_values.astype(bool)
        if column_type is datetime:
            return np.array([raw_value in ["", b""] for raw_value in raw_values])
        if column_type is float:
            return np.isnan(raw_values)
        if column_type is Category:
            return raw_values == -1
        if column_type is Window:
            return np.isnan(raw_values).all(axis=1)
        if column_type is Embedding:
            return np.array([len(x) == 0 for x in raw_values])
        return np.full(len(self), False)

    def notnull(self, column_name: str) -> np.ndarray:
        """
        Get non-missing values mask for the given column.

        `None`, `NaN` and category "" values are mapped to `False`. So non-null-mask
        for columns of type `bool`, `int` and `string` always has only `True` values.
        A `Window` is mapped on `True` if at least one of its values is not `NaN`.
        """
        return ~self.isnull(column_name)

    def rename_column(self, old_name: str, new_name: str) -> None:
        """
        Rename a dataset column.
        """
        self._assert_is_writable()
        self._assert_column_exists(old_name)
        self.check_column_name(new_name)
        self._assert_column_not_exists(new_name)
        self._h5_file[new_name] = self._h5_file[old_name]
        if f"__group__/{old_name}" in self._h5_file:
            self._h5_file["__group__"].move(old_name, new_name)
        del self._h5_file[old_name]
        self._column_names.discard(old_name)
        self._column_names.add(new_name)
        self._update_generation_id()

    def prune(self) -> None:
        """
        Rebuild the whole dataset with the same content.

        This method can be useful after column deletions, in order to decrease
        the dataset file size.
        """
        # pylint: disable=too-many-nested-blocks, too-many-branches
        self._assert_is_opened()
        column_names = self._column_names
        # Internal columns could be not appended yet, then do not copy them.
        for column_name in INTERNAL_COLUMN_NAMES:
            if column_name in self._h5_file and isinstance(
                self._h5_file[column_name], h5py.Dataset
            ):
                column_names.add(column_name)
        with TemporaryDirectory() as temp_dir:
            new_dataset = os.path.join(temp_dir, "dataset.h5")
            with h5py.File(new_dataset, "w") as h5_file:
                # Copy top-level meta-information, if presented.
                for attr_name, attr in self._h5_file.attrs.items():
                    h5_file.attrs[attr_name] = attr
                for column_name in column_names:
                    column = self._h5_file[column_name]
                    new_column = h5_file.create_dataset(
                        column.name,
                        column.shape,
                        column.dtype,
                        maxshape=column.maxshape,
                    )
                    for attr_name, attr in column.attrs.items():
                        new_column.attrs[attr_name] = attr
                    raw_values = column[()]
                    if self._is_ref_column(column):
                        if h5py.check_string_dtype(column.dtype):
                            # New-style string refs.
                            for ref in raw_values:
                                if ref:
                                    h5_dataset = self._resolve_ref(ref, column_name)
                                    if h5_dataset.name not in h5_file:
                                        h5_file.create_dataset(
                                            h5_dataset.name, data=h5_dataset[()]
                                        )
                        else:
                            # Old-style refs.
                            refs = []
                            for ref in raw_values:
                                if ref:
                                    h5_dataset = self._resolve_ref(ref, column_name)
                                    if h5_dataset.name in h5_file:
                                        new_h5_dataset = h5_file[h5_dataset.name]
                                    else:
                                        new_h5_dataset = h5_file.create_dataset(
                                            h5_dataset.name, data=h5_dataset[()]
                                        )
                                    refs.append(new_h5_dataset.ref)
                                else:
                                    refs.append(None)
                            raw_values = refs
                    if self._get_column_type(column) is Embedding:
                        raw_values = list(raw_values)
                    new_column[:] = raw_values
            self.close()
            shutil.move(new_dataset, os.path.realpath(self._filepath))
            self.open()

    @overload
    def get_column_type(
        self, name: str, as_string: Literal[False] = False
    ) -> Type[ColumnType]:
        ...

    @overload
    def get_column_type(self, name: str, as_string: Literal[True]) -> str:
        ...

    def get_column_type(
        self, name: str, as_string: bool = False
    ) -> Union[Type[ColumnType], str]:
        """
        Get type of dataset column.

        Args:
            name: Column name.
            as_string: Get internal name of the column type.

        Example:
            >>> from renumics.spotlight import Dataset
            >>> with Dataset("docs/example.h5", "w") as dataset:
            ...     dataset.append_bool_column("bool")
            ...     dataset.append_datetime_column("datetime")
            ...     dataset.append_array_column("array")
            ...     dataset.append_mesh_column("mesh")
            >>> with Dataset("docs/example.h5", "r") as dataset:
            ...     for column_name in sorted(dataset.keys()):
            ...         print(column_name, dataset.get_column_type(column_name))
            array <class 'numpy.ndarray'>
            bool <class 'bool'>
            datetime <class 'datetime.datetime'>
            mesh <class 'renumics.spotlight.dtypes.Mesh'>
            >>> with Dataset("docs/example.h5", "r") as dataset:
            ...     for column_name in sorted(dataset.keys()):
            ...         print(column_name, dataset.get_column_type(column_name, True))
            array array
            bool bool
            datetime datetime
            mesh Mesh
        """
        self._assert_is_opened()
        if not isinstance(name, str):
            raise TypeError(
                f"`item` argument should be a string, but value {name} of type "
                f"`{type(name)}` received.`"
            )
        self._assert_column_exists(name, internal=True)
        type_name = self._h5_file[name].attrs["type"]
        if as_string:
            return type_name
        return get_column_type(type_name)

    def get_column_attributes(
        self, name: str
    ) -> Dict[
        str,
        Optional[
            Union[
                bool,
                int,
                str,
                ColumnType,
                Dict[str, int],
                Dict[str, FileBasedColumnType],
            ]
        ],
    ]:
        """
        Get attributes of a column. Available but unset attributes contain None.

        Args:
            name: Column name.

        Example:
            >>> from renumics.spotlight import Dataset
            >>> with Dataset("docs/example.h5", "w") as dataset:
            ...     dataset.append_int_column("int", range(5))
            ...     dataset.append_int_column(
            ...         "int1",
            ...         hidden=True,
            ...         default=10,
            ...         description="integer column",
            ...         tags=["important"],
            ...         editable=False,
            ...     )
            >>> with Dataset("docs/example.h5", "r") as dataset:
            ...     attributes = dataset.get_column_attributes("int")
            ...     for key in sorted(attributes.keys()):
            ...         print(key, attributes[key])
            default None
            description None
            editable True
            hidden False
            optional False
            order None
            tags None
            >>> with Dataset("docs/example.h5", "r") as dataset:
            ...     attributes = dataset.get_column_attributes("int1")
            ...     for key in sorted(attributes.keys()):
            ...         print(key, attributes[key])
            default 10
            description integer column
            editable False
            hidden True
            optional True
            order None
            tags ['important']
        """
        self._assert_is_opened()
        if not isinstance(name, str):
            raise TypeError(
                f"`item` argument should be a string, but value {name} of type "
                f"`{type(name)}` received.`"
            )
        self._assert_column_exists(name, internal=True)

        column = self._h5_file[name]
        column_attrs = column.attrs
        column_type = self._get_column_type(column_attrs)
        allowed_attributes = self._user_column_attributes(column_type)

        attrs: Dict[
            str,
            Optional[
                Union[
                    bool,
                    int,
                    str,
                    ColumnType,
                    Dict[str, int],
                    Dict[str, FileBasedColumnType],
                ]
            ],
        ] = {attribute_name: None for attribute_name in allowed_attributes}

        attrs.update(
            {
                attribute_name: attribute_type(column_attrs[attribute_name])
                if not attribute_type == object
                else column_attrs[attribute_name]
                for attribute_name, attribute_type in allowed_attributes.items()
                if attribute_name in column_attrs
            }
        )

        if "categories" in attrs:
            if column_attrs.get("category_keys") is not None:
                attrs["categories"] = dict(
                    zip(
                        column_attrs.get("category_keys"),
                        column_attrs.get("category_values"),
                    )
                )
        elif "lookup" in attrs:
            if column_attrs.get("lookup_keys") is not None:
                attrs["lookup"] = {  # type: ignore
                    key: self._decode_value(ref, column)
                    for key, ref in zip(
                        column_attrs.get("lookup_keys"),
                        column_attrs.get("lookup_values"),
                    )
                }
            else:
                attrs["lookup"] = False

        default: _EncodedColumnType = attrs.get("default")
        if default is not None:
            attrs["default"] = self._decode_value(default, column)

        return attrs

    def _assert_valid_attribute(
        self, attribute_name: str, attribute_value: ColumnInputType, column_name: str
    ) -> None:
        column = self._h5_file.get(column_name)
        column_type = self._get_column_type(column)

        allowed_attributes = self._user_column_attributes(column_type)
        if attribute_name not in allowed_attributes:
            raise exceptions.InvalidAttributeError(
                f'Setting an attribute with the name "{attribute_name}" for column '
                f'"{column_name}" is not allowed. '
                f'Allowed attribute names for "{column_type}" '
                f'are: "{list(allowed_attributes.keys())}"'
            )
        if not isinstance(attribute_value, allowed_attributes[attribute_name]):
            raise exceptions.InvalidAttributeError(
                f'Attribute "{attribute_name}" for column "{column_name}" '
                f"should be an {allowed_attributes[attribute_name]} or `None`, but "
                f"value {attribute_value} of type `{type(attribute_value)}` received."
            )
        if (
            attribute_name == "optional"
            and not attribute_value
            and column.attrs.get("optional")
        ):
            raise exceptions.InvalidAttributeError(
                f'Invalid `optional` argument for column "{column_name}" of '
                f"type {column_type}. Columns can not be changed from "
                f"`optional=False` to `optional=True`."
            )
        if attribute_name == "tags" and not all(
            isinstance(tag, str) for tag in attribute_value
        ):
            raise exceptions.InvalidAttributeError(
                f'Invalid `tags` argument for column "{column_name}" of type '
                f"{column_type}. Tags should be a `list of str`."
            )

    @staticmethod
    def _write_lookup(
        attrs: h5py.AttributeManager,
        keys: Union[List, np.ndarray],
        values: Union[List, np.ndarray],
        column_name: str,
    ) -> None:
        try:
            attrs["lookup_keys"] = keys
            attrs["lookup_values"] = values
        except RuntimeError as e:
            raise exceptions.InvalidAttributeError(
                f"It seems that you have too many ({len(keys)}) unique values to "
                f"store them in a lookup (~4000). To further write new data into "
                f'column "{column_name}", you have to first disable the lookup:'
                f'\n\t`dataset.set_column_attributes("{column_name}", lookup=False)`'
                f"\nAlternatively, you can disable the lookup at column creation, e.g.:"
                f"\n\t`dataset.append_<type>_column(<name>, lookup=False)`"
            ) from e

    def set_column_attributes(
        self,
        name: str,
        order: Optional[int] = None,
        hidden: Optional[bool] = None,
        optional: Optional[bool] = None,
        default: ColumnInputType = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        **attrs: Any,
    ) -> None:
        # pylint: disable=too-many-arguments, too-many-locals
        # pylint: disable=too-many-branches, too-many-statements
        """
        Set attributes of a column.

        Args:
            name: Column name.
            order: Optional Spotlight priority order value. `None` means the
                lowest priority.
            hidden: Whether column is hidden in Spotlight.
            optional: Whether column is optional. If `default` other than `None`
                is specified, `optional` is automatically set to `True`.
            default: Value to use by default if column is optional and no value
                or `None` is given.
            description: Optional column description.
            tags: Optional tags for the column.
            attrs: Optional more ColumnType specific attributes .
        """
        self._assert_is_writable()
        if not isinstance(name, str):
            raise TypeError(
                f"`name` argument should be a string, but value {name} of type "
                f"`{type(name)}` received.`"
            )
        self._assert_column_exists(name)

        if default is not None:
            optional = True

        attrs["order"] = order
        attrs["hidden"] = hidden
        attrs["optional"] = optional
        attrs["description"] = description
        attrs["tags"] = tags

        attrs = {k: v for k, v in attrs.items() if v is not None}

        column = self._h5_file[name]
        column_type = self._get_column_type(column)

        if "lookup" in attrs:
            lookup = attrs["lookup"]
            if lookup in (True, np.bool_(True)):
                attrs["lookup"] = {}
            elif lookup in (False, np.bool_(False)):
                if "lookup_values" in column.attrs:
                    for ref in column.attrs["lookup_values"]:
                        try:
                            del self._resolve_ref(ref, name).attrs["key"]
                        except (KeyError, ValueError):
                            ...
                    del column.attrs["lookup_keys"], column.attrs["lookup_values"]
                del attrs["lookup"]

        for attribute_name, attribute_value in attrs.items():
            self._assert_valid_attribute(attribute_name, attribute_value, name)

        if "categories" in attrs:
            if any(not v == np.int32(v) for v in attrs["categories"].values()):
                raise exceptions.InvalidAttributeError(
                    f'Attribute "categories" for column "{name}" contains '
                    "invalid dict - values must be convertible to np.int32."
                )
            if any(not isinstance(v, str) for v in attrs["categories"].keys()):
                raise exceptions.InvalidAttributeError(
                    f'Attribute "categories" for column "{name}" contains '
                    "invalid dict - keys must be of type str."
                )
            if any(v == "" for v in attrs["categories"].keys()):
                raise exceptions.InvalidAttributeError(
                    f'Attribute "categories" for column "{name}" contains '
                    'invalid dict - "" (empty string) is no allowed as category key.'
                )
            if len(attrs["categories"].values()) > len(
                set(attrs["categories"].values())
            ):
                raise exceptions.InvalidAttributeError(
                    f'Attribute "categories" for column "{name}" contains '
                    "invalid dict - keys and values must be unique"
                )
            if column.attrs.get("category_keys") is not None:
                values_must_include = column[:]
                if "default" in column.attrs:
                    values_must_include = np.append(
                        values_must_include, column.attrs["default"]
                    )
                missing_values = [
                    encoded_value
                    for encoded_value in values_must_include
                    if encoded_value not in attrs["categories"].values()
                ]
                if any(missing_values):
                    raise exceptions.InvalidAttributeError(
                        f'Attribute "categories" for column "{name}" '
                        f"should include an entry for all values (and the default value) "
                        f"of the column ({set(column[:])}), but "
                        f"entries(s) having values {set(missing_values)} are missing."
                    )

            attrs["category_keys"] = list(map(str, attrs["categories"].keys()))
            attrs["category_values"] = np.array(
                list(attrs["categories"].values()), dtype=np.int32
            )
            del attrs["categories"]

        if "lookup" in attrs:
            lookup = attrs.pop("lookup")
            if "lookup_values" in column.attrs:
                raise exceptions.InvalidAttributeError(
                    f'Lookup for the column "{name}" already set, cannot reset it.'
                )
            lookup_keys = []
            lookup_values = []
            for key, value in lookup.items():
                ref = self._encode_value(value, column)
                self._resolve_ref(ref, name).attrs["key"] = key
                lookup_keys.append(key)
                lookup_values.append(ref)
            self._write_lookup(
                column.attrs,
                np.array(lookup_keys, dtype=h5py.string_dtype()),
                np.array(lookup_values, dtype=h5py.string_dtype()),
                name,
            )

        if "lossy" in attrs:
            lossy = attrs["lossy"]
            attrs["format"] = "mp3" if lossy else "flac"
            if len(column) > 0 and (
                column.attrs.get("lossy") != lossy
                or column.attrs.get("format") != attrs.get("format")
            ):
                raise exceptions.InvalidAttributeError(
                    "Cannot change `lossy` attribute after column creation."
                )

        column.attrs.update(attrs)

        if attrs.get("optional"):
            old_default = column.attrs.pop("default", None)
            # Set new default value.
            try:
                if default is None and old_default is None:
                    default = self._default_default(column_type)
                    if (
                        default is None
                        and column_type is Embedding
                        and not self._is_ref_column(column)
                    ):
                        # For a non-ref `Embedding` column, replace `None` with an empty array.
                        default = np.empty(0, column.dtype.metadata["vlen"])
                if column_type is Category and default != "":
                    if default not in column.attrs["category_keys"]:
                        column.attrs["category_values"] = np.append(
                            column.attrs["category_values"],
                            max(column.attrs["category_values"] + 1),
                        ).astype(dtype=np.int32)
                        column.attrs["category_keys"] = np.append(
                            column.attrs["category_keys"], np.array(default)
                        )
                if default is not None:
                    encoded_value = self._encode_value(default, column)
                    if column_type is datetime and encoded_value is None:
                        encoded_value = ""
                    column.attrs["default"] = encoded_value

            except Exception as e:
                # Rollback
                if old_default is not None:
                    column.attrs["default"] = old_default
                raise e
        self._update_generation_id()

    def _repr_html_(self) -> str:
        return self._pretty_table().get_html_string()

    def _pretty_table(self) -> prettytable.PrettyTable:
        """
        Get `PrettyTable` representation of the dataset.
        """

        def _format(value: _EncodedColumnType, ref_type_name: str) -> str:
            """
            Get string representation of a dataset value.
            """
            if value is None:
                return ""
            if isinstance(value, h5py.Reference):
                return f"<{ref_type_name}>" if value else ""
            return str(value)

        self._assert_is_opened()
        required_keys = (
            "type",
            "order",
            "hidden",
            "optional",
            "default",
            "description",
            "tags",
        )
        table = prettytable.PrettyTable()
        column_names = sorted(self._column_names)
        columns = [self._h5_file[column_name] for column_name in column_names]
        column_reprs = []
        for column in columns:
            attrs = column.attrs
            type_name = attrs["type"]
            column_type = get_column_type(type_name)
            optional_keys = set(
                self._user_column_attributes(column_type).keys()
            ).difference(required_keys)
            column_reprs.append(
                [
                    key + ": " + _format(attrs.get(key), type_name)
                    for key in required_keys + tuple(sorted(optional_keys))
                ]
            )
        column_repr_length = max((len(x) for x in column_reprs), default=0)
        for column_repr in column_reprs:
            column_repr.extend([""] * (column_repr_length - len(column_repr)))
        for column_name, column_repr, column in zip(
            column_names, column_reprs, columns
        ):
            type_name = column.attrs["type"]
            column_repr.extend(_format(value, type_name) for value in column)
            table.add_column(column_name, column_repr)
        return table

    def _append_column(
        self,
        name: str,
        column_type: Type[ColumnType],
        values: Union[ColumnInputType, Iterable[ColumnInputType]],
        dtype: np.dtype,
        order: Optional[int] = None,
        hidden: bool = True,
        optional: bool = False,
        default: ColumnInputType = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        **attrs: Any,
    ) -> None:
        # pylint: disable=too-many-arguments, too-many-locals
        self._assert_is_writable()
        self.check_column_name(name)
        self._assert_column_not_exists(name)
        # Here, only do expensive logic which *should not* be applied in the
        # `set_column_attributes` method.
        shape: Tuple[int, ...] = (0,)
        maxshape: Tuple[Optional[int], ...] = (None,)
        if column_type is Category:
            categories = attrs.get("categories", None)
            if categories is None:
                # Values are given, but no categories.
                if is_iterable(values):
                    values = list(values)
                    categories = set(values)
                else:
                    categories = {values}
                categories.difference_update({"", None})
            if is_iterable(categories) and not isinstance(categories, dict):
                # dict is forced to preserve the order.
                categories = list(dict.fromkeys(categories, None).keys())
                attrs["categories"] = dict(zip(categories, range(len(categories))))
            # Otherwise, exception about type will be raised later in the
            # `set_column_attributes` method.
        elif column_type is Window:
            shape = (0, 2)
            maxshape = (None, 2)
        elif issubclass(column_type, _BaseFileBasedData):
            lookup = attrs.get("lookup", None)
            if is_iterable(lookup) and not isinstance(lookup, dict):
                # Assume that we can keep all the lookup values in memory.
                attrs["lookup"] = {str(i): v for i, v in enumerate(lookup)}
        try:
            column = self._h5_file.create_dataset(name, shape, dtype, maxshape=maxshape)
            self._column_names.add(name)
            column.attrs["type"] = get_column_type_name(column_type)
            self.set_column_attributes(
                name,
                order,
                hidden,
                optional,
                default,
                description,
                tags,
                **attrs,
            )
            self._set_column(column, values)
        except Exception as e:
            if name in self._h5_file:
                del self._h5_file[name]
            try:
                del self._h5_file[f"__group__/{name}"]
            except KeyError:
                pass
            self._column_names.discard(name)
            raise e
        self._update_generation_id()

    def _set_column(
        self,
        column: h5py.Dataset,
        values: Union[ColumnInputType, Iterable[ColumnInputType]],
        indices: Union[None, slice, List[Union[int, bool]], np.ndarray] = None,
        preserve_values: bool = False,
    ) -> None:
        # pylint: disable=too-many-branches, too-many-statements
        column_name = self._get_column_name(column)
        row_wise_filling_message = (
            f"Dataset has initialized, but unfilled columns and should be "
            f"filled row-wise, but values received for column "
            f'"{column_name}".'
        )
        attrs = column.attrs

        # Prepare indices.
        if indices is None:
            column_indices = values_indices = slice(None)  # equivalent to `[:]`.
            indices_length = self._length
        else:
            # We can only write unique sorted indices to `h5py` column, so
            # prepare such indices.
            try:
                column_indices = np.arange(self._length, dtype=int)[indices]
            except Exception as e:
                raise exceptions.InvalidIndexError(
                    f"Indices {indices} of type `{type(indices)}` do not match "
                    f"to the dataset with the length {self._length}."
                ) from e
            indices_length = len(column_indices)  # type: ignore
            if indices_length == 0:
                # e.g.: `dataset[column_name, []] = values`.
                logger.warning(
                    "No values set because the given indices reference no elements."
                )
                return
            column_indices, values_indices = np.unique(
                column_indices, return_index=True
            )
            if len(cast(np.ndarray, column_indices)) != indices_length:
                # For now, forbid non-unique indices.
                raise exceptions.InvalidIndexError(
                    "When setting multiple values in a column, indices should be unique."
                )
            # Fix for non-unique indices.
            # indices, values_indices = np.unique(indices[::-1], return_index=True)
            # values_indices = indices_length - values_indices
        target_column_length = self._length

        encoded_values: Union[np.ndarray, List[_EncodedColumnType]]
        if is_iterable(values):
            # Single windows and embeddings also come here.
            encoded_values = self._encode_values(values, column)
            if len(encoded_values) != indices_length:
                if indices_length == 0:
                    # That is, `self._length` is 0 (otherwise already returned).
                    if len(self._column_names) == 1:
                        target_column_length = indices_length = len(encoded_values)
                    else:
                        raise exceptions.InvalidShapeError(row_wise_filling_message)
                elif len(encoded_values) == 1:
                    # Stretch the values for all indices.
                    encoded_values = np.broadcast_to(
                        encoded_values, (indices_length, *encoded_values.shape[1:])
                    )
                else:
                    raise exceptions.InvalidShapeError(
                        f"{indices_length} values or a single value expected "
                        f'for column "{column_name}", but '
                        f"{len(encoded_values)} values received."
                    )
            elif indices_length == 0:
                # Set an empty column with 0 values, i.e. do nothing.
                return
            else:
                # Reorder values according to the given indices.
                encoded_values = encoded_values[values_indices]
            if self._get_column_type(column) is Embedding:
                encoded_values = list(encoded_values)
        elif values is not None:
            # A single value is given. `Window` and `Embedding` values should
            # never go here, because they are always iterable, even a single value.
            if self._length == 0:
                if len(self._column_names) == 1:
                    target_column_length = indices_length = 1
                else:
                    raise exceptions.InvalidShapeError(row_wise_filling_message)
            encoded_values = [
                self._encode_value(cast(ColumnInputType, values), column)
            ] * indices_length
        elif self._length == 0:
            return
        elif attrs.get("optional", False):
            encoded_values = column.attrs.get(
                "default", "" if h5py.check_string_dtype(column.dtype) else None
            )
        else:
            raise exceptions.InvalidDTypeError(
                f'Dataset has been initialized and values for non-optional column "{column_name}" '
                f"must be provided on column creation. But no values were provided."
            )

        old_values = column[:] if preserve_values else None
        try:
            column.resize(target_column_length, axis=0)
            column[column_indices] = encoded_values
        except Exception as e:
            if preserve_values:
                column.resize(self._length, axis=0)
                column[:] = old_values
            raise e
        self._length = target_column_length
        self._update_internal_columns(column_indices)

    def _set_row(self, index: IndexType, row: Dict[str, ColumnInputType]) -> None:
        old_row = {
            column_name: self._h5_file[column_name][index]
            for column_name in self._column_names
        }
        try:
            row = self._encode_row(row)
            for column_name, value in row.items():
                self._h5_file[column_name][index] = value
        except Exception as e:
            # Rollback changed row.
            for column_name, item_value in old_row.items():
                self._h5_file[column_name][index] = item_value
            raise e
        self._update_internal_columns(index)

    def _set_value(
        self,
        column: h5py.Dataset,
        index: IndexType,
        value: ColumnInputType,
        check_index: bool = False,
    ) -> None:
        if check_index:
            self._assert_index_exists(index)
        old_value = column[index]
        try:
            value = self._encode_value(value, column)
            if value is None:
                attrs = column.attrs
                if attrs.get("optional", False):
                    value = attrs.get("default", None)
            column[index] = value
        except Exception as e:
            column[index] = old_value
            raise e
        self._update_internal_columns(index)

    def _get_column(
        self,
        column: h5py.Dataset,
        indices: Optional[Indices1DType] = None,
    ) -> np.ndarray:
        """
        Read and decode values of the given existing column.

        If `indices` is `None`, get the whole column. Otherwise, all possible
        indices supported by one-dimensional numpy arrays should work.
        """
        if indices is None:
            values = column[()]
        else:
            # We can only read unique increasing indices from h5py,
            # so prepare such indices, take values and remap them back.
            try:
                indices = np.arange(len(self), dtype=int)[indices]
            except Exception as e:
                raise exceptions.InvalidIndexError(
                    f"Indices {indices} of type `{type(indices)}` do not match "
                    f"to the dataset with the length {self._length}."
                ) from e
            indices, mapping = np.unique(indices, return_inverse=True)
            values = column[indices][mapping]
        return self._decode_values(values, column)

    def _decode_values(self, values: np.ndarray, column: h5py.Dataset) -> np.ndarray:
        column_type = self._get_column_type(column)
        if column.attrs.get("external", False):
            column_type = cast(Type[ExternalColumnType], column_type)
            return self._decode_external_values(values, column_type)
        if self._is_ref_column(column):
            column_type = cast(Type[RefColumnType], column_type)
            return self._decode_ref_values(values, column, column_type)
        column_type = cast(Type[SimpleColumnType], column_type)
        return self._decode_simple_values(values, column, column_type)

    @staticmethod
    def _decode_simple_values(
        values: np.ndarray, column: h5py.Dataset, column_type: Type[SimpleColumnType]
    ) -> np.ndarray:
        if column_type is Category:
            mapping = dict(
                zip(column.attrs["category_values"], column.attrs["category_keys"])
            )
            mapping[-1] = ""
            return np.array([mapping[x] for x in values], dtype=str)
        if h5py.check_string_dtype(column.dtype):
            # `column_type` is `str` or `datetime`.
            values = np.array([x.decode("utf-8") for x in values])
            if column_type is str:
                return values
            # Decode datetimes.
            return np.array(
                [None if x == "" else datetime.fromisoformat(x) for x in values],
                dtype=object,
            )
        if column_type is Embedding:
            null_mask = [len(x) == 0 for x in values]
            values[null_mask] = None
        # For column types `bool`, `int`, `float` or `Window`, return the array as-is.
        return values

    def _decode_ref_values(
        self, values: np.ndarray, column: h5py.Dataset, column_type: Type[RefColumnType]
    ) -> np.ndarray:
        column_name = self._get_column_name(column)
        if column_type in (np.ndarray, Embedding):
            # `np.array([<...>], dtype=object)` creation does not work for
            # some cases and erases dtypes of sub-arrays, so we use assignment.
            decoded_values = np.empty(len(values), dtype=object)
            decoded_values[:] = [
                self._decode_ref_value(ref, column_type, column_name) for ref in values
            ]
            return decoded_values
        return np.array(
            [self._decode_ref_value(ref, column_type, column_name) for ref in values],
            dtype=object,
        )

    def _decode_external_values(
        self, values: np.ndarray, column_type: Type[ExternalColumnType]
    ) -> np.ndarray:
        return np.array(
            [self._decode_external_value(value, column_type) for value in values],
            dtype=object,
        )

    def _get_value(
        self, column: h5py.Dataset, index: IndexType, check_index: bool = False
    ) -> Optional[ColumnType]:
        if check_index:
            self._assert_index_exists(index)
        value = column[index]
        return self._decode_value(value, column)

    def _get_column_names_and_length(self) -> Tuple[Set[str], int]:
        """
        Parse valid columns of the same length from a H5 file. Valid columns
        should have a known type stored in column attributes and have the same
        length.

        If valid columns of different length found, take the columns of the most
        frequent (mode) length only. If multiple modes found, take the columns
        of the greatest length.

        Returns:
            column_names: Names of the chosen columns.
            length: Length of the chosen columns.
        """
        names = []
        lengths = []
        for name in self._h5_file:
            h5_dataset = self._h5_file[name]
            if isinstance(h5_dataset, h5py.Dataset):
                try:
                    self._get_column_type(h5_dataset)
                except (KeyError, exceptions.InvalidDTypeError):
                    continue
                else:
                    names.append(name)
                    shape = h5_dataset.shape
                    lengths.append(shape[0] if shape else 0)
        max_count = 0
        length_modes = []
        for length in set(lengths):
            count = lengths.count(length)
            if count == max_count:
                length_modes.append(length)
            elif count > max_count:
                length_modes = [length]
                max_count = count
        length = max(length_modes, default=0)
        column_names = {
            column_name
            for column_name, column_length in zip(names, lengths)
            if column_length == length
        }
        if len(column_names) < len(names):
            logger.info(
                f"Columns with different length found. The greatest of the "
                f"most frequent length ({length}) chosen and only columns with "
                f"this length taken as the dataset's columns."
            )
        return column_names, length

    def _encode_values(
        self, values: Iterable[ColumnInputType], column: h5py.Dataset
    ) -> np.ndarray:
        if self._is_ref_column(column):
            values = cast(Iterable[RefColumnInputType], values)
            return self._encode_ref_values(values, column)
        values = cast(Iterable[SimpleColumnInputType], values)
        return self._encode_simple_values(values, column)

    def _encode_simple_values(
        self, values: Iterable[SimpleColumnInputType], column: h5py.Dataset
    ) -> np.ndarray:
        # pylint: disable=too-many-branches, too-many-return-statements
        column_type = cast(Type[SimpleColumnType], self._get_column_type(column))
        if column_type is Category:
            mapping = dict(
                zip(column.attrs["category_keys"], column.attrs["category_values"])
            )
            if column.attrs.get("optional", False):
                default = column.attrs.get("default", -1)
                mapping[None] = default
                if default == -1:
                    mapping[""] = -1
            try:
                # Map values and save as the right int type.
                return np.array([mapping[x] for x in values], dtype=column.dtype)
            except KeyError as e:
                column_name = self._get_column_name(column)
                raise exceptions.InvalidValueError(
                    f'Values for the categorical column "{column_name}" '
                    f"contain unknown categories."
                ) from e
        if column_type is datetime:
            if _check_valid_array(values, column_type):
                encoded_values = np.array(
                    [None if x is None else x.isoformat() for x in values.tolist()]
                )
            else:
                encoded_values = np.array(
                    [self._encode_value(value, column) for value in values]
                )
            if np.issubdtype(encoded_values.dtype, str):
                # That means, we have all strings in array, no `None`s.
                return encoded_values
            return self._replace_none(encoded_values, column)
        if column_type is Window:
            encoded_values = self._asarray(values, column, column_type)
            if encoded_values.ndim == 1:
                if len(encoded_values) == 2:
                    # A single window, reshape it to an array.
                    return np.broadcast_to(values, (1, 2))
                if len(encoded_values) == 0:
                    # An empty array, reshape for compatibility.
                    return np.broadcast_to(values, (0, 2))
            elif encoded_values.ndim == 2 and encoded_values.shape[1] == 2:
                # An array with valid windows.
                return encoded_values
            column_name = self._get_column_name(column)
            raise exceptions.InvalidShapeError(
                f'Input values to `Window` column "{column_name}" should have '
                f"one of shapes (2,) (a single window) or (n, 2) (multiple "
                f"windows), but values with shape {encoded_values.shape} received."
            )
        if column_type is Embedding:
            if _check_valid_array(values, column_type):
                # This is the only case we can handle fast and easily, otherwise
                # embedding should go through `_encode_value` element-wise.
                if values.ndim == 1:
                    # Handle 1-dimensional input as a single embedding.
                    self._assert_valid_or_set_embedding_shape(values.shape, column)
                    values_list = list(np.broadcast_to(values, (1, len(values))))
                elif values.ndim == 2:
                    self._assert_valid_or_set_embedding_shape(values.shape[1:], column)
                    values_list = list(values)
                else:
                    raise exceptions.InvalidShapeError(
                        f"Input values for an `Embedding` column should have 1 "
                        f"or 2 dimensions, but values with shape "
                        f"{values.shape} received."
                    )
            else:
                values_list = [self._encode_value(value, column) for value in values]
            encoded_values = np.empty(len(values_list), dtype=object)
            encoded_values[:] = values_list
            encoded_values = self._replace_none(encoded_values, column)
            return encoded_values
        # column type is `bool`, `int`, `float` or `str`.
        encoded_values = self._asarray(values, column, column_type)
        if encoded_values.ndim == 1:
            return encoded_values
        column_name = self._get_column_name(column)
        raise exceptions.InvalidShapeError(
            f'Input values to `{column_type}` column "{column_name}" should '
            f"be 1-dimensional, but values with shape {encoded_values.shape} "
            f"received."
        )

    def _encode_ref_values(
        self, values: Iterable[RefColumnInputType], column: h5py.Dataset
    ) -> np.ndarray:
        encoded_values = np.array(
            [self._encode_value(value, column) for value in values]
        )
        encoded_values = self._replace_none(encoded_values, column)
        if h5py.check_string_dtype(column.dtype):
            encoded_values[encoded_values == np.array(None)] = ""
        return encoded_values

    def _asarray(
        self,
        values: Iterable[SimpleColumnInputType],
        column: h5py.Dataset,
        column_type: Type[SimpleColumnType],
    ) -> np.ndarray:
        if isinstance(values, np.ndarray):
            if _check_valid_value_dtype(values.dtype, column_type):
                return values
        elif not isinstance(values, (list, tuple, range)):
            # Make iterables, dicts etc. convertible to an array.
            values = list(values)
        # Array can contain `None`s, so do not infer dtype.
        encoded_values = np.array(values, dtype=object)
        encoded_values = self._replace_none(encoded_values, column)
        try:
            # At the moment, `None`s are already replaced, so try optimistic
            # dtype conversion.
            return np.array(encoded_values.tolist(), dtype=column.dtype)
        except TypeError as e:
            column_name = self._get_column_name(column)
            raise exceptions.InvalidValueError(
                f'Values for the column "{column_name}" of type {column_type} '
                f"are not convertible to the dtype {column.dtype}."
            ) from e

    @staticmethod
    def _replace_none(values: np.ndarray, column: h5py.Dataset) -> np.ndarray:
        """replace all None entries with the default value for the column"""

        # none_mask = values == np.array(None)
        none_mask = [x is None for x in values]

        if not any(none_mask):
            # no nones present -> just return all the values
            return values

        if not column.attrs.get("optional", False):
            raise exceptions.InvalidDTypeError(
                f"`values` argument for non-optional column "
                f'"{column.name.lstrip("/")}" contains `None` values.'
            )

        try:
            default = column.attrs["default"]
        except KeyError:
            # no default value -> keep None as None
            return values

        if not isinstance(default, str):
            default = default.tolist()

        # Replace `None`s with the default value.
        default_array = np.empty(1, dtype=object)
        default_array[0] = default
        values[none_mask] = default_array
        return values

    def _encode_row(
        self, values: Dict[str, ColumnInputType]
    ) -> Dict[str, _EncodedColumnType]:
        """
        Encode a single row for writing to dataset.

        This method also replaces missed and `None` values with default values
        if possible and checks row consistency.
        """
        # Encode row.
        values = values.copy()
        for column_name in self._column_names:
            values[column_name] = self._encode_value(
                values.get(column_name), self._h5_file[column_name]
            )
            if values[column_name] is None:
                column = self._h5_file[column_name]
                attrs = column.attrs
                if attrs.get("optional", False):
                    values[column_name] = attrs.get(
                        "default", "" if h5py.check_string_dtype(column.dtype) else None
                    )
        # Check row consistency.
        if values.keys() == self._column_names:
            return values
        error_message = (
            "Keys of `values` mismatch column names, even with updated "
            "default values."
        )
        missing_keys = self._column_names - set(values.keys())
        if missing_keys:
            error_message += (
                '\n\tKeys "' + '", "'.join(missing_keys) + '" missing in ' "`values`."
            )
        excessive_keys = set(values.keys()) - self._column_names
        if excessive_keys:
            error_message += (
                '\n\tColumns "'
                + '", "'.join(excessive_keys)
                + '" should be appended to the dataset.'
            )
        raise exceptions.InvalidRowError(error_message)

    def _encode_value(
        self, value: ColumnInputType, column: h5py.Dataset
    ) -> _EncodedColumnType:
        """
        Encode a value for writing into a column, *but* do not replace `None`s
        with default value (only check that this exists), since batch replace
        should be faster.
        """
        column_name = self._get_column_name(column)
        attrs = column.attrs
        if value is None:
            if attrs.get("optional", False):
                return value
            raise exceptions.InvalidDTypeError(
                f'No value given for the non-optional column "{column_name}".'
            )
        if attrs.get("external", False):
            value = cast(PathOrURLType, value)
            return self._encode_external_value(value, column)
        column_type = self._get_column_type(attrs)
        if self._is_ref_column(column):
            value = cast(RefColumnInputType, value)
            return self._encode_ref_value(value, column, column_type, column_name)
        value = cast(SimpleColumnInputType, value)
        return self._encode_simple_value(value, column, column_type, column_name)

    def _encode_simple_value(
        self,
        value: SimpleColumnInputType,
        column: h5py.Dataset,
        column_type: Type[ColumnType],
        column_name: str,
    ) -> _EncodedColumnType:
        """
        Encode a non-ref value, e.g. bool, int, float, str, datetime, Category,
        Window and Embedding (in last versions).

        Value *cannot* be `None` already.
        """
        attrs = column.attrs
        if column_type is Category:
            categories = dict(
                zip(attrs.get("category_keys"), attrs.get("category_values"))
            )
            if attrs.get("optional", False) and attrs.get("default", -1) == -1:
                categories[""] = -1
            if value not in categories.keys():
                raise exceptions.InvalidValueError(
                    f"Values for {column_type} column "
                    f'"{column.name.lstrip("/")}" should be one of '
                    f"{list(categories.keys())} "
                    f"but value '{value}' received."
                )
            return categories[value]
        if column_type is Window:
            value = np.asarray(value, dtype=column.dtype)
            if value.shape == (2,):
                return value
            raise exceptions.InvalidDTypeError(
                f"Windows should consist of 2 values, but window of shape "
                f"{value.shape} received for column {column_name}."
            )
        if column_type is Embedding:
            # `Embedding` column is not a ref column.
            if isinstance(value, Embedding):
                value = value.encode(attrs.get("format", None))
            value = np.asarray(value, dtype=column.dtype.metadata["vlen"])
            self._assert_valid_or_set_embedding_shape(value.shape, column)
            return value
        self._assert_valid_value_type(value, column_type, column_name)
        if isinstance(value, np.str_):
            return value.tolist()
        if isinstance(value, np.datetime64):
            value = value.astype(datetime)
        if isinstance(value, datetime):
            return value.isoformat()
        return value

    def _encode_ref_value(
        self,
        value: RefColumnInputType,
        column: h5py.Dataset,
        column_type: Type[ColumnType],
        column_name: str,
    ) -> _EncodedColumnType:
        """
        Encode a ref value, e.g. np.ndarray, Sequence1D, Image, Mesh, Audio,
        Video, and Embedding (in old versions).

        Value *cannot* be `None` already.
        """
        # pylint: disable=too-many-branches
        attrs = column.attrs
        key: Optional[str] = None
        lookup_keys: List[str] = []
        if column_type is Mesh and isinstance(value, trimesh.Trimesh):
            value = Mesh.from_trimesh(value)
        elif is_file_based_column_type(column_type) and isinstance(
            value, (str, os.PathLike)
        ):
            try:
                lookup_keys = attrs["lookup_keys"].tolist()
            except KeyError:
                pass  # Don't need to search/update, so encode value as usual.
            else:
                key = str(value)
                try:
                    index = lookup_keys.index(key)
                except ValueError:
                    pass  # Index not found, so encode value as usual.
                else:
                    # Return stored ref, do not process data again.
                    return attrs["lookup_values"][index]
            value = column_type.from_file(value)
        if issubclass(column_type, (Embedding, Image, Sequence1D)):
            if not isinstance(value, column_type):
                value = column_type(value)  # type: ignore
            value = value.encode(attrs.get("format", None))  # type: ignore
        elif issubclass(column_type, (Mesh, Audio, Video)):
            self._assert_valid_value_type(value, column_type, column_name)
            value = value.encode(attrs.get("format", None))  # type: ignore
        else:
            value = np.asarray(value)
        # `value` can be a `np.ndarray` or a `np.void`.
        if isinstance(value, np.ndarray):
            # Check dtype.
            self._assert_valid_or_set_value_dtype(value.dtype, column)
            if column_type is Embedding:
                self._assert_valid_or_set_embedding_shape(value.shape, column)
        dataset_name = str(uuid.uuid4()) if key is None else escape_dataset_name(key)
        h5_dataset = self._h5_file.create_dataset(
            f"__group__/{column_name}/{dataset_name}", data=value
        )
        if h5py.check_ref_dtype(column.dtype):
            ref = h5_dataset.ref  # Legacy handling.
        else:
            ref = dataset_name
        if key is not None:
            # `lookup_keys` is not `None`, so `lookup_values` too.
            self._write_lookup(
                attrs,
                lookup_keys + [key],
                np.concatenate(  # pylint: disable=unexpected-keyword-arg
                    (attrs["lookup_values"], [ref]),
                    dtype=column.dtype,
                ),
                column_name,
            )
            h5_dataset.attrs["key"] = key
        return ref

    def _encode_external_value(self, value: PathOrURLType, column: h5py.Dataset) -> str:
        """
        Encode an external value, i.e. an URL or a path.
        Value *should not* be a `None`.

        Column *must* be an external column (H5 dataset with string dtype).
        """
        if not isinstance(value, (str, os.PathLike)):
            column_name = self._get_column_name(column)
            raise exceptions.InvalidDTypeError(
                f'For the external column "{column_name}" values should '
                f"contain only URLs and/or paths (`str` or `os.PathLike`), but "
                f"value {value} of type {type(value)} received."
            )
        value = str(value)
        attrs = column.attrs
        lookup_keys: Optional[List[str]] = None
        # We still can have a lookup.
        try:
            lookup_keys = attrs["lookup_keys"].tolist()
        except KeyError:
            pass  # Don't need to search/update, so encode value as usual.
        else:
            lookup_keys = cast(List[str], lookup_keys)
            try:
                index = lookup_keys.index(value)
            except ValueError:
                pass  # Index not found, so encode value as usual.
            else:
                # Return stored value, do not process data again.
                return attrs["lookup_values"][index]
        if not (validators.url(value) or os.path.isfile(value)):
            logger.warning(
                f'File "{value}" not found, but still written into '
                f"the dataset. If it does not appear at the reading "
                f"time, a `None` will be returned."
            )
        if lookup_keys is not None:
            # `lookup_keys` is not `None`, so `lookup_values` too.
            self._write_lookup(
                attrs,
                lookup_keys + [value],
                np.concatenate(  # pylint: disable=unexpected-keyword-arg
                    (attrs["lookup_values"], [value]),
                    dtype=column.dtype,
                ),
                self._get_column_name(column),
            )
        return value

    @staticmethod
    def _assert_valid_value_type(
        value: ColumnInputType, column_type: Type[ColumnType], column_name: str
    ) -> None:
        if not _check_valid_value_type(value, column_type):
            allowed_types = (column_type,) + _ALLOWED_COLUMN_TYPES.get(column_type, ())
            raise exceptions.InvalidDTypeError(
                f'Values for non-optional {column_type} column "{column_name}" '
                f"should be one of {allowed_types} instances, but value "
                f"{value} of type `{type(value)}` received."
            )

    def _decode_value(
        self,
        value: Union[
            np.bool_, np.integer, np.floating, bytes, str, np.ndarray, h5py.Reference
        ],
        column: h5py.Dataset,
    ) -> Optional[ColumnType]:
        column_type = self._get_column_type(column)
        if column.attrs.get("external", False):
            value = cast(bytes, value)
            column_type = cast(Type[ExternalColumnType], column_type)
            return self._decode_external_value(value, column_type)
        if self._is_ref_column(column):
            value = cast(Union[bytes, h5py.Reference], value)
            column_type = cast(Type[RefColumnType], column_type)
            column_name = self._get_column_name(column)
            return self._decode_ref_value(value, column_type, column_name)
        value = cast(Union[np.bool_, np.integer, np.floating, bytes, np.ndarray], value)
        column_type = cast(Type[SimpleColumnType], column_type)
        return self._decode_simple_value(value, column, column_type)

    @staticmethod
    def _decode_simple_value(
        value: Union[np.bool_, np.integer, np.floating, bytes, str, np.ndarray],
        column: h5py.Dataset,
        column_type: Type[SimpleColumnType],
    ) -> Optional[Union[bool, int, float, str, datetime, np.ndarray]]:
        # pylint: disable=too-many-return-statements
        if column_type is Window:
            value = cast(np.ndarray, value)
            return value
        if column_type is Embedding:
            value = cast(np.ndarray, value)
            if len(value) == 0:
                return None
            return value
        if column_type is Category:
            mapping = dict(
                zip(column.attrs["category_values"], column.attrs["category_keys"])
            )
            if column.attrs.get("optional", False) and column.attrs.get(
                "default", None
            ) in (-1, None):
                mapping[-1] = ""
            return mapping[value]
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        if column_type is datetime:
            value = cast(str, value)
            if value == "":
                return None
            return datetime.fromisoformat(value)
        value = cast(Union[np.bool_, np.integer, np.floating, str], value)
        column_type = cast(Type[Union[bool, int, float, str]], column_type)
        return column_type(value)

    def _decode_ref_value(
        self,
        ref: Union[bytes, str, h5py.Reference],
        column_type: Type[RefColumnType],
        column_name: str,
    ) -> Optional[Union[np.ndarray, Audio, Image, Mesh, Sequence1D, Video]]:
        # Value can be a H5 reference or a string reference.
        if not ref:
            return None
        value = self._resolve_ref(ref, column_name)[()]
        value = cast(Union[np.ndarray, np.void], value)
        if column_type in (np.ndarray, Embedding):
            return value
        column_type = cast(
            Type[Union[Audio, Image, Mesh, Sequence1D, Video]], column_type
        )
        return column_type.decode(value)

    def _decode_external_value(
        self,
        value: Union[str, bytes],
        column_type: Type[ExternalColumnType],
    ) -> Optional[ExternalColumnType]:
        if not value:
            return None
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        file = prepare_path_or_url(value, os.path.dirname(self._filepath))
        try:
            return column_type.from_file(file)
        except Exception:  # pylint: disable=broad-except
            # No matter what happens, we should not crash, but warn instead.
            logger.warning(
                f"File or URL {value} either does not exist or could not be "
                f"loaded by the class `spotlight.{column_type.__name__}`."
                f"Instead of script failure the value will be replaced with "
                f"`None`."
            )
            return None

    def _append_internal_columns(self) -> None:
        """
        Append internal columns to the first created or imported dataset.
        """
        internal_column_values = [self._get_username(), get_current_datetime()]
        for column_name, value in zip(INTERNAL_COLUMN_NAMES, internal_column_values):
            try:
                column = self._h5_file[column_name]
            except KeyError:
                # Internal column does not exist, create.
                value = cast(Union[str, datetime], value)
                self.append_column(
                    column_name, type(value), value if self._length > 0 else None
                )
            else:
                # Internal column exists, check type.
                try:
                    type_name = column.attrs["type"]
                except KeyError as e:
                    raise exceptions.InconsistentDatasetError(
                        f'Internal column "{column_name}" already exists, but '
                        f"has no type stored in attributes. Remove or rename "
                        f"the respective h5 dataset."
                    ) from e
                column_type = get_column_type(type_name)
                if column_type is not type(value):
                    raise exceptions.InconsistentDatasetError(
                        f'Internal column "{column_name}" already exists, '
                        f"but has invalid type `{column_type}` "
                        f"(`{type(value)}` expected). Remove or rename "
                        f"the respective h5 dataset."
                    )

    def _update_internal_columns(
        self, index: Optional[Union[IndexType, Indices1DType]] = None
    ) -> None:
        """
        Update internal columns.

        Indices should be prepared (slice with positive step or unique sorted sequence).
        """
        internal_column_values = [
            self._get_username(),
            get_current_datetime().isoformat(),
        ]
        for column_name, value in zip(INTERNAL_COLUMN_NAMES, internal_column_values):
            if column_name not in self._h5_file:
                continue
            column = self._h5_file[column_name]
            column_length = len(column)
            if column_length != self._length:
                column.resize(self._length, axis=0)
            if column_length < self._length:
                # A row/rows appended, append values.
                column[column_length - self._length - 1 :] = value
            elif column_length == self._length:
                if index is None:
                    # A column appended, update all values.
                    column[:] = value
                else:
                    # A row/rows chenged, update values according to `index`.
                    column[index] = value
            # Otherwise, all columns deleted. All values removed through resize.

    def _update_generation_id(self) -> None:
        self._h5_file.attrs["spotlight_generation_id"] += 1

    def _rollback(self, length: int) -> None:
        """
        Rollback dataset after a failed row/dataset append.

        Args:
            length: Target length of dataset after rollback.
        """
        for column_name in self._column_names:
            column = self._h5_file[column_name]
            column_length = column.shape[0] if column.shape else 0
            if column_length <= length:
                continue
            column.resize(length, axis=0)

    def _resolve_ref(
        self, ref: Union[h5py.Reference, str, bytes], column_name: str
    ) -> h5py.Dataset:
        if isinstance(ref, bytes):
            ref = ref.decode("utf-8")
        if isinstance(ref, str):
            return self._h5_file[f"__group__/{column_name}/{ref}"]
        return self._h5_file[ref]

    @staticmethod
    def _get_username() -> str:
        return ""

    @staticmethod
    def _get_column_type(
        x: Union[str, h5py.Dataset, h5py.AttributeManager]
    ) -> Type[ColumnType]:
        """
        Get column type by its name, or extract it from `h5py` entities.
        """
        if isinstance(x, str):
            return get_column_type(x)
        if isinstance(x, h5py.Dataset):
            return get_column_type(x.attrs["type"])
        if isinstance(x, h5py.AttributeManager):
            return get_column_type(x["type"])
        raise TypeError(
            f"Argument is expected to ba an instance of type `str`, `h5py.Dataset` "
            f"or `h5py.AttributeManager`, but `x` of type {type(x)} received."
        )

    @staticmethod
    def _get_column_name(column: h5py.Dataset) -> str:
        """
        Get name of a column.
        """
        return column.name.split("/")[-1]

    @staticmethod
    def _is_ref_column(column: h5py.Dataset) -> bool:
        """
        Check if a column is ref column.
        """
        return column.attrs["type"] in REF_COLUMN_TYPE_NAMES and (
            h5py.check_string_dtype(column.dtype) or h5py.check_ref_dtype(column.dtype)
        )

    @staticmethod
    def _check_mode(mode: str) -> None:
        """
        Check an open mode.
        """
        if mode not in ("r", "r+", "w", "w-", "x", "a"):
            raise exceptions.InvalidModeError(
                f'Open mode should be one of "r", "r+", "w", "w-"/"x" or "a" '
                f"but {mode} received."
            )

    @staticmethod
    def check_column_name(name: str) -> None:
        """
        Check a column name.
        """
        if not isinstance(name, str):
            raise exceptions.InvalidColumnNameError(
                f"Column name should be a string, but value {name} of type "
                f"`{type(name)}` received."
            )
        if "/" in name:
            raise exceptions.InvalidColumnNameError(
                f'Column name should not contain "/", but "{name}" received.'
            )
        if name == "__group__":
            raise exceptions.InvalidColumnNameError(
                'Column name "__group__" is reserved for internal use.'
            )

    def _is_writable(self) -> bool:
        """
        Check whether dataset is writable.
        """
        return self._mode != "r"

    def _assert_is_opened(self) -> None:
        if self._closed:
            raise exceptions.ClosedDatasetError("Dataset is closed.")

    def _assert_is_writable(self) -> None:
        self._assert_is_opened()
        if not self._is_writable():
            raise exceptions.ReadOnlyDatasetError("Dataset is read-only.")

    def _assert_column_not_exists(self, name: str) -> None:
        if name in self._column_names:
            raise exceptions.ColumnExistsError(f'Column "{name}" already exists.')
        if name in self._h5_file:
            raise exceptions.ColumnExistsError(
                f'"{name}" name is already used in the H5 file '
                f'"{self._filepath}" (but not as a Spotlight dataset column).'
            )

    def _assert_column_exists(
        self, name: str, check_type: bool = False, internal: bool = False
    ) -> None:
        if check_type and not isinstance(name, str):
            raise TypeError(
                f"Column name should be a string, but value {name} of type "
                f"`{type(name)}` received.`"
            )
        column_names = (
            self._column_names
            if not internal
            else self._column_names.union(INTERNAL_COLUMN_NAMES)
        )
        if name not in column_names:
            raise exceptions.ColumnNotExistsError(f'Column "{name}" does not exist.')

    def _assert_index_exists(self, index: IndexType, check_type: bool = False) -> None:
        if check_type and not is_integer(index):
            raise TypeError(
                f"Dataset index should be an integer, but value {index} of "
                f"type `{type(index)}` received."
            )
        if index < -self._length or index >= self._length:
            raise exceptions.InvalidIndexError(
                f"Row {index} does not exist, dataset has length {self._length}."
            )

    def _assert_valid_or_set_value_dtype(
        self, dtype: np.dtype, column: h5py.Dataset
    ) -> None:
        attrs = column.attrs
        if "value_dtype" in attrs:
            if dtype.str != attrs["value_dtype"]:
                column_name = self._get_column_name(column)
                raise exceptions.InvalidDTypeError(
                    f'Values for {attrs["type"]} column "{column_name}" '
                    f"should have dtype `{np.dtype(attrs['value_dtype'])}`, "
                    f"but value with dtype `{dtype}` received."
                )
        elif issubclass(dtype.type, (np.bool_, np.number)):
            attrs["value_dtype"] = dtype.str
        else:
            column_name = self._get_column_name(column)
            raise exceptions.InvalidDTypeError(
                f'Values for {attrs["type"]} column "{column_name}" should '
                f"have numeric or boolean dtype, but value with dtype {dtype} "
                f"received."
            )

    def _assert_valid_or_set_embedding_shape(
        self, shape: Tuple[int, ...], column: h5py.Dataset
    ) -> None:
        attrs = column.attrs
        if shape == (0,) and attrs.get("optional", False):
            # Do not check shape if an empty array given for an optional column.
            return
        if "value_shape" in attrs:
            if shape != attrs["value_shape"]:
                column_name = self._get_column_name(column)
                raise exceptions.InvalidShapeError(
                    f'Values for `Embedding` column "{column_name}" '
                    f'should have shape {attrs["value_shape"]}, but '
                    f"value with shape {shape} received."
                )
        elif len(shape) == 1 and shape[0] > 0:
            attrs["value_shape"] = shape
        else:
            column_name = self._get_column_name(column)
            raise exceptions.InvalidShapeError(
                f'Values for `Embedding` column "{column_name}" should '
                f"have shape `(num_features,)`, `num_features > 0`, "
                f"but value with shape {shape} received."
            )
