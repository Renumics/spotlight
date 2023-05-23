#!/usr/bin/env python3

"""
generate spotlight test dataset with 50k rows
"""

import os

from pathlib import Path
import click

from tqdm import tqdm
import numpy as np
from sklearn import datasets
import sklearn.utils
from sklearn.decomposition import PCA


from renumics.spotlight import Dataset, Embedding

N_ROWS = 50 * 1000
N_COMPONENTS_EMBEDDINGS = 128
N_FLOAT_COLS = 100


@click.command()
@click.option(
    "--output-path",
    "-o",
    type=click.Path(file_okay=False, dir_okay=True, writable=True),
    help="output folder",
    default=Path("."),
)
def generate_tallymarks_dataset_ultra(
    output_path: Path,
) -> None:
    """
    Generate a test dataset based on mnist with
        - number
        - An embedding of the image (d=128)
        - multiple random float columns (n=100)
    """

    digits: sklearn.utils.Bunch = datasets.load_digits()

    digits_data = digits.data  # pylint:disable=no-member
    digits_target = digits.target  # pylint:disable=no-member
    if N_ROWS > len(digits_data):
        digits_data = np.pad(
            digits_data, [(0, N_ROWS - len(digits_data)), (0, 0)], mode="wrap"
        )
        digits_target = np.pad(
            digits_target, [(0, N_ROWS - len(digits_target))], mode="wrap"
        )

    coords = PCA(n_components=N_COMPONENTS_EMBEDDINGS).fit_transform(
        np.pad(digits_data, [(0, 0), (0, N_COMPONENTS_EMBEDDINGS - 64)], mode="wrap")
    )
    encoded = [Embedding(coord) for coord in coords]

    output_h5_file = os.path.join(
        output_path,
        f"tallymarks_dataset_ultra50k_emb{N_COMPONENTS_EMBEDDINGS}_floats{N_FLOAT_COLS}.h5",
    )
    with Dataset(output_h5_file, "w") as dataset:
        dataset.append_int_column(
            "number",
            [int(label) for label in digits_target],
            optional=True,
            default=-1,
            description="This is just the `number` value, converted to float.",
        )
        dataset.append_embedding_column("encoded", encoded, optional=True)

        for i in tqdm(range(N_FLOAT_COLS)):
            dataset.append_float_column(f"float_{i}", list(np.random.rand(N_ROWS)))


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    generate_tallymarks_dataset_ultra()  # type: ignore
