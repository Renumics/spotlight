import uuid
from itertools import islice
from typing import Iterable, List, Union

import numpy as np
import orjson
import pyarrow as pa
import pyarrow.dataset
import pyarrow.types

try:
    # let ray register it's extension types if it is installed
    import ray.data  # noqa
    import ray.air.util.tensor_extensions.arrow  # noqa
except ModuleNotFoundError:
    pass


import renumics.spotlight.dtypes as spotlight_dtypes
from renumics.spotlight.data_source import DataSource
from renumics.spotlight.data_source.data_source import ColumnMetadata
from renumics.spotlight.data_source.decorator import datasource


class UnknownArrowType(Exception):
    """
    We encountered an unknown arrow DataType during type conversion
    """


class UnknownArrowExtensionType(Exception):
    """
    We encountered an unknown arrow Extension Type during type conversion
    """


EMPTY_MAP: spotlight_dtypes.DTypeMap = {}


def iter_batched(values: Iterable, n: int) -> Iterable[tuple]:
    it = iter(values)
    return iter(lambda: tuple(islice(it, n)), ())


@datasource(pyarrow.dataset.Dataset)
@datasource(pyarrow.dataset.FileSystemDataset)
class ArrowDatasetSource(DataSource):
    def __init__(self, source: pyarrow.dataset.Dataset):
        self._dataset = source
        self._intermediate_dtypes: spotlight_dtypes.DTypeMap = self._convert_schema()

        self._semantic_dtypes = {}

        if source.schema.metadata:
            # support hf metadata (only images for now)
            if hf_metadata := orjson.loads(
                source.schema.metadata.get(b"huggingface", "null")
            ):
                features = hf_metadata.get("info", {}).get("features", {})
                for name, feat in features.items():
                    if feat.get("_type") == "Image":
                        self._semantic_dtypes[name] = spotlight_dtypes.image_dtype

    @property
    def column_names(self) -> List[str]:
        return self._dataset.schema.names

    @property
    def intermediate_dtypes(self) -> spotlight_dtypes.DTypeMap:
        return self._intermediate_dtypes

    @property
    def semantic_dtypes(self) -> spotlight_dtypes.DTypeMap:
        return self._semantic_dtypes

    def __len__(self) -> int:
        return self._dataset.count_rows()

    def get_generation_id(self) -> int:
        return 0

    def get_uid(self) -> str:
        return str(uuid.uuid4())

    def get_name(self) -> str:
        return "Arrow Dataset"

    def get_column_values(
        self,
        column_name: str,
        indices: Union[List[int], np.ndarray, slice] = slice(None),
    ) -> np.ndarray:
        try:
            # Import these arrow extension types to ensure that they are registered.
            import ray.air.util.tensor_extensions.arrow  # noqa
        except ModuleNotFoundError:
            pass

        if indices == slice(None):
            table = self._dataset.to_table(columns=[column_name])
        else:
            if isinstance(indices, slice):
                indices = np.array(range(*indices.indices(len(self))))

            table = self._dataset.take(
                indices,
                columns=[column_name],
                batch_size=min(len(indices), 2048),
                batch_readahead=0,
                fragment_readahead=0,
            )

        raw_values = table[column_name]

        dtype = self._intermediate_dtypes.get(column_name)
        if isinstance(dtype, spotlight_dtypes.ArrayDType):
            if dtype.shape is not None:
                shape = [-1 if x is None else x for x in dtype.shape]
                return np.array([np.array(arr).reshape(shape) for arr in raw_values])
            else:
                return raw_values.to_numpy()

        # convert hf image values
        if self._semantic_dtypes.get(column_name) == spotlight_dtypes.image_dtype:
            return np.array(
                [
                    (
                        value["path"].as_py()
                        if value["bytes"].as_py() is None
                        else value["bytes"].as_py()
                    )
                    for value in raw_values
                ],
                dtype=object,
            )
        else:
            return raw_values.to_numpy()

    def get_column_metadata(self, column_name: str) -> ColumnMetadata:
        field_index = self._dataset.schema.get_field_index(column_name)
        field = self._dataset.schema.field(field_index)
        return ColumnMetadata(nullable=field.nullable, editable=False)

    def _convert_schema(self) -> spotlight_dtypes.DTypeMap:
        schema: spotlight_dtypes.DTypeMap = {}
        for field in self._dataset.schema:
            schema[field.name] = _convert_dtype(field)
        print(schema)
        return schema


