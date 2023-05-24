"""
Taks for dimensionality reduction
"""

from typing import List, Tuple, cast

import numpy as np
import pandas as pd

from renumics.spotlight.dataset.exceptions import ColumnNotExistsError
from renumics.spotlight.dtypes import Category, Embedding
from ..data_source import DataSource

SEED = 42


def get_aligned_data(
    table: DataSource, column_names: List[str], indices: List[int]
) -> Tuple[np.ndarray, List[int]]:
    """
    Align data from table's columns, remove `NaN`'s.
    """

    if not column_names or not indices:
        return np.empty(0, np.float64), []
    columns = [table.get_column(column_name, indices) for column_name in column_names]
    for column in columns:
        if column.type == Embedding:
            if column.embedding_length:
                none_replacement = np.full(column.embedding_length, np.nan)
                column.values = np.array(
                    [
                        value if value is not None else none_replacement
                        for value in column.values
                    ]
                )
        elif column.type not in (int, bool, float, Category):
            raise ValueError(
                f'Column "{column.name}" of type {column.type.__name__} is not embeddable.'
            )
    data = np.hstack([column.values.reshape((len(indices), -1)) for column in columns])
    mask = ~pd.isna(data).any(axis=1)
    return data[mask], (np.array(indices)[mask]).tolist()


def compute_umap(
    table: DataSource,
    column_names: List[str],
    indices: List[int],
    n_neighbors: int,
    metric: str,
    min_dist: float,
) -> Tuple[np.ndarray, List[int]]:
    """
    Prepare data from table and compute U-Map on them.
    """
    # pylint: disable=import-outside-toplevel, too-many-arguments

    try:
        data, indices = get_aligned_data(table, column_names, indices)
    except (ColumnNotExistsError, ValueError):
        return np.empty(0, np.float64), []
    if data.size == 0:
        return np.empty(0, np.float64), []

    from sklearn import preprocessing

    if metric == "standardized euclidean":
        data = preprocessing.StandardScaler(copy=False).fit_transform(data)
        metric = "euclidean"
    elif metric == "robust euclidean":
        data = preprocessing.RobustScaler(copy=False).fit_transform(data)
        metric = "euclidean"
    if data.shape[1] == 2:
        return data, indices

    import umap

    embeddings = umap.UMAP(
        n_neighbors=n_neighbors, metric=metric, min_dist=min_dist, random_state=SEED
    ).fit_transform(data)
    return cast(np.ndarray, embeddings), indices


def compute_pca(
    table: DataSource,
    column_names: List[str],
    indices: List[int],
    normalization: str,
) -> Tuple[np.ndarray, List[int]]:
    """
    Prepare data from table and compute PCA on them.
    """
    # pylint: disable=import-outside-toplevel
    from sklearn import preprocessing, decomposition

    try:
        data, indices = get_aligned_data(table, column_names, indices)
    except (ColumnNotExistsError, ValueError):
        return np.empty(0, np.float64), []
    if data.size == 0:
        return np.empty(0, np.float64), []
    if data.shape[1] == 1:
        return np.hstack((data, np.zeros_like(data))), indices
    if normalization == "standardize":
        data = preprocessing.StandardScaler(copy=False).fit_transform(data)
    elif normalization == "robust standardize":
        data = preprocessing.RobustScaler(copy=False).fit_transform(data)
    reducer = decomposition.PCA(n_components=2, copy=False, random_state=SEED)
    embeddings = reducer.fit_transform(data)
    return embeddings, indices
