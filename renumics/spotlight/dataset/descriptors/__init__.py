"""make descriptor methods more available
"""
from typing import List, Optional, Tuple

import numpy as np
import pycatch22
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from renumics.spotlight.dataset import Dataset
from renumics.spotlight.dataset.exceptions import ColumnExistsError, InvalidDTypeError
from renumics.spotlight.dtypes import Audio, Sequence1D
from .data_alignment import align_column_data


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
    # pylint: disable=too-many-arguments
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


def get_catch22_feature_names(catch24: bool = False) -> List[str]:
    """
    Get Catch22 feature names in the same order as returned by :func:`catch22`.
    """
    # Run Catch22 with dummy data to get feature names.
    return pycatch22.catch22_all([0], catch24)["names"]


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
    # pylint: disable=too-many-arguments, too-many-branches
    if suffix is None:
        suffix = "catch24" if catch24 else "catch22"
    column_type = dataset.get_column_type(column)
    if column_type not in (Audio, Sequence1D):
        raise InvalidDTypeError(
            f"catch22 is only applicable to columns of type `Audio` and "
            f'`Sequence1D`, but column "{column}" of type {column_type} received.'
        )

    column_names = []
    if as_float_columns:
        for name in get_catch22_feature_names(catch24):
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
