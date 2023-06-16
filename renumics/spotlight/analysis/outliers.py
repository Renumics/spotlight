"""
Outlier detection
"""

import numpy as np
import pandas as pd
import cleanlab.outlier
from renumics.spotlight.io.pandas import prepare_column
from renumics.spotlight.dtypes import Embedding


def calculate_outlier_scores(embeddings: pd.Series) -> np.ndarray:
    """
    calculate outlier scores for an embedding column
    """
    feature_series = prepare_column(embeddings, dtype=Embedding).dropna()
    features = np.stack(feature_series.dropna().to_numpy())  # type: ignore

    scores = np.full(shape=(len(embeddings),), fill_value=np.nan)
    scores[feature_series.index] = cleanlab.outlier.OutOfDistribution().fit_score(
        features=features, verbose=False
    )
    return scores


def detect_outliers(embeddings: pd.Series) -> np.ndarray:
    """
    detect outliers in an embedding column
    """
    scores = calculate_outlier_scores(embeddings)
    return scores < 0.55
