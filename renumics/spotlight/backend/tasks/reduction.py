"""
Taks for dimensionality reduction
"""

from typing import List, Tuple, cast

import numpy as np
import pandas as pd

from renumics.spotlight import dtypes
from renumics.spotlight.data_store import DataStore

SEED = 42


class ColumnNotEmbeddable(Exception):
    """
    The column is not embeddable
    """


def align_data(
    data_store: DataStore, column_names: List[str], indices: List[int]
) -> Tuple[np.ndarray, List[int]]:
    """
    Align data from table's columns, remove `NaN`'s.
    """
    from sklearn import preprocessing

    if not column_names or not indices:
        return np.empty(0, np.float64), []

    aligned_values = []
    for column_name in column_names:
        dtype = data_store.dtypes[column_name]
        column_values = data_store.get_converted_values(column_name, indices)
        if dtypes.is_embedding_dtype(dtype):
            embedding_length = max(
                0 if x is None else len(cast(np.ndarray, x)) for x in column_values
            )
            if embedding_length:
                none_replacement = np.full(embedding_length, np.nan)
                aligned_values.append(
                    np.array(
                        [
                            value if value is not None else none_replacement
                            for value in column_values
                        ]
                    )
                )
        elif dtypes.is_category_dtype(dtype):
            na_mask = np.array(column_values) == -1
            one_hot_values = preprocessing.label_binarize(
                column_values, classes=sorted(set(column_values).difference({-1}))  # type: ignore
            ).astype(float)
            one_hot_values[na_mask] = np.nan
            aligned_values.append(one_hot_values)
        elif dtypes.is_scalar_dtype(dtype):
            aligned_values.append(np.array(column_values, dtype=float))
        else:
            raise ColumnNotEmbeddable(
                f"Column '{column_name}' of type {dtype} is not embeddable."
            )

    data = np.hstack([col.reshape((len(indices), -1)) for col in aligned_values])
    mask = ~pd.isna(data).any(axis=1)
    return data[mask], (np.array(indices)[mask]).tolist()


def compute_umap(
    data_store: DataStore,
    column_names: List[str],
    indices: List[int],
    n_neighbors: int,
    metric: str,
    min_dist: float,
) -> Tuple[np.ndarray, List[int]]:
    """
    Prepare data from table and compute U-Map on them.
    """

    data, indices = align_data(data_store, column_names, indices)

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
    data_store: DataStore,
    column_names: List[str],
    indices: List[int],
    normalization: str,
) -> Tuple[np.ndarray, List[int]]:
    """
    Prepare data from table and compute PCA on them.
    """

    data, indices = align_data(data_store, column_names, indices)

    if data.size == 0:
        return np.empty(0, np.float64), []

    from sklearn import decomposition, preprocessing

    if data.shape[1] == 1:
        return np.hstack((data, np.zeros_like(data))), indices
    if normalization == "standardize":
        data = preprocessing.StandardScaler(copy=False).fit_transform(data)
    elif normalization == "robust standardize":
        data = preprocessing.RobustScaler(copy=False).fit_transform(data)
    reducer = decomposition.PCA(n_components=2, copy=False, random_state=SEED)
    # `fit_transform` returns Fortran-ordered array.
    embeddings = np.ascontiguousarray(reducer.fit_transform(data))
    return embeddings, indices
