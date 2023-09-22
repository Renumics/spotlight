#!/usr/bin/env python3

"""
This script creates multimodal Hugging Face dataset to test Spotlight on.
"""

import datasets
import numpy as np

from renumics.spotlight import dtypes


def random_values(
    dtype: dtypes.DType, num_rows: int, optional: bool = False
) -> np.ndarray:
    if dtypes.is_bool_dtype(dtype):
        values = np.random.randint(0, 2, num_rows, bool)
    elif dtypes.is_int_dtype(dtype):
        values = np.random.randint(0, 2, num_rows, bool)
    elif dtypes.is_float_dtype(dtype):
        values = np.random.normal(0, 100, num_rows)
    # elif dtypes.is_str_dtype(dtype):
    #     str_lengths = np.random.randint(0, 100, num_rows)
    #     null_indices = np.random.randint(0, num_rows, num_rows // 10)
    #     str_lengths[null_indices] = 0
    #     all_letters = np.array(
    #         list(string.ascii_letters + string.digits + string.punctuation)
    #     )
    else:
        raise NotImplementedError

    if not optional:
        return values

    null_indices = np.random.randint(0, num_rows, num_rows // 10)
    if np.issubdtype(values.dtype, np.floating):
        values[null_indices] = np.nan
    else:
        values = values.astype(object)
        values[null_indices] = None
    return values


def create_hf_dataset(num_rows: int) -> None:
    ds = datasets.Dataset.from_dict(
        {
            # "bool": random_values(dtypes.bool_dtype, num_rows),
            # "int": random_values(dtypes.int_dtype, num_rows),
            # "float": random_values(dtypes.float_dtype, num_rows),
            "embedding": [[1, 2, 3, 4], [1, 6, 3, 7], [-1, -2, -3, -4]],
            "sequence_1d": [[1, 2, 3, 4], [1, 6, 3], [-1, -2, -3, -4, 10]],
            "sequence_2d": [
                [[1, 2, 3, 4], [-1, 3, 1, 6]],
                [[1, -3, 10], [1, 6, 3]],
                [[-10, 0, 10], [-1, -2, -3]],
            ],
            "sequence_2d_t": [[[5, 3], [2, 5], [10, 8]], [], [[-1, 1], [1, 10]]],
        },
        features=datasets.Features(
            {
                "embedding": datasets.Sequence(
                    feature=datasets.Value("float64"), length=4
                ),
                "sequence_1d": datasets.Sequence(feature=datasets.Value("float64")),
                "sequence_2d": datasets.Sequence(
                    feature=datasets.Sequence(feature=datasets.Value("float64")),
                    length=2,
                ),
                "sequence_2d_t": datasets.Sequence(
                    feature=datasets.Sequence(
                        feature=datasets.Value("float64"), length=2
                    ),
                ),
            }
        ),
        # info=datasets.DatasetInfo(),
        # split=datasets.NamedSplit,
    )
    ds.save_to_disk("build/datasets/hf")
    print(ds.features)


if __name__ == "__main__":
    np.random.seed(42)
    create_hf_dataset(100)
