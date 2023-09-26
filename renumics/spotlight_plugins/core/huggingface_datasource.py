from typing import List, Optional, Union, cast

import datasets
import numpy as np

from renumics.spotlight.data_source import DataSource
from renumics.spotlight.data_source.decorator import datasource
from renumics.spotlight.dtypes import (
    ArrayDType,
    CategoryDType,
    DType,
    DTypeMap,
    audio_dtype,
    bool_dtype,
    datetime_dtype,
    float_dtype,
    image_dtype,
    int_dtype,
    file_dtype,
    bytes_dtype,
    is_array_dtype,
    is_embedding_dtype,
    is_file_dtype,
    is_float_dtype,
    is_int_dtype,
    str_dtype,
)
from renumics.spotlight.data_source.data_source import ColumnMetadata
from renumics.spotlight.logging import logger


_FeatureType = Union[
    datasets.Value,
    datasets.ClassLabel,
    datasets.Sequence,
    datasets.Array2D,
    datasets.Array3D,
    datasets.Array4D,
    datasets.Array5D,
    datasets.Audio,
    datasets.Image,
    datasets.Translation,
    dict,
    list,
]


class UnsupportedFeature(Exception):
    """
    We encountered an unsupported datasets Feature
    """

    def __init__(self, feature: _FeatureType) -> None:
        super().__init__(f"Unsupported HuggingFace Feature: {type(feature)}")


@datasource(datasets.Dataset)
class HuggingfaceDataSource(DataSource):
    _dataset: datasets.Dataset
    _intermediate_dtypes: DTypeMap
    _guessed_dtypes: DTypeMap

    def __init__(self, source: datasets.Dataset):
        super().__init__(source)
        self._dataset = source
        self._intermediate_dtypes = {
            col: _get_intermediate_dtype(feat)
            for col, feat in self._dataset.features.items()
        }
        self._guessed_dtypes = {}
        for col, feat in self._dataset.features.items():
            guessed_dtype = _guess_semantic_dtype(feat)
            if guessed_dtype:
                self._guessed_dtypes[col] = guessed_dtype

    @property
    def column_names(self) -> List[str]:
        return self._dataset.column_names

    @property
    def intermediate_dtypes(self) -> DTypeMap:
        return self._intermediate_dtypes

    def __len__(self) -> int:
        return len(self._dataset)

    @property
    def semantic_dtypes(self) -> DTypeMap:
        return self._guessed_dtypes

    def get_generation_id(self) -> int:
        return 0

    def get_uid(self) -> str:
        return self._dataset._fingerprint

    def get_name(self) -> str:
        return f"🤗 Dataset {self._dataset.builder_name or ''}"

    def get_column_values(
        self,
        column_name: str,
        indices: Union[List[int], np.ndarray, slice] = slice(None),
    ) -> np.ndarray:
        intermediate_dtype = self._intermediate_dtypes[column_name]

        if isinstance(indices, slice):
            if indices == slice(None):
                raw_values = self._dataset.data[column_name]
            else:
                actual_indices = list(range(len(self._dataset)))[indices]
                raw_values = self._dataset.data[column_name].take(actual_indices)
        else:
            raw_values = self._dataset.data[column_name].take(indices)

        feature = self._dataset.features[column_name]

        if isinstance(feature, datasets.Audio) or isinstance(feature, datasets.Image):
            return np.array(
                [
                    value["path"].as_py()
                    if value["bytes"].as_py() is None
                    else value["bytes"].as_py()
                    for value in raw_values
                ],
                dtype=object,
            )

        if isinstance(feature, dict):
            if is_file_dtype(intermediate_dtype):
                return np.array(
                    [value["bytes"].as_py() for value in raw_values], dtype=object
                )
            else:
                return np.array([str(value) for value in raw_values])

        if isinstance(feature, datasets.Sequence):
            if is_array_dtype(intermediate_dtype):
                values = [
                    _convert_object_array(value) for value in raw_values.to_numpy()
                ]
                return_array = np.empty(len(values), dtype=object)
                return_array[:] = values
                return return_array
            if is_embedding_dtype(intermediate_dtype):
                return raw_values.to_numpy()
            return np.array([str(value) for value in raw_values])

        if isinstance(
            feature,
            (datasets.Array2D, datasets.Array3D, datasets.Array4D, datasets.Array5D),
        ):
            if is_array_dtype(intermediate_dtype):
                values = [
                    _convert_object_array(value) for value in raw_values.to_numpy()
                ]
                return_array = np.empty(len(values), dtype=object)
                return_array[:] = values
                return return_array
            return np.array([str(value) for value in raw_values])

        if isinstance(feature, datasets.Translation):
            return np.array([str(value) for value in raw_values])

        if isinstance(feature, datasets.Value):
            hf_dtype = feature.dtype
            if hf_dtype.startswith("duration"):
                return raw_values.to_numpy().astype(int)
            if hf_dtype.startswith("time32") or hf_dtype.startswith("time64"):
                return raw_values.to_numpy().astype(str)
            if hf_dtype.startswith("timestamp[ns"):
                return raw_values.to_numpy().astype(int)

        return raw_values.to_numpy()

    def get_column_metadata(self, _: str) -> ColumnMetadata:
        return ColumnMetadata(nullable=True, editable=False)


