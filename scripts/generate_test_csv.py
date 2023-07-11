#!/usr/bin/env python3

"""
This script generates multimodal CSV dataset.
"""

import datetime
from pathlib import Path
from typing import List, Optional, Sequence

import click
import numpy as np
import pandas as pd

from generate_multimodal_test_data import _random_data, _random_embeddings  # type: ignore

from renumics import spotlight

DATA_FOLDER = Path("data")
AUDIO_FOLDER = DATA_FOLDER / "audio"
IMAGE_FOLDER = DATA_FOLDER / "images"
MESH_FOLDER = DATA_FOLDER / "meshes"
VIDEO_FOLDER = DATA_FOLDER / "videos"


def _random_embeddings_list(
    count: int, seed: int, dim: int, optional: bool = False
) -> List[Optional[List[float]]]:
    embeddings = _random_embeddings(count, seed, dim, optional).tolist()
    return [
        embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
        for embedding in embeddings
    ]


def _random_choice(
    options: Sequence[Optional[str]], count: int, seed: int
) -> List[Optional[str]]:
    np.random.seed(seed)
    return np.random.choice(options, count, replace=True).tolist()  # type: ignore


@click.command()  # type: ignore
@click.option(
    "-o",
    "--output-folder",
    type=click.Path(exists=True, file_okay=False, writable=True),
    help="output folder",
    default=".",
)
@click.option("--num-rows", type=int, help="target row count", default=1000)
@click.option("--seed", type=int, help="random seed", default=42)
def generate_test_csv(output_folder: str, num_rows: int, seed: int) -> None:
    """
    Generate multimodal CSV dataset.
    """
    df = pd.DataFrame()

    audio_options = sorted(map(str, AUDIO_FOLDER.rglob("*")))
    image_options = sorted(map(str, IMAGE_FOLDER.glob("*")))
    mesh_options = sorted(map(str, MESH_FOLDER.glob("*")))
    video_options = sorted(map(str, VIDEO_FOLDER.glob("*")))

    audio_options += ["/tmp/non-existing.txt", image_options[0], None]  # type: ignore
    image_options += ["/tmp/non-existing.txt", mesh_options[0], None]  # type: ignore
    mesh_options += ["/tmp/non-existing.txt", video_options[0], None]  # type: ignore
    video_options += ["/tmp/non-existing.txt", audio_options[0], None]  # type: ignore

    df["audio"] = audio_options + _random_choice(
        audio_options, num_rows - len(audio_options), seed
    )
    df["image"] = image_options + _random_choice(
        image_options, num_rows - len(image_options), seed + 1
    )
    df["mesh"] = mesh_options + _random_choice(
        mesh_options, num_rows - len(mesh_options), seed + 2
    )
    df["video"] = video_options + _random_choice(
        video_options, num_rows - len(video_options), seed + 3
    )
    df["embedding"] = _random_embeddings_list(num_rows, seed + 4, 4, optional=True)
    df["window"] = _random_embeddings_list(num_rows, seed + 5, 2, optional=True)
    # df["datetime"] = pd.to_datetime(_random_data(datetime.datetime, num_rows, seed + 6))
    for i, data_type in enumerate(
        (
            bool,
            int,
            float,
            str,
            datetime.datetime,
            spotlight.Category,
        )
    ):
        df[data_type.__name__.lower()] = _random_data(data_type, num_rows, seed + 6 + i)

    output_file = Path(output_folder) / f"multimodal-random-{num_rows}.csv"
    # print(df.dtypes)
    df.to_csv(output_file, index=False)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    generate_test_csv()  # type: ignore
