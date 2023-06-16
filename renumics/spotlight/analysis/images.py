"""
find issues in images
"""

import pandas as pd
import cleanvision


def analyze_images(images: pd.Series) -> pd.DataFrame:
    """
    find issues in images
    """
    lab = cleanvision.Imagelab(filepaths=images.tolist())
    lab.find_issues()
    return lab.issues
