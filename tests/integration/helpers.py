from datetime import datetime, timezone
from typing import Any

import numpy as np

from renumics.spotlight import dtypes
from renumics.spotlight.dataset import VALUE_TYPE_BY_DTYPE_NAME
from renumics.spotlight.dataset.typing import ColumnInputType, OutputType
from renumics.spotlight.media import Audio, Embedding, Image, Mesh, Sequence1D, Video


def _as_datetime64(value: Any) -> np.ndarray:
    """
    Convert a value to `np.datetime64`. Timezone-aware datetimes are converted
    to naive UTC first, since `np.datetime64` cannot represent timezones.
    """
    if isinstance(value, datetime) and value.tzinfo is not None:
        value = value.astimezone(timezone.utc).replace(tzinfo=None)
    return np.array(value, dtype="datetime64[us]")


def approx(
    expected: ColumnInputType, actual: OutputType | None, dtype_name: str
) -> bool:
    """
    Check whether expected and actual dataset values are almost equal.
    """
    if actual is None and expected is None:
        return True

    dtype = dtypes.create_dtype(dtype_name)
    if dtypes.is_scalar_dtype(dtype) or dtypes.is_str_dtype(dtype):
        value_type = VALUE_TYPE_BY_DTYPE_NAME[dtype_name]
        expected_value: np.ndarray = np.array(expected, dtype=value_type)
        actual_value: np.ndarray = np.array(actual, dtype=value_type)
        return approx(expected_value, actual_value, "array")
    if dtypes.is_datetime_dtype(dtype):
        expected_datetime = _as_datetime64(expected)
        actual_datetime = _as_datetime64(actual)
        return approx(expected_datetime, actual_datetime, "array")
    if dtypes.is_category_dtype(dtype):
        expected_category = np.array(expected, dtype="str")
        actual_category = np.array(actual, dtype="str")
        return approx(expected_category, actual_category, "array")
    if dtypes.is_array_dtype(dtype):
        expected_array = np.asarray(expected)
        assert isinstance(actual, np.ndarray)
        if actual.shape != expected_array.shape:
            return False
        if issubclass(expected_array.dtype.type, np.inexact):
            return np.allclose(actual, expected_array, equal_nan=True)
        return actual.tolist() == expected_array.tolist()
    if dtypes.is_window_dtype(dtype):
        expected_window = np.asarray(expected, dtype=float)
        assert isinstance(actual, np.ndarray)
        return approx(expected_window, actual, "array")
    if dtypes.is_embedding_dtype(dtype):
        if isinstance(expected, Embedding):
            expected_embedding = expected
        else:
            expected_embedding = Embedding(expected)  # type: ignore
        assert isinstance(actual, np.ndarray)
        return approx(expected_embedding.data, actual, "array")
    if dtypes.is_sequence_1d_dtype(dtype):
        if isinstance(expected, Sequence1D):
            expected_sequence_1d = expected
        else:
            expected_sequence_1d = Sequence1D(expected)  # type: ignore
        assert isinstance(actual, Sequence1D)
        return approx(expected_sequence_1d.index, actual.index, "array") and approx(
            expected_sequence_1d.value, actual.value, "array"
        )
    if dtypes.is_audio_dtype(dtype):
        assert isinstance(expected, Audio)
        assert isinstance(actual, Audio)
        return (
            approx(expected.data, actual.data, "array")
            and actual.sampling_rate == expected.sampling_rate
        )
    if dtypes.is_image_dtype(dtype):
        if isinstance(expected, Image):
            expected_image = expected
        else:
            expected_image = Image(expected)  # type: ignore
        assert isinstance(actual, Image)
        return approx(expected_image.data, actual.data, "array")
    if dtypes.is_mesh_dtype(dtype):
        assert isinstance(expected, Mesh)
        assert isinstance(actual, Mesh)
        return (
            approx(expected.points, actual.points, "array")
            and approx(expected.triangles, actual.triangles, "array")
            and len(actual.point_displacements) == len(expected.point_displacements)
            and all(
                approx(expected_displacement, actual_displacement, "array")
                for actual_displacement, expected_displacement in zip(
                    actual.point_displacements,
                    expected.point_displacements,
                    strict=True,
                )
            )
            and actual.point_attributes.keys() == expected.point_attributes.keys()
            and all(
                approx(
                    point_attribute,
                    actual.point_attributes[attribute_name],
                    "array",
                )
                for attribute_name, point_attribute in expected.point_attributes.items()
            )
        )
    if dtypes.is_video_dtype(dtype):
        if isinstance(expected, Video):
            expected_video = expected
        else:
            expected_video = Video(expected)  # type: ignore
        assert isinstance(actual, Video)
        return actual.data == expected_video.data
    raise TypeError(f"Invalid type name {dtype_name} received.")
