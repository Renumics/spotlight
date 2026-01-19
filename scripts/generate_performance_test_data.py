#!/usr/bin/env python3

"""
generate spotlight test dataset
"""

from pathlib import Path

import click
import numpy as np

from renumics.spotlight import Dataset, Embedding


@click.command()  # type: ignore
@click.option(
    "--output-path",
    "-o",
    type=click.Path(file_okay=False, dir_okay=True, writable=True),
    help="output folder",
    default=Path("."),
)
def generate_datasets(output_path: Path) -> None:
    """
    generate four datasets (default, one with many columns,
    one with large embedding size and one with both.
    """
    generate_dataset(
        Path(output_path) / "default.h5", emb_col_count=2, embedding_size=32
    )
    generate_dataset(
        Path(output_path) / "many_cols.h5", emb_col_count=20, embedding_size=32
    )
    generate_dataset(
        Path(output_path) / "large_embeddings.h5", emb_col_count=2, embedding_size=320
    )
    generate_dataset(
        Path(output_path) / "many_cols_large_embeddings.h5",
        emb_col_count=6,
        embedding_size=96,
    )


def generate_dataset(
    output_file_path: Path,
    emb_col_count: int,
    embedding_size: int,
    rows_count: int = 5000,
) -> None:
    """generate dataset with a strn, float and array column
    and the given number of columns with embeddings"""
    with Dataset(output_file_path, "w") as dataset:
        # add some random small data
        dataset.append_string_column("string", ["string" for _ in range(rows_count)])
        dataset.append_float_column(
            "float", np.random.random_sample((rows_count,)).tolist()
        )

        dataset.append_array_column(
            "embeddings_as_array",
            [np.random.random_sample((embedding_size,)) for _ in range(rows_count)],
        )

        # add larger embeddings
        for col_i in range(emb_col_count + 1):
            dataset.append_embedding_column(
                f"encoded_{col_i}",
                [
                    Embedding(np.random.random_sample((embedding_size,)))
                    for _ in range(rows_count)
                ],
            )


if __name__ == "__main__":
    generate_datasets()  # type: ignore
