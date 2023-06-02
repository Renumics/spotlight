"""
Dataset Analysis
"""

from typing import List, Union, Literal

import numpy as np
import pandas as pd
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from renumics.spotlight.dtypes.typing import ColumnTypeMapping
from renumics.spotlight.dtypes import Embedding

from renumics.spotlight.analysis.outliers import detect_outliers


# pylint: disable=too-few-public-methods
class DatasetProblem(BaseModel):
    """
    A Problem affecting multiple rows of the dataset
    """

    type: Union[Literal["warning"], Literal["error"]]
    description: str
    rows: List[int]


def find_problems(df: pd.DataFrame, dtypes: ColumnTypeMapping) -> List[DatasetProblem]:
    """
    Find dataset problems in df
    """

    problems: List[DatasetProblem] = []

    for column_name, dtype in dtypes.items():
        if dtype == Embedding:
            mask = detect_outliers(df[column_name])
            rows = np.where(mask)[0].tolist()
            if rows:
                problems.append(
                    DatasetProblem(
                        type="warning",
                        description=f"Outliers detected ({column_name})",
                        rows=rows,
                    )
                )

    return problems
