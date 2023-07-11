#!/usr/bin/env python3

"""
This script generates multimodal Spotlight dataset for benchmarking.
"""

import os
import string
import datetime
from typing import Type

import click
import numpy as np
from tqdm import trange

from renumics import spotlight


DATA_TYPES = [
    bool,
    int,
    float,
    str,
    datetime.datetime,
    spotlight.Category,
    spotlight.Window,
    spotlight.Embedding,
]

FLOAT_SCALE = 100
STRING_LETTERS = string.ascii_letters + string.digits + string.punctuation
MAX_STRING_LENGTH = 100
NUM_CATEGORIES = 100
MAX_EMBEDDING_DIM = 2048


def _random_bools(num_rows: int, seed: int) -> np.ndarray:
    np.random.seed(seed)
    return np.random.choice([True, False], num_rows)


def _random_ints(num_rows: int, seed: int) -> np.ndarray:
    dtype = "int32"
    np.random.seed(seed)
    return np.random.randint(
        np.iinfo(dtype).min, np.iinfo(dtype).max, size=num_rows, dtype=dtype  # type: ignore
    )


def _random_floats(num_rows: int, seed: int) -> np.ndarray:
    np.random.seed(seed)
    floats = np.random.normal(0.0, FLOAT_SCALE, num_rows)
    np.random.seed(seed)
    null_indices = np.random.randint(0, num_rows, num_rows // 10)
    floats[null_indices] = np.nan
    return floats


def _random_strings(num_rows: int, seed: int) -> np.ndarray:
    np.random.seed(seed)
    lengths = np.random.randint(0, MAX_STRING_LENGTH, num_rows)
    np.random.seed(seed)
    null_indices = np.random.randint(0, num_rows, num_rows // 10)
    lengths[null_indices] = 0
    np.random.seed(seed)
    all_indices = np.random.randint(0, len(STRING_LETTERS), lengths.sum())
    all_letters = np.array(list(STRING_LETTERS))[all_indices]
    strings = []
    start = 0
    for length in lengths:
        strings.append("".join(all_letters[start : start + length]))
        start += length
    return np.array(strings)


def _random_datetimes(num_rows: int, seed: int) -> np.ndarray:
    np.random.seed(seed)
    # days = np.random.randint(0, 3652058, num_rows).tolist()
    days = np.random.randint(612890, 825830, num_rows).tolist()  # For pandas
    np.random.seed(seed)
    seconds = np.random.randint(0, 86399, num_rows).tolist()
    np.random.seed(seed)
    microseconds = np.random.randint(0, 999999, num_rows).tolist()
    min_datetime = datetime.datetime.min
    datetimes = []
    for day, second, microsecond in zip(days, seconds, microseconds):
        datetimes.append(min_datetime + datetime.timedelta(day, second, microsecond))
    data = np.array(datetimes, dtype=object)
    null_indices = np.random.randint(0, num_rows, num_rows // 10)
    data[null_indices] = None
    return data


def _random_categories(num_rows: int, seed: int) -> np.ndarray:
    categories = np.append("", _random_strings(NUM_CATEGORIES - 1, seed))
    np.random.seed(seed)
    data = np.random.choice(categories, num_rows)
    return data


def _random_windows(num_rows: int, seed: int) -> np.ndarray:
    np.random.seed(seed)
    windows = np.random.uniform(0, np.finfo("float32").max, (num_rows, 2))
    np.random.seed(seed)
    null_indices = np.random.randint(0, num_rows, num_rows // 10)
    windows[null_indices] = np.nan
    return windows


def _random_embeddings(
    num_rows: int, seed: int, dim: int = 128, optional: bool = False
) -> np.ndarray:
    dim = min(dim, MAX_EMBEDDING_DIM)
    np.random.seed(seed)
    embeddings = np.random.normal(0.0, FLOAT_SCALE, (num_rows, dim)).astype("float32")
    if not optional:
        return embeddings
    data = np.full(num_rows, None, object)
    np.random.seed(seed)
    null_indices = np.random.randint(0, num_rows, num_rows - num_rows // 5)
    data[~null_indices] = list(embeddings[~null_indices])
    return data


def _random_data(data_type: Type, num_rows: int, seed: int) -> np.ndarray:
    # pylint: disable=too-many-return-statements
    if data_type is bool:
        return _random_bools(num_rows, seed)
    if data_type is int:
        return _random_ints(num_rows, seed)
    if data_type is float:
        return _random_floats(num_rows, seed)
    if data_type is str:
        return _random_strings(num_rows, seed)
    if data_type is datetime.datetime:
        return _random_datetimes(num_rows, seed)
    if data_type is spotlight.Category:
        return _random_categories(num_rows, seed)
    if data_type is spotlight.Window:
        return _random_windows(num_rows, seed)
    if data_type is spotlight.Embedding:
        return _random_embeddings(num_rows, seed)
    raise ValueError(f"Unknown data type {data_type}.")


@click.command()  # type: ignore
@click.option(
    "--output-path",
    "-o",
    type=click.Path(file_okay=False, writable=True),
    help="output folder",
    default=".",
)
@click.option("--num-rows", type=int, help="target row count", default=50000)
@click.option("--num-cols", type=int, help="target column count", default=8)
@click.option("--seed", type=int, help="random seed", default=42)
def generate_multimodal_dataset(
    output_path: str, num_rows: int, num_cols: int, seed: int
) -> None:
    """
    Create benchmark dataset with columns of all types which will be loaded to
    Spotlight immediately, that is:
        bool, int, float, string, datetime, Category, Window, Embedding
    """
    if not os.path.isdir(output_path):
        raise OSError(
            f"Given output path {output_path} does not exist or is not a directory."
        )
    output_h5_file = os.path.join(
        output_path, f"tallymarks-multimodal-{num_cols}x{num_rows}.h5"
    )
    num_data_types = len(DATA_TYPES)
    with spotlight.Dataset(output_h5_file, "w") as dataset:
        for i in trange(num_cols):
            data_type = DATA_TYPES[i % num_data_types]
            optional = False
            if data_type in (
                datetime.datetime,
                spotlight.Category,
                spotlight.Embedding,
            ):
                optional = True
            column_name = f"{data_type.__name__.lower()}_{i // num_data_types}"
            dataset.append_column(
                column_name,
                data_type,
                _random_data(data_type, num_rows, seed + i),
                optional=optional,
            )


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    generate_multimodal_dataset()  # type: ignore
