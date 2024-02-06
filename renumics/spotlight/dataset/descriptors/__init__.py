"""make descriptor methods more available
"""

import warnings
from typing import Optional, Tuple

import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from renumics.spotlight import dtypes
from renumics.spotlight.dataset import Dataset
from renumics.spotlight.dataset.exceptions import ColumnExistsError, InvalidDTypeError

from .data_alignment import align_column_data

warnings.warn(
    "`renumics.spotlight.dataset.descriptors` module is deprecated and will "
    "be removed in future versions.",
    DeprecationWarning,
    stacklevel=2,
)


def pca(
    dataset: Dataset,
    column: str,
    n_components: int = 8,
    inplace: bool = False,
    suffix: str = "pca",
    overwrite: bool = False,
) -> Optional[Tuple[np.ndarray, np.ndarray]]:
    """
    Generate PCA embeddings for the given column of a dataset and
    optionally write them back into dataset.
    """

    embedding_column_name = f"{column}-{suffix}"
    if inplace and not overwrite and embedding_column_name in dataset.keys():
        raise ColumnExistsError(
            f'Column "{embedding_column_name}" already exists. Either set '
            f"another `suffix` argument or set `overwrite` argument to `True`."
        )
    data, mask = align_column_data(dataset, column, allow_nan=False)

    if inplace:
        if overwrite and embedding_column_name in dataset.keys():
            del dataset[embedding_column_name]
        dataset.append_embedding_column(embedding_column_name, optional=True)
    if len(data) == 0:
        if inplace:
            return None
        return np.empty((0, n_components), dtype=data.dtype), np.full(
            len(dataset), False
        )

    data = StandardScaler().fit_transform(data)
    embeddings = PCA(n_components=n_components).fit_transform(data)
    if inplace:
        dataset[embedding_column_name, mask] = embeddings
        return None
    return embeddings, mask


def catch22(
    dataset: Dataset,
    column: str,
    catch24: bool = False,
    inplace: bool = False,
    suffix: Optional[str] = None,
    overwrite: bool = False,
    as_float_columns: bool = False,
) -> Optional[Tuple[np.ndarray, np.ndarray]]:
    """
    Generate Catch22 embeddings for the given column of a dataset and
    optionally write them back into dataset.
    """
    try:
        import pycatch22
    except ModuleNotFoundError as e:
        raise RuntimeError(
            "Install Spotlight with 'descriptors' extras in order to use `catch22`."
        ) from e

    if suffix is None:
        suffix = "catch24" if catch24 else "catch22"
    dtype = dataset.get_dtype(column)
    if not dtypes.is_audio_dtype(dtype) and not dtypes.is_sequence_1d_dtype(dtype):
        raise InvalidDTypeError(
            f"catch22 is only applicable to columns of type `Audio` and "
            f'`Sequence1D`, but column "{column}" of type {dtype} received.'
        )

    column_names = []
    if as_float_columns:
        feature_names = pycatch22.catch22_all([0], catch24)["names"]
        for name in feature_names:
            column_names.append("-".join((column, suffix, name)))
    else:
        column_names.append(f"{column}-{suffix}")
    if inplace and not overwrite:
        for name in column_names:
            if name in dataset.keys():
                raise ColumnExistsError(
                    f'Column "{name}" already exists. Either set another '
                    f"`suffix` argument or set `overwrite` argument to `True`."
                )
    data, mask = align_column_data(dataset, column, allow_nan=False)

    if inplace:
        if overwrite:
            for name in column_names:
                if name in dataset.keys():
                    del dataset[name]
        for name in column_names:
            if as_float_columns:
                dataset.append_float_column(name, optional=True)
            else:
                dataset.append_embedding_column(name, optional=True)
    if len(data) == 0:
        if inplace:
            return None
        return np.empty((0, 24 if catch24 else 22), dtype=data.dtype), np.full(
            len(dataset), False
        )

    embeddings = np.array(
        [pycatch22.catch22_all(sample, catch24)["values"] for sample in data],
        dtype=float,
    )

    if inplace:
        if as_float_columns:
            for name, values in zip(column_names, embeddings.T):
                dataset[name, mask] = values
        else:
            dataset[column_names[0], mask] = embeddings
        return None
    return embeddings, mask
