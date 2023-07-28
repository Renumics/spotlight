"""
Pytest Fixtures for h5 tests
"""

import tempfile
from typing import Iterator

import pytest
from renumics import spotlight

from tests.h5.data import COLUMNS


@pytest.fixture
def dataset_path() -> Iterator[str]:
    """
    H5 Dataset for tests
    """

    with tempfile.NamedTemporaryFile(suffix=".h5") as temp:
        with spotlight.Dataset(temp.name, "w") as dataset:
            for col, (dtype, values) in COLUMNS.items():
                dataset.append_column(
                    col,
                    column_type=dtype,
                    values=values,
                    optional=dtype not in (int, bool),
                )
        yield temp.name
