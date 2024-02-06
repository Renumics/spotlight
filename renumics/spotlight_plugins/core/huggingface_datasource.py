from typing import List, Optional, Union, cast

import datasets
import numpy as np

import renumics.spotlight.dtypes as spotlight_dtypes
from renumics.spotlight.data_source import DataSource
from renumics.spotlight.data_source.data_source import ColumnMetadata
from renumics.spotlight.data_source.decorator import datasource
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
    _intermediate_dtypes: spotlight_dtypes.DTypeMap
    _guessed_dtypes: spotlight_dtypes.DTypeMap

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
    def intermediate_dtypes(self) -> spotlight_dtypes.DTypeMap:
        return self._intermediate_dtypes

    def __len__(self) -> int:
        return len(self._dataset)

    @property
    def semantic_dtypes(self) -> spotlight_dtypes.DTypeMap:
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
                raw_values = self._dataset.data.fast_gather(actual_indices)[column_name]
        else:
            raw_values = self._dataset.data.fast_gather(indices)[column_name]

        feature = self._dataset.features[column_name]

        if isinstance(feature, datasets.Audio) or isinstance(feature, datasets.Image):
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

        if isinstance(feature, dict):
            if spotlight_dtypes.is_file_dtype(intermediate_dtype):
                return np.array(
                    [value["bytes"].as_py() for value in raw_values], dtype=object
                )
            else:
                return np.array([str(value) for value in raw_values])

        if isinstance(feature, datasets.Sequence):
            if spotlight_dtypes.is_array_dtype(intermediate_dtype):
                values = [
                    _convert_object_array(value) for value in raw_values.to_numpy()
                ]
                return_array = np.empty(len(values), dtype=object)
                return_array[:] = values
                return return_array
            if spotlight_dtypes.is_sequence_dtype(intermediate_dtype):
                return raw_values.to_numpy()
            return np.array([str(value) for value in raw_values])

        if isinstance(
            feature,
            (datasets.Array2D, datasets.Array3D, datasets.Array4D, datasets.Array5D),
        ):
            if spotlight_dtypes.is_array_dtype(intermediate_dtype):
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


def _guess_semantic_dtype(feature: _FeatureType) -> Optional[spotlight_dtypes.DType]:
    if isinstance(feature, datasets.Audio):
        return spotlight_dtypes.audio_dtype
    if isinstance(feature, datasets.Image):
        return spotlight_dtypes.image_dtype
    return None


def _get_intermediate_dtype(feature: _FeatureType) -> spotlight_dtypes.DType:
    if isinstance(feature, datasets.Value):
        hf_dtype = feature.dtype
        if hf_dtype == "bool":
            return spotlight_dtypes.bool_dtype
        elif hf_dtype.startswith("int"):
            return spotlight_dtypes.int_dtype
        elif hf_dtype.startswith("uint"):
            return spotlight_dtypes.int_dtype
        elif hf_dtype.startswith("float"):
            return spotlight_dtypes.float_dtype
        elif hf_dtype.startswith("time32"):
            return spotlight_dtypes.str_dtype
        elif hf_dtype.startswith("time64"):
            return spotlight_dtypes.str_dtype
        elif hf_dtype.startswith("timestamp"):
            if hf_dtype.startswith("timestamp[ns"):
                return spotlight_dtypes.int_dtype
            return spotlight_dtypes.datetime_dtype
        elif hf_dtype.startswith("date32"):
            return spotlight_dtypes.datetime_dtype
        elif hf_dtype.startswith("date64"):
            return spotlight_dtypes.datetime_dtype
        elif hf_dtype.startswith("duration"):
            return spotlight_dtypes.int_dtype
        elif hf_dtype.startswith("decimal"):
            return spotlight_dtypes.float_dtype
        elif hf_dtype == "binary":
            return spotlight_dtypes.bytes_dtype
        elif hf_dtype == "large_binary":
            return spotlight_dtypes.bytes_dtype
        elif hf_dtype == "string":
            return spotlight_dtypes.str_dtype
        elif hf_dtype == "large_string":
            return spotlight_dtypes.str_dtype
        else:
            logger.warning(f"Unsupported Hugging Face value dtype: {hf_dtype}.")
            return spotlight_dtypes.str_dtype
    elif isinstance(feature, datasets.ClassLabel):
        return spotlight_dtypes.CategoryDType(
            categories=cast(datasets.ClassLabel, feature).names
        )
    elif isinstance(feature, datasets.Audio):
        return spotlight_dtypes.file_dtype
    elif isinstance(feature, datasets.Image):
        return spotlight_dtypes.file_dtype
    elif isinstance(feature, datasets.Sequence):
        inner_dtype = _get_intermediate_dtype(feature.feature)
        if spotlight_dtypes.is_int_dtype(
            inner_dtype
        ) or spotlight_dtypes.is_float_dtype(inner_dtype):
            return spotlight_dtypes.ArrayDType(
                (None if feature.length == -1 else feature.length,)
            )
        if spotlight_dtypes.is_str_dtype(
            inner_dtype
        ) or spotlight_dtypes.is_category_dtype(inner_dtype):
            return spotlight_dtypes.SequenceDType(
                inner_dtype, None if feature.length == -1 else feature.length
            )
        if spotlight_dtypes.is_array_dtype(inner_dtype):
            assert inner_dtype.shape is not None
            shape = (
                None if feature.length == -1 else feature.length,
                *inner_dtype.shape,
            )
            return spotlight_dtypes.ArrayDType(shape)
        return spotlight_dtypes.str_dtype
    elif isinstance(feature, list):
        inner_dtype = _get_intermediate_dtype(feature[0])
        if spotlight_dtypes.is_int_dtype(
            inner_dtype
        ) or spotlight_dtypes.is_float_dtype(inner_dtype):
            return spotlight_dtypes.ArrayDType((None,))
        if spotlight_dtypes.is_str_dtype(
            inner_dtype
        ) or spotlight_dtypes.is_category_dtype(inner_dtype):
            return spotlight_dtypes.SequenceDType(inner_dtype)
        if spotlight_dtypes.is_array_dtype(inner_dtype):
            assert inner_dtype.shape is not None
            shape = (None, *inner_dtype.shape)
            return spotlight_dtypes.ArrayDType(shape)
        return spotlight_dtypes.str_dtype
    elif isinstance(
        feature,
        (datasets.Array2D, datasets.Array3D, datasets.Array4D, datasets.Array5D),
    ):
        return spotlight_dtypes.ArrayDType(feature.shape)
    elif isinstance(feature, dict):
        if len(feature) == 2 and "bytes" in feature and "path" in feature:
            return spotlight_dtypes.file_dtype
        else:
            return spotlight_dtypes.str_dtype
    elif isinstance(feature, datasets.Translation):
        return spotlight_dtypes.str_dtype
    logger.warning(f"Unsupported Hugging Face feature: {feature}.")
    return spotlight_dtypes.str_dtype


def _convert_object_array(value: np.ndarray) -> np.ndarray:
    if value.dtype.type is np.object_:
        return np.array([_convert_object_array(x) for x in value])
    return value
