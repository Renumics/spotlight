"""
Test `spotlight.Dataset.prune` method.
"""
import os.path
from pathlib import Path
from typing import List

import numpy as np

from renumics import spotlight
from tests.test_dataset.conftest import ColumnData


def test_prune(
    tmp_path: Path, simple_data: List[ColumnData], complex_data: List[ColumnData]
) -> None:
    """
    Test prune on a fresh created dataset.
    """
    # pylint: disable=too-many-locals
    data = simple_data + complex_data
    length = len(complex_data[0].values)
    output_h5_file = tmp_path / "dataset.h5"

    with spotlight.Dataset(output_h5_file, "w"):
        pass
    empty_size = os.path.getsize(output_h5_file)
    assert 5000 < empty_size < 10000

    with spotlight.Dataset(output_h5_file, "a") as dataset:
        for sample in data:
            dataset.append_column(
                sample.name,
                sample.column_type,
                description=sample.description,
                **sample.attrs,
            )
    initialized_size = os.path.getsize(output_h5_file)
    assert initialized_size > empty_size

    with spotlight.Dataset(output_h5_file, "a") as dataset:
        for i in range(length):
            data_dict = {sample.name: sample.values[i] for sample in data}
            dataset.append_row(**data_dict)
    filled_size = os.path.getsize(output_h5_file)
    assert filled_size > 4000000

    with spotlight.Dataset(output_h5_file, "a") as dataset:
        for column_name in dataset.keys():  # pylint: disable=consider-using-dict-items
            del dataset[column_name]
    cleaned_size = os.path.getsize(output_h5_file)
    assert cleaned_size <= filled_size

    with spotlight.Dataset(output_h5_file, "a") as dataset:
        dataset.prune()
    pruned_size = os.path.getsize(output_h5_file)
    assert pruned_size < filled_size
    assert np.abs(pruned_size - empty_size) <= 1000
