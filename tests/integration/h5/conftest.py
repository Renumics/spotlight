"""
Pytest Fixtures for h5 tests
"""

import os.path
import tempfile
from typing import Iterator

import pytest
from renumics import spotlight

from .data import COLUMNS


@pytest.fixture
def dataset_path() -> Iterator[str]:
    """
    H5 Dataset for tests
    """

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dataset = os.path.join(temp_dir, "dataset.h5")
        with spotlight.Dataset(temp_dataset, "w") as dataset:
            for col, (dtype, values) in COLUMNS.items():
                dataset.append_column(
                    col,
                    column_type=dtype,
                    values=values,
                    optional=dtype not in (int, bool),
                )
        yield temp_dataset
