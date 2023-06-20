"""
find issues in images
"""

from typing import Iterable
from pathlib import Path
from tempfile import TemporaryDirectory
import tqdm

import numpy as np
import cleanvision

from renumics.spotlight.backend.data_source import DataSource
from renumics.spotlight.dtypes.typing import ColumnTypeMapping
from renumics.spotlight.dtypes import Image

from .decorator import data_analyzer
from .typing import DataIssue


_issue_types = {
    "is_light_issue": "Bright images ({column_name})",
    "is_dark_issue": "Dark images ({column_name})",
    "is_blurry_issue": "Blurry images ({column_name})",
    "is_exact_duplicates_issue": "Exact duplicates ({column_name})",
    "is_near_duplicates_issue": "Near duplicates ({column_name})",
    "is_odd_aspect_ratio_issue": "Odd aspect ratio ({column_name})",
    "is_low_information_issue": "Low information ({column_name})",
    "is_grayscale_issue": "Grayscale images ({column_name})",
}


@data_analyzer
def analyze_with_cleanvision(
    data_source: DataSource, dtypes: ColumnTypeMapping
) -> Iterable[DataIssue]:
    """
    find image issues using cleanvision
    """
    # pylint: disable=too-many-locals

    image_columns = [col for col, dtype in dtypes.items() if dtype == Image]

    for column_name in image_columns:
        # load image data from data source
        images = (
            data_source.get_cell_data(column_name, row)
            for row in range(len(data_source))
        )

        # Write images to temporary directory for cleanvision.
        # They alsow support huggingface's image format.
        # Maybe use that in the future where applicable.
        indices_list = []
        image_paths = []
        with TemporaryDirectory() as tmp:
            for i, image_data in enumerate(tqdm.tqdm(images)):
                if not image_data:
                    continue
                path = Path(tmp) / f"{i}.png"
                path.write_bytes(image_data)
                image_paths.append(str(path))
                indices_list.append(i)
            lab = cleanvision.Imagelab(filepaths=image_paths)
            lab.find_issues()
            analysis = lab.issues

        indices = np.array(indices_list)

        # Iterate over all the different issue types
        # and convert them to our internal DataIssue format.
        for cleanvision_key, description in _issue_types.items():
            rows = indices[analysis[cleanvision_key]].tolist()
            if rows:
                yield DataIssue(
                    severity="warning",
                    description=description.format(column_name=column_name),
                    rows=rows,
                )
