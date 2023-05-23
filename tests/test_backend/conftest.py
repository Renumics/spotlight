"""
Helper methods for tests
"""
from typing import Iterator, Tuple
from urllib.parse import urljoin

import pytest
from fastapi.testclient import TestClient
import pandas as pd

from renumics import spotlight
from renumics.spotlight.backend import create_datasource


BASE_URL = "https://spotlightpublic.blob.core.windows.net/internal-test-data/"


@pytest.fixture()
def viewer_weather_df() -> Iterator[spotlight.Viewer]:
    """setup a viewer with loaded dataframe"""
    csv_df = pd.read_csv("data/csv/australian-weather-small.csv")
    viewer = spotlight.show(
        csv_df,
        "127.0.0.1",
        no_browser=True,
        port="auto",
        wait=False,
        dtype={"WindGustSpeed": str},
    )
    yield viewer
    viewer.close()


@pytest.fixture()
def viewer_tally_df() -> Iterator[spotlight.Viewer]:
    """setup a viewer with exported dataframe"""
    with spotlight.Dataset("build/datasets/tallymarks_dataset.h5", "r") as dataset:
        df = dataset.to_pandas()
        df["encoded"] = dataset["encoded"]

    # Valid external data
    df["audio"] = ""
    df["image"] = ""
    df.at[0, "audio"] = "data/audio/stereo/gs-16b-2c-44100hz.mp3"
    df.at[1, "audio"] = urljoin(BASE_URL, "gs-16b-2c-44100hz.ogg")
    df.at[2, "audio"] = None
    df.at[0, "image"] = "data/images/lena.jpg"
    df.at[1, "image"] = urljoin(BASE_URL, "lena.bmp")
    df.at[2, "image"] = None
    # Invalid external data
    df.at[4, "audio"] = "data/images/lena.jpg"
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
def viewer_double_tally_df() -> Iterator[Tuple[spotlight.Viewer, spotlight.Viewer]]:
    """setup a viewer with exported dataframe"""
    with spotlight.Dataset("build/datasets/tallymarks_dataset.h5", "r") as dataset:
        df = dataset.to_pandas()
        df["encoded"] = [
            embedding if embedding is not None else None
            for embedding in dataset["encoded"]  # pylint: disable=(not-an-iterable)
        ]
    viewer = spotlight.show(
        df,
        "127.0.0.1",
        no_browser=True,
        port="auto",
        wait=False,
    )

    with spotlight.Dataset("build/datasets/tallymarks_dataset.h5", "r") as dataset:
        df2 = dataset.to_pandas()
        df2["encoded"] = [
            embedding if embedding is not None else None
            for embedding in dataset["encoded"]  # pylint: disable=(not-an-iterable)
        ]
    df2["number"] = df2["number"] + 2000
    viewer2 = spotlight.show(
        df2,
        "127.0.0.1",
        no_browser=True,
        port="auto",
        wait=False,
    )
    yield viewer, viewer2
    viewer.close()
    viewer2.close()


@pytest.fixture()
def testclient() -> TestClient:
    """setup API client with loaded spotlight h5 file in backend"""

    # pylint: disable=import-outside-toplevel
    from renumics.spotlight.backend.app import create_app

    app = create_app()
    app.data_source = create_datasource("build/datasets/tallymarks_dataset.h5")
    return TestClient(app)