def _guess_semantic_dtype(feature: _FeatureType) -> Optional[DType]:
    if isinstance(feature, datasets.Audio):
        return audio_dtype
    if isinstance(feature, datasets.Image):
        return image_dtype
    return None


def _get_intermediate_dtype(feature: _FeatureType) -> DType:
    if isinstance(feature, datasets.Value):
        hf_dtype = feature.dtype
        if hf_dtype == "bool":
            return bool_dtype
        elif hf_dtype.startswith("int"):
            return int_dtype
        elif hf_dtype.startswith("uint"):
            return int_dtype
        elif hf_dtype.startswith("float"):
            return float_dtype
        elif hf_dtype.startswith("time32"):
            return str_dtype
        elif hf_dtype.startswith("time64"):
            return str_dtype
        elif hf_dtype.startswith("timestamp"):
            if hf_dtype.startswith("timestamp[ns"):
                return int_dtype
            return datetime_dtype
        elif hf_dtype.startswith("date32"):
            return datetime_dtype
        elif hf_dtype.startswith("date64"):
            return datetime_dtype
        elif hf_dtype.startswith("duration"):
            return int_dtype
        elif hf_dtype.startswith("decimal"):
            return float_dtype
        elif hf_dtype == "binary":
            return bytes_dtype
        elif hf_dtype == "large_binary":
            return bytes_dtype
        elif hf_dtype == "string":
            return str_dtype
        elif hf_dtype == "large_string":
            return str_dtype
        else:
            logger.warning(f"Unsupported Hugging Face value dtype: {hf_dtype}.")
            return str_dtype
    elif isinstance(feature, datasets.ClassLabel):
        return CategoryDType(categories=cast(datasets.ClassLabel, feature).names)
    elif isinstance(feature, datasets.Audio):
        return file_dtype
    elif isinstance(feature, datasets.Image):
        return file_dtype
    elif isinstance(feature, datasets.Sequence):
        inner_dtype = _get_intermediate_dtype(feature.feature)
        if is_int_dtype(inner_dtype) or is_float_dtype(inner_dtype):
            return ArrayDType((None if feature.length == -1 else feature.length,))
        if is_array_dtype(inner_dtype):
            if inner_dtype.shape is None:
                return str_dtype
            shape = (
                None if feature.length == -1 else feature.length,
                *inner_dtype.shape,
            )
            if shape.count(None) > 1:
                return str_dtype
            return ArrayDType(shape)
        return str_dtype
    elif isinstance(feature, list):
        inner_dtype = _get_intermediate_dtype(feature[0])
        if is_int_dtype(inner_dtype) or is_float_dtype(inner_dtype):
            return ArrayDType((None,))
        if is_array_dtype(inner_dtype):
            if inner_dtype.shape is None:
                return str_dtype
            shape = (None, *inner_dtype.shape)
            if shape.count(None) > 1:
                return str_dtype
            return ArrayDType(shape)
        return str_dtype
    elif isinstance(
        feature,
        (datasets.Array2D, datasets.Array3D, datasets.Array4D, datasets.Array5D),
    ):
        return ArrayDType(feature.shape)
    elif isinstance(feature, dict):
        if len(feature) == 2 and "bytes" in feature and "path" in feature:
            return file_dtype
        else:
            return str_dtype
    elif isinstance(feature, datasets.Translation):
        return str_dtype
    logger.warning(f"Unsupported Hugging Face feature: {feature}.")
    return str_dtype


def _convert_object_array(value: np.ndarray) -> np.ndarray:
    if value.dtype.type is np.object_:
        return np.array([_convert_object_array(x) for x in value])
    return value