PA_INTEGER_TYPES = [
    pa.int8(),
    pa.int16(),
    pa.int32(),
    pa.int64(),
    pa.uint8(),
    pa.uint16(),
    pa.uint32(),
    pa.uint64(),
]

PA_FLOAT_TYPES = [pa.float16(), pa.float32(), pa.float64()]


def _convert_dtype(field: pa.Field) -> spotlight_dtypes.DType:
    if field.type == pa.null():
        # should we introduce a `null` dtype?
        return spotlight_dtypes.unknown_dtype
    if field.type == pa.bool_():
        return spotlight_dtypes.bool_dtype
    if field.type in PA_INTEGER_TYPES:
        return spotlight_dtypes.int_dtype
    if field.type in PA_FLOAT_TYPES:
        return spotlight_dtypes.float_dtype
    if field.type in (
        pa.time32("s"),
        pa.time32("ms"),
        pa.time64("us"),
        pa.time64("ns"),
        pa.date32(),
        pa.date64(),
    ):
        return spotlight_dtypes.datetime_dtype
    if isinstance(field.type, pa.TimestampType):
        return spotlight_dtypes.datetime_dtype
    if isinstance(field.type, pa.DurationType):
        return spotlight_dtypes.int_dtype
    if isinstance(field.type, pa.MonthDayNanoIntervalScalar):
        return spotlight_dtypes.SequenceDType(spotlight_dtypes.int_dtype, 3)
    if field.type == pa.binary():
        return spotlight_dtypes.bytes_dtype
    if isinstance(field.type, pa.FixedSizeBinaryType):
        return spotlight_dtypes.bytes_dtype
    if field.type == pa.large_binary():
        return spotlight_dtypes.bytes_dtype
    if field.type in (pa.string(), pa.large_string()):
        return spotlight_dtypes.str_dtype
    if isinstance(field.type, pa.Decimal128Type):
        return spotlight_dtypes.float_dtype
    if isinstance(field.type, pa.ListType):
        return spotlight_dtypes.SequenceDType(_convert_dtype(field.type.value_field))
    if isinstance(field.type, pa.FixedSizeListType):
        return spotlight_dtypes.SequenceDType(
            _convert_dtype(field.type.value_field), field.type.list_size
        )
    if isinstance(field.type, pa.LargeListType):
        return spotlight_dtypes.SequenceDType(_convert_dtype(field.type.value_field))
    if isinstance(field.type, pa.MapType):
        return spotlight_dtypes.unknown_dtype
    if isinstance(field.type, pa.StructType):
        return spotlight_dtypes.unknown_dtype
    if isinstance(field.type, pa.DictionaryType):
        if (field.type.index_type() in PA_INTEGER_TYPES) and (
            field.type.value_type() in (pa.string(), pa.large_string())
        ):
            return spotlight_dtypes.CategoryDType()
        return spotlight_dtypes.unknown_dtype
    if isinstance(field.type, pa.RunEndEncodedType):
        return spotlight_dtypes.SequenceDType(
            _convert_dtype(pa.field("", field.type.value_type))
        )
    if isinstance(field.type, pa.ExtensionType):
        # handle known extensions
        if field.type.extension_name == "ray.data.arrow_tensor":
            return spotlight_dtypes.ArrayDType(shape=field.type.shape)

        raise UnknownArrowExtensionType(field.type.extension_name)

    raise UnknownArrowType(field.type)
