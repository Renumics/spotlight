#!/usr/bin/env python3

"""
This script creates multimodal Hugging Face dataset to test Spotlight on.
"""

import datasets
import numpy as np
from renumics import spotlight

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
            "bool": [True, False, False],
            "int": [-1, 1, 100000],
            "uint": [1, 1, 30000],
            "float": [1.0, float("nan"), 1000],
            "string": ["foo", "barbaz", ""],
            "label": ["foo", "bar", "foo"],
            # "int": random_values(dtypes.int_dtype, num_rows),
            # "float": random_values(dtypes.float_dtype, num_rows),
            "embedding": [[1, 2, 3, 4], [1, 6, 3, 7], [-1, -2, -3, -4]],
            # HF sequence as Spotlight sequence
            "sequence_1d": [[1, 2, 3, 4], [1, 6, 3], [-1, -2, float("nan"), -4, 10]],
            "sequence_2d": [
                [[1, 2, 3, 4], [-1, 3, 1, 6]],
                [[1, -3, 10], [1, 6, 3]],
                [[-10, 0, 10], [-1, -2, -3]],
            ],
            "sequence_2d_t": [[[5, 3], [2, 5], [10, 8]], [], [[-1, 1], [1, 10]]],
            # HF sequence as Spotlight array
            "sequence_2d_array": [
                [[1, 2, 3, 4], [-1, 3, 1, 6], [1, 2, 4, 4]],
                [[1, -3, 10], [1, 6, 3], [1, float("nan"), 4]],
                [[-10, 0, 10], [-1, -2, -3], [1, 2, 4]],
            ],
            "sequence_3d_array": [
                [[[1, 2, 3, 4], [-1, 3, 1, 6], [1, 2, 4, 4]]],
                [[[1, -3, 10], [1, 6, 3], [1, float("nan"), 4]]],
                [[[-10, 0, 10], [-1, -2, -3], [1, 2, 4]]],
            ],
            # HF 2D array as Spotlight sequence
            "array_2d_sequence": [
                [[1, 2, 3], [-1, 3, 1]],
                [[1, -3, 10], [1, 6, 3]],
                [[-10, 0, 10], [-1, -2, -3]],
            ],
            "array_2d_t_sequence": [
                [[5, 3], [2, 5], [10, 8]],
                [[float("nan"), 1], [1, 1], [2, 2]],
                [[-1, 1], [1, 10], [10, 1]],
            ],
            "array_2d_vlen_sequence": [
                [[5, 3], [2, 5], [10, 8]],
                [],
                [[-1, 1], [1, 10]],
            ],
            # HF 4D array as Spotlight array
            "array_4d": [
                [[[[1.0, 1.0, -10.0]]], [[[-1.0, 1.0, -1.0]]], [[[2.0, 1.0, 1.0]]]],
                [
                    [[[2.0, -3.0, 0.0]]],
                    [[[3.0, 6.0, -2.0]]],
                    [[[4.0, float("nan"), 2.0]]],
                    [[[4.0, float("nan"), 2.0]]],
                ],
                [[[[3.0, 10.0, 10.0]]], [[[6.0, 3.0, -3.0]]], [[[4.0, 4.0, 4.0]]]],
            ],
            # HF list as Spotlight embedding
            "list_sequence": [[1, 2, 3, 4], [1, 6, 3, 7], [-1, -2, -3, -4]],
        },
        features=datasets.Features(
            {
                "bool": datasets.Value("bool"),
                "int": datasets.Value("int32"),
                "uint": datasets.Value("uint16"),
                "float": datasets.Value("float64"),
                "string": datasets.Value("string"),
                "label": datasets.ClassLabel(
                    num_classes=4, names=["foo", "bar", "baz", "barbaz"]
                ),
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
                "sequence_2d_array": datasets.Sequence(
                    feature=datasets.Sequence(feature=datasets.Value("float64")),
                    length=3,
                ),
                "sequence_3d_array": datasets.Sequence(
                    feature=datasets.Sequence(
                        feature=datasets.Sequence(feature=datasets.Value("float64")),
                        length=3,
                    ),
                    length=1,
                ),
                "array_2d_sequence": datasets.Array2D(shape=(2, 3), dtype="float64"),
                "array_2d_t_sequence": datasets.Array2D(shape=(3, 2), dtype="float64"),
                "array_2d_vlen_sequence": datasets.Array2D(
                    shape=(None, 2), dtype="float64"
                ),
                "array_4d": datasets.Array4D(shape=(None, 1, 1, 3), dtype="float64"),
                "list_sequence": [datasets.Value("float64")],
            }
        ),
        # info=datasets.DatasetInfo(),
        # split=datasets.NamedSplit,
    )
    ds.save_to_disk("./build/datasets/hf")
    print(ds.features)


if __name__ == "__main__":
    np.random.seed(42)
    create_hf_dataset(100)

    ds = datasets.load_from_disk("./build/datasets/hf")
    spotlight.show(ds)
