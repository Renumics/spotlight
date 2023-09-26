"""
Pytest Fixtures for Hugging Face tests
"""

import datasets
import pytest

from .dataset import create_hf_dataset


@pytest.fixture
def dataset() -> datasets.Dataset:
    """
    H5 Dataset for tests
    """

    return create_hf_dataset()
