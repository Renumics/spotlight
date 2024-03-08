"""
Outlier detection
"""

import inspect
from typing import Iterable, List

import cleanlab.outlier
import numpy as np

from renumics.spotlight.data_store import DataStore
from renumics.spotlight.dtypes import is_embedding_dtype

from ..decorator import data_analyzer
from ..typing import DataIssue


@data_analyzer
def analyze_with_cleanlab(
    data_store: DataStore, columns: List[str]
) -> Iterable[DataIssue]:
    """
    Find (embedding) outliers with cleanlab
    """

    embedding_columns = (
        col
        for col in columns
        if col in data_store.dtypes and is_embedding_dtype(data_store.dtypes[col])
    )

    for column_name in embedding_columns:
        converted_values = data_store.get_converted_values(column_name)
        embeddings = np.array(converted_values, dtype=object)
        mask = _detect_outliers(embeddings)
        rows = np.where(mask)[0].tolist()

        if len(rows):
            yield DataIssue(
                title="Outliers in embeddings",
                rows=rows,
                severity="medium",
                columns=[column_name],
                description=inspect.cleandoc(
                    """
                    There are outliers in one of your embedding columns.

                    Here are a few issues that outliers might indicate:
                    1. Data entry or measurement errors
                    2. Feature engineering issues, like missing normalization
                    3. Sampling bias in your dataset
                """
                ),
            )


def _calculate_outlier_scores(embeddings: np.ndarray) -> np.ndarray:
    """
    calculate outlier scores for an embedding column
    """
    if embeddings.ndim > 1:
        mask = np.ones(len(embeddings), dtype=bool)
    else:
        mask = np.array([value is not None for value in embeddings])

    features = np.stack(embeddings[mask])  # type: ignore

    scores = np.full(shape=(len(embeddings),), fill_value=np.nan)

    # cleanlab's ood needs at least 10 features
    # Don't calculate any scores if we have less than 10 embeddings.
    if len(features) < 10:
        return scores

    scores[mask] = cleanlab.outlier.OutOfDistribution().fit_score(
        features=features, verbose=False
    )
    return scores


def _detect_outliers(embeddings: np.ndarray) -> np.ndarray:
    """
    detect outliers in an embedding column
    """
    scores = _calculate_outlier_scores(embeddings)
    return scores < 0.50
