"""Synthetic tables for ui-tests"""

import datetime
from pathlib import Path
from typing import List, Union

import numpy as np
import trimesh
from sklearn.datasets import load_digits

from renumics.spotlight import Dataset, Image, Mesh, Sequence1D

#: videos of the repository that tables of this module refer to
VIDEO_FILES = [
    "data/videos/sea-360p-10s.mp4",
    "data/videos/sea-360p.webm",
    "data/videos/sea-360p.mp4",
]

DIGIT_NAMES = [
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
]


def _digit_image(pixels: np.ndarray, label: int) -> Image:
    """
    An upscaled digit, dark on light, as greyscale, RGB or RGBA image depending on
    the label.
    """
    image = (255 - pixels / 16 * 255).astype(np.uint8)
    image = np.repeat(np.repeat(image, 24, axis=0), 24, axis=1)
    if label > 2:
        image = image[..., np.newaxis]
    if label > 4:
        image = np.concatenate([image] * 3, axis=-1)
    if label > 7:
        alpha = np.full((*image.shape[:2], 1), 200, np.uint8)
        image = np.concatenate([image, alpha], axis=-1)
    return Image(image)


def _tally_mesh(count: int) -> Mesh:
    """`count` bars next to each other"""
    bars = [
        trimesh.creation.box(extents=[1, 10, 1]).apply_translation([2 * i, 0, 0])
        for i in range(count)
    ]
    mesh = trimesh.util.concatenate(bars)
    return Mesh(mesh.vertices, mesh.faces)


def _damped_sine(target: int) -> Sequence1D:
    """a sequence which converges to `target`"""
    x = np.linspace(0, 50, 100)
    return Sequence1D(x, np.sin(x) * np.exp(-x / 10) + target)


def write_image_example_table(path: Union[str, Path], row_count: int = 50) -> Path:
    """
    Write a table with the hand-written digits of scikit-learn for screenshots and
    the similarity map: a column of every common data type and an embedding of the
    digit images. The media and embedding of the zeros are missing.
    """
    path = Path(path)
    digits = load_digits()
    start = datetime.datetime(2024, 1, 1, 12)
    with Dataset(path, "w") as dataset:
        dataset.append_int_column("number")
        dataset.append_categorical_column("name", categories=DIGIT_NAMES)
        dataset.append_bool_column("even")
        dataset.append_string_column("parity")
        dataset.append_float_column("ink")
        dataset.append_datetime_column("recorded")
        dataset.append_image_column("image", optional=True)
        dataset.append_embedding_column("embedding", optional=True)
        dataset.append_mesh_column("mesh", optional=True)
        dataset.append_sequence_1d_column("sequence", optional=True)
        dataset.append_audio_column("audio", optional=True)
        dataset.append_video_column("video", optional=True)
        for row in range(row_count):
            label = int(digits.target[row])
            missing = label == 0
            dataset.append_row(
                number=label,
                name=DIGIT_NAMES[label],
                even=label % 2 == 0,
                parity="even" if label % 2 == 0 else "odd",
                ink=float(digits.data[row].mean()),
                recorded=start + datetime.timedelta(hours=row),
                image=None if missing else _digit_image(digits.images[row], label),
                embedding=None if missing else digits.data[row],
                mesh=None if missing else _tally_mesh(label),
                sequence=None if missing else _damped_sine(label),
                audio=None if missing else f"data/audio/{label}.wav",
                video=None if missing else VIDEO_FILES[row % len(VIDEO_FILES)],
            )
    return path


def write_performance_table(
    path: Union[str, Path],
    embedding_column_count: int,
    embedding_size: int,
    row_count: int = 5000,
) -> Path:
    """
    Write a large table of random data to measure the loading time: a string, a float
    and an array column and the given number of embedding columns.
    """
    path = Path(path)
    rng = np.random.default_rng(42)
    with Dataset(path, "w") as dataset:
        dataset.append_string_column("string", ["string"] * row_count)
        dataset.append_float_column("float", rng.random(row_count))
        dataset.append_array_column(
            "embeddings_as_array", list(rng.random((row_count, embedding_size)))
        )
        for column in range(embedding_column_count):
            dataset.append_embedding_column(
                f"encoded_{column}", rng.random((row_count, embedding_size))
            )
    return path


def selection_example_texts(row_count: int) -> List[str]:
    """Texts for the `note` column of the selection example table, some of them
    long (the table payload truncates them), some with commas, quotes and line breaks,
    some with emoji."""
    texts = []
    for row in range(row_count):
        if row % 7 == 3:
            texts.append(f"synthetic sentence number {row} " * 8)
        elif row % 11 == 5:
            texts.append(f'say "hi" {row}\nsecond line')
        elif row % 13 == 9:
            # characters outside the BMP count as one for the backend, as two in JavaScript
            texts.append(f"emoji \U0001f600\U0001f680 number {row} " + "x" * 100)
        else:
            texts.append(f"short, with comma {row}")
    return texts


def selection_example_ids(row_count: int) -> List[str]:
    """Values of the `id` column of the selection example table"""
    return [f"item-{row:04d}" for row in range(row_count)]


def write_selection_example_table(path: Union[str, Path], row_count: int = 40) -> Path:
    """
    Write a table with made-up data to test selecting rows, copying and exporting:
    an id, an integer, a float, a category, a text and a video column.
    """
    path = Path(path)
    texts = selection_example_texts(row_count)
    with Dataset(path, "w") as dataset:
        dataset.append_string_column("id")
        dataset.append_int_column("number")
        dataset.append_float_column("score")
        dataset.append_categorical_column("group", categories=["a", "b", "c"])
        dataset.append_string_column("note")
        dataset.append_video_column("video", optional=True)
        for row, identifier in enumerate(selection_example_ids(row_count)):
            dataset.append_row(
                id=identifier,
                number=(row * 7919) % 1000,
                score=((row * 13) % 100) / 8,
                group="abc"[row % 3],
                note=texts[row],
                video=VIDEO_FILES[row % len(VIDEO_FILES)],
            )
    return path
