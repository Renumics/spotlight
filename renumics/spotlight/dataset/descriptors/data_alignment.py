"""
This module provides utilities for descriptors.
"""

from typing import Tuple

import numpy as np
from scipy import interpolate, signal
from skimage.color import rgba2rgb, rgb2gray
from skimage.transform import resize_local_mean

from renumics.spotlight import (
    Audio,
    Dataset,
    Embedding,
    Image,
    Sequence1D,
    Window,
)
from renumics.spotlight.dataset import exceptions


def align_audio_data(dataset: Dataset, column: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Align data from an audio column.
    """
    # pylint: disable=too-many-locals
    column_type = dataset.get_column_type(column)
    if column_type is not Audio:
        raise exceptions.InvalidDTypeError(
            f'An audio column expected, but column "{column}" of type {column_type} received.'
        )
    notnull_mask = dataset.notnull(column)
    if notnull_mask.sum() == 0:
        # No data to interpolate, so either dataset is empty, or no samples are valid.
        return np.empty((0, 0), dtype=np.float64), notnull_mask
    raw_data = dataset[column, notnull_mask]
    sampling_rates = []
    steps = []
    for sample in raw_data:
        sampling_rates.append(sample.sampling_rate)
        steps.append(len(sample.data))
    # Resample to the least frequent audio sample.
    target_sampling_rate = min(sampling_rates)
    lengths = np.array(steps) / np.array(sampling_rates)
    target_length = lengths.max()
    target_steps = int(np.ceil(target_length * target_sampling_rate))
    data = []
    for sample, sample_steps in zip(raw_data, steps):
        y = sample.data
        if np.issubdtype(y.dtype, np.integer):
            max_value = 2 ** (np.iinfo(y.dtype).bits - 1)
            y = y.astype(np.float64) / max_value
        if y.ndim > 1:
            y = y.mean(axis=-1)
        sampling_rate = sample.sampling_rate
        if sampling_rate != target_sampling_rate:
            ratio = target_sampling_rate / sampling_rate
            n_samples = int(np.ceil(sample_steps * ratio))
            y = signal.resample(y, n_samples, axis=-1)
        padding = np.zeros(target_steps - sample_steps, dtype=y.dtype)
        y = np.append(y, padding)
        data.append(y)
    return np.stack(data), notnull_mask


def align_embedding_data(
    dataset: Dataset, column: str
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Align data from an embedding column.
    """
    column_type = dataset.get_column_type(column)
    if column_type is not Embedding:
        raise exceptions.InvalidDTypeError(
            f'An embedding column expected, but column "{column}" of type {column_type} received.'
        )
    notnull_mask = dataset.notnull(column)
    if notnull_mask.sum() == 0:
        # No data to interpolate, so either dataset is empty, or no samples are valid.
        return np.empty((0, 0), dtype=np.float64), notnull_mask
    return np.array(list(dataset[column, notnull_mask])), notnull_mask


def align_image_data(dataset: Dataset, column: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Align data from an image column.
    """
    column_type = dataset.get_column_type(column)
    if column_type is not Image:
        raise exceptions.InvalidDTypeError(
            f'An image column expected, but column "{column}" of type {column_type} received.'
        )
    notnull_mask = dataset.notnull(column)
    if notnull_mask.sum() == 0:
        # No data to interpolate, so either dataset is empty, or no samples are valid.
        return np.empty(0, dtype=np.float64), notnull_mask
    raw_data = dataset[column, notnull_mask]
    min_height, min_width = np.inf, np.inf
    for sample in raw_data:
        height, width = sample.data.shape[:2]
        min_height = min(min_height, height)
        min_width = min(min_width, width)
    data = []
    for sample in raw_data:
        y = sample.data
        height, width = y.shape[:2]
        if np.issubdtype(y.dtype, np.integer):
            y = y.astype(np.float64) / 255
        if y.ndim > 2:
            channels = y.shape[2]
            if channels == 1:
                y = y[:, :]
            elif channels == 3:
                y = rgb2gray(y)
            elif channels == 4:
                y = rgb2gray(rgba2rgb(y))
        if height != min_height or width != min_width:
            y = resize_local_mean(y, (min_height, min_width), preserve_range=True)
        y = y.flatten()
        data.append(y)
    return np.array(data), notnull_mask


def align_sequence_1d_data(
    dataset: Dataset, column: str
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Align data from an sequence 1D column.
    """
    column_type = dataset.get_column_type(column)
    if column_type is not Sequence1D:
        raise exceptions.InvalidDTypeError(
            f'A sequence 1D column expected, but column "{column}" of type {column_type} received.'
        )
    notnull_mask = dataset.notnull(column)
    if notnull_mask.sum() == 0:
        # No data to interpolate, so either dataset is empty, or no samples are valid.
        return np.empty((0, 0), dtype=np.float64), notnull_mask
    raw_data = dataset[column, notnull_mask]
    timesteps = np.empty(0, dtype=raw_data[0].index.dtype)
    for sample in raw_data:
        timesteps = np.union1d(timesteps, sample.index)
    # Space the overall count of unique timesteps evenly over the maximal time range.
    x = np.linspace(timesteps.min(), timesteps.max(), len(timesteps))
    data = []
    for sample in raw_data:
        f = interpolate.interp1d(
            sample.index,
            sample.value,
            kind="linear",
            copy=False,
            bounds_error=False,
            fill_value=0,
            assume_sorted=False,
        )
        y = f(x)
        data.append(y)
    return np.stack(data), notnull_mask


def align_column_data(
    dataset: Dataset, column: str, allow_nan: bool = False
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Align data from an Spotlight dataset column if possible.
    """
    column_type = dataset.get_column_type(column)
    if column_type is Audio:
        data, mask = align_audio_data(dataset, column)
    elif column_type is Embedding:
        data, mask = align_embedding_data(dataset, column)
    elif column_type is Image:
        data, mask = align_image_data(dataset, column)
    elif column_type is Sequence1D:
        data, mask = align_sequence_1d_data(dataset, column)
    elif column_type in (bool, int, float, Window):
        data = dataset[column].astype(np.float64).reshape((len(dataset), -1))
        mask = np.full(len(dataset), True)
    else:
        raise NotImplementedError(f"{column_type} column currently not supported.")

    if not allow_nan:
        # Remove "rows" with `NaN`s.
        finite_mask = np.isfinite(data).all(axis=1)
        if not finite_mask.all():
            indices = np.arange(len(dataset))
            indices = indices[mask]
            indices = indices[finite_mask]
            mask = np.full(len(dataset), False)
            mask[indices] = True
            data = data[finite_mask]
    return data, mask
