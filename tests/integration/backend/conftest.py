"""
Helper methods for tests
"""

import tempfile
from collections.abc import Iterator
from urllib.parse import urljoin

import numpy as np
import pandas as pd
import pytest

from renumics import spotlight

BASE_URL = "https://spotlightpublic.blob.core.windows.net/internal-test-data/"


def _example_df(row_count: int = 50) -> pd.DataFrame:
    """
    a dataframe with an integer, a text and an embedding column, every tenth
    embedding is missing
    """
    rng = np.random.default_rng(42)
    return pd.DataFrame(
        {
            "number": range(row_count),
            "even_text": ["even" if i % 2 == 0 else "odd" for i in range(row_count)],
            "encoded": [
                None if i % 10 == 0 else rng.normal(size=12) for i in range(row_count)
            ],
        }
    )


@pytest.fixture()
def viewer_csv_df() -> Iterator[spotlight.Viewer]:
    """setup a viewer with loaded dataframe"""
    csv_df = pd.read_csv("data/csv/multimodal-random-small.csv")
    viewer = spotlight.show(
        csv_df,
        host="127.0.0.1",
        no_browser=True,
        port="auto",
        wait=False,
        dtype={
            "audio": spotlight.Audio,
            "embedding": spotlight.Embedding,
            "image": spotlight.Image,
            "mesh": spotlight.Mesh,
            "video": spotlight.Video,
            "window": spotlight.Window,
        },
    )
    yield viewer
    viewer.close()


@pytest.fixture()
def viewer_tally_df() -> Iterator[spotlight.Viewer]:
    """setup a viewer with a dataframe with external audio and images"""
    df = _example_df()

    # Valid external data
    df["audio"] = None
    df["image"] = None
    df.at[0, "audio"] = "data/audio/stereo/gs-16b-2c-44100hz.mp3"
    df.at[1, "audio"] = urljoin(BASE_URL, "gs-16b-2c-44100hz.ogg")
    df.at[2, "audio"] = None
    df.at[0, "image"] = "data/images/nature-360p.jpg"
    df.at[1, "image"] = urljoin(BASE_URL, "nature-360p.bmp")
    df.at[2, "image"] = None
    # Invalid external data
    df.at[4, "audio"] = "data/images/nature-360p.jpg"
    df.at[5, "audio"] = "foo"
    df.at[4, "image"] = "data/audio/stereo/gs-16b-2c-44100hz.mp3"
    df.at[5, "image"] = "foo"

    viewer = spotlight.show(
        df,
        "127.0.0.1",
        no_browser=True,
        port="auto",
        wait=False,
        dtype={
            "audio": spotlight.Audio,
            "image": spotlight.Image,
            "encoded": spotlight.Embedding,
        },
    )
    yield viewer
    viewer.close()


@pytest.fixture()
def viewer_double_tally_df() -> Iterator[tuple[spotlight.Viewer, spotlight.Viewer]]:
    """setup two viewers with different dataframes"""
    df = _example_df()
    viewer = spotlight.show(
        df,
        "127.0.0.1",
        no_browser=True,
        port="auto",
        wait=False,
        dtype={"encoded": spotlight.Embedding},
    )

    df2 = _example_df()
    df2["number"] = df2["number"] + 2000
    viewer2 = spotlight.show(
        df2,
        "127.0.0.1",
        no_browser=True,
        port="auto",
        wait=False,
        dtype={"encoded": spotlight.Embedding},
    )
    yield viewer, viewer2
    viewer.close()
    viewer2.close()


@pytest.fixture()
def non_existing_image_df_viewer() -> Iterator[spotlight.Viewer]:
    """
    Setup a viewer with a single non-existing external image inside.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        df = pd.DataFrame({"image": [f"{temp_dir}/image.jpg"]})
        viewer = spotlight.show(
            df,
            "127.0.0.1",
            no_browser=True,
            port="auto",
            wait=False,
            dtype={"image": spotlight.Image},
        )
        yield viewer
        viewer.close()
