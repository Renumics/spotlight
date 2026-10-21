"""Small synthetic tables for ui-tests"""

from pathlib import Path
from typing import List, Union

from renumics.spotlight import Dataset

#: videos of the repository that tables of this module refer to
VIDEO_FILES = [
    "data/videos/sea-360p-10s.mp4",
    "data/videos/sea-360p.webm",
    "data/videos/sea-360p.mp4",
]


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
    path.parent.mkdir(parents=True, exist_ok=True)
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
