import uuid
from typing import List, Union

import numpy as np
import pyarrow as pa
import pyarrow.dataset
import pyarrow.types

import renumics.spotlight.dtypes as spotlight_dtypes
from renumics.spotlight.data_source import DataSource
from renumics.spotlight.data_source.data_source import ColumnMetadata
from renumics.spotlight.data_source.decorator import datasource


class UnknownArrowType(Exception):
    """
    We encountered an unknown arrow DataType during type conversion
    """


EMPTY_MAP: spotlight_dtypes.DTypeMap = {}


@datasource(pyarrow.dataset.Dataset)
@datasource(pyarrow.dataset.FileSystemDataset)
class ArrowDatasetSource(DataSource):
    def __init__(self, source: pyarrow.dataset.Dataset):
        self._dataset = source
        self._intermediate_dtypes: spotlight_dtypes.DTypeMap = self._convert_schema()

    @property
    def column_names(self) -> List[str]:
        return self._dataset.schema.names

    @property
    def intermediate_dtypes(self) -> spotlight_dtypes.DTypeMap:
        return self._intermediate_dtypes

    @property
    def semantic_dtypes(self) -> spotlight_dtypes.DTypeMap:
        return EMPTY_MAP

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
        if isinstance(indices, slice):
            indices = np.array(range(*indices.indices(len(self))))

        table = self._dataset.take(indices)
        values = table[column_name]
        return values.to_numpy()

    def get_column_metadata(self, column_name: str) -> ColumnMetadata:
        field_index = self._dataset.schema.get_field_index(column_name)
        field = self._dataset.schema.field(field_index)
        return ColumnMetadata(nullable=field.nullable, editable=False)

    def _convert_schema(self) -> spotlight_dtypes.DTypeMap:
        schema: spotlight_dtypes.DTypeMap = {}
        for field in self._dataset.schema:
            schema[field.name] = _convert_dtype(field)
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

    raise UnknownArrowType()
