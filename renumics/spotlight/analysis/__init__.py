"""
Dataset Analysis
"""

from typing import List, Union, Literal

import numpy as np
import pandas as pd
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from renumics.spotlight.dtypes.typing import ColumnTypeMapping
from renumics.spotlight.dtypes import Embedding, Image

from renumics.spotlight.analysis.outliers import detect_outliers
from renumics.spotlight.analysis.images import analyze_images


# pylint: disable=too-few-public-methods
class DatasetIssue(BaseModel):
    """
    A Problem affecting multiple rows of the dataset
    """

    severity: Union[Literal["warning"], Literal["error"]]
    description: str
    rows: List[int]


def find_issues(df: pd.DataFrame, dtypes: ColumnTypeMapping) -> List[DatasetIssue]:
    """
    Find dataset issues in df
    """
    # pylint: disable=too-many-locals

    issues: List[DatasetIssue] = []

    for column_name, dtype in dtypes.items():
        if dtype == Image:
            analysis = analyze_images(df[column_name])

            bright_rows = np.where(analysis["is_light_issue"])[0].tolist()
            if bright_rows:
                issues.append(
                    DatasetIssue(
                        severity="warning",
                        description=f"Bright images ({column_name})",
                        rows=bright_rows,
                    )
                )

            dark_rows = np.where(analysis["is_dark_issue"])[0].tolist()
            if dark_rows:
                issues.append(
                    DatasetIssue(
                        severity="warning",
                        description=f"Dark images ({column_name})",
                        rows=dark_rows,
                    )
                )

            blurry_rows = np.where(analysis["is_blurry_issue"])[0].tolist()
            if blurry_rows:
                issues.append(
                    DatasetIssue(
                        severity="warning",
                        description=f"Blurry images ({column_name})",
                        rows=blurry_rows,
                    )
                )

            duplicate_rows = np.where(analysis["is_exact_duplicates_issue"])[0].tolist()
            if duplicate_rows:
                issues.append(
                    DatasetIssue(
                        severity="warning",
                        description=f"Exact duplicates ({column_name})",
                        rows=duplicate_rows,
                    )
                )

            near_duplicate_rows = np.where(analysis["is_near_duplicates_issue"])[
                0
            ].tolist()
            if near_duplicate_rows:
                issues.append(
                    DatasetIssue(
                        severity="warning",
                        description=f"Near duplicates ({column_name})",
                        rows=near_duplicate_rows,
                    )
                )

            odd_aspect_ratio_rows = np.where(analysis["is_odd_aspect_ratio_issue"])[
                0
            ].tolist()
            if odd_aspect_ratio_rows:
                issues.append(
                    DatasetIssue(
                        severity="warning",
                        description=f"Odd aspect ratio ({column_name})",
                        rows=odd_aspect_ratio_rows,
                    )
                )

            low_information_rows = np.where(analysis["is_low_information_issue"])[
                0
            ].tolist()
            if low_information_rows:
                issues.append(
                    DatasetIssue(
                        severity="warning",
                        description=f"Low information ({column_name})",
                        rows=low_information_rows,
                    )
                )

            grayscale_rows = np.where(analysis["is_grayscale_issue"])[0].tolist()
            if grayscale_rows:
                issues.append(
                    DatasetIssue(
                        severity="warning",
                        description=f"Grayscale ({column_name})",
                        rows=grayscale_rows,
                    )
                )

        if dtype == Embedding:
            mask = detect_outliers(df[column_name])
            rows = np.where(mask)[0].tolist()
            if rows:
                issues.append(
                    DatasetIssue(
                        severity="warning",
                        description=f"Outliers ({column_name})",
                        rows=rows,
                    )
                )

    return issues
