"""
Taks for dimensionality reduction
"""

from typing import List, Tuple, cast

import numpy as np
import pandas as pd

from renumics.spotlight.dataset.exceptions import ColumnNotExistsError
from renumics.spotlight.dtypes import Category, Embedding
from renumics.spotlight.dtypes.typing import ColumnTypeMapping
from ..data_source import DataSource

SEED = 42


class ColumnNotEmbeddable(Exception):
    """
    The column is not embeddable
    """


def get_aligned_data(
    table: DataSource,
    dtypes: ColumnTypeMapping,
    column_names: List[str],
    indices: List[int],
) -> Tuple[np.ndarray, List[int]]:
    """
    Align data from table's columns, remove `NaN`'s.
    """

    if not column_names or not indices:
        return np.empty(0, np.float64), []

    from sklearn import preprocessing

    values = []
    for column_name in column_names:
        column = table.get_column(column_name, dtypes[column_name], indices)
        if column.type is Embedding:
            if column.embedding_length:
                none_replacement = np.full(column.embedding_length, np.nan)
                values.append(
                    np.array(
                        [
                            value if value is not None else none_replacement
                            for value in column.values
                        ]
                    )
                )
        elif column.type is Category:
            if column.categories:
                classes = sorted(column.categories.values())
                na_mask = ~np.isin(np.array(column.values), classes)
                one_hot_values = preprocessing.label_binarize(
                    column.values, classes=sorted(column.categories.values())
                ).astype(float)
                one_hot_values[na_mask] = np.nan
                values.append(one_hot_values)
            else:
                values.append(np.full(len(column.values), np.nan))
        elif column.type in (int, bool, float):
            values.append(np.array(column.values))
        else:
            raise ColumnNotEmbeddable

    data = np.hstack([col.reshape((len(indices), -1)) for col in values])
    mask = ~pd.isna(data).any(axis=1)
    return data[mask], (np.array(indices)[mask]).tolist()


def compute_umap(
    table: DataSource,
    dtypes: ColumnTypeMapping,
    column_names: List[str],
    indices: List[int],
    n_neighbors: int,
    metric: str,
    min_dist: float,
) -> Tuple[np.ndarray, List[int]]:
    """
    Prepare data from table and compute U-Map on them.
    """

    try:
        data, indices = get_aligned_data(table, dtypes, column_names, indices)
    except (ColumnNotExistsError, ColumnNotEmbeddable):
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
    dtypes: ColumnTypeMapping,
    column_names: List[str],
    indices: List[int],
    normalization: str,
) -> Tuple[np.ndarray, List[int]]:
    """
    Prepare data from table and compute PCA on them.
    """

    from sklearn import preprocessing, decomposition

    try:
        data, indices = get_aligned_data(table, dtypes, column_names, indices)
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
