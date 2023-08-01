#!/usr/bin/env python3

"""
generate spotlight test dataset
"""

import os
import datetime
from typing import Dict, Optional, Union

from pathlib import Path
import click

import numpy as np
import sklearn.utils
import trimesh
from scipy.io import wavfile
from sklearn import datasets
from sklearn.decomposition import PCA

from renumics.spotlight import Dataset, Embedding, Image, Mesh, Sequence1D, Audio, Video


@click.command()  # type: ignore
@click.option(
    "--output-path",
    "-o",
    type=click.Path(file_okay=False, dir_okay=True, writable=True),
    help="output folder",
    default=Path("."),
)
def generate_tallymarks_dataset(
    output_path: Path,
) -> None:
    """
    Generate a test dataset based on mnist with
        - picture of hand-writen digit as Image
        - 2x 3D slashes with count=label as Mesh (one animated)
        - 2 Sequence1D converging to label and label*100
        - 1 Sequence 1D converging to label but with different ends and starts
        - An embedding of the image (d=3)
        - Other values for primitive data_types
    """

    number_of_images = 50
    digits: sklearn.utils.Bunch = datasets.load_digits()

    coords = PCA(n_components=12).fit_transform(digits.data)
    encoded = [Embedding(coord) for coord in coords]

    output_h5_file = os.path.join(output_path, "tallymarks_dataset_small.h5")
    with Dataset(output_h5_file, "w") as dataset:
        dataset.append_int_column(
            "number",
            optional=True,
            default=-1,
            description="This is just the `number` value, converted to float.",
        )
        dataset.append_image_column("image", optional=True)
        dataset.append_embedding_column("encoded", optional=True)
        dataset.append_mesh_column("mesh", optional=True, description="optional")

        for image, label, encoded_row in list(
            zip(digits.images, digits.target, encoded)
        )[:number_of_images]:
            dataset.append_row(
                number=int(label) if label > 0 else None,
                encoded=encoded_row if label > 0 else None,
                image=_image(image, label) if label > 0 else None,
                mesh=_mesh(label) if label > 0 else None,
            )

    output_h5_file = os.path.join(output_path, "tallymarks_dataset.h5")
    with Dataset(output_h5_file, "w") as dataset:
        dataset.append_float_column(
            "length",
            optional=True,
            description="[optional, editable] This is just the `number` value, converted to float.",
        )
        dataset.append_image_column("image", optional=True)

        dataset.append_bool_column(
            "even",
            description="[optional, editable] A very long description with hyphens: "
            + "foo-bar-baz-" * 50,
        )
        dataset.append_int_column(
            "number",
            optional=True,
            default=-1,
            description="[optional, editable]",
        )
        dataset.append_categorical_column(
            "number_cat",
            optional=True,
            description="[optional, editable]",
            categories=[_category(i) for i in range(10)],
        )

        dataset.append_string_column(
            "even_text",
            optional=True,
            description="[optional, editable] A very long description without hyphens: "
            + "foobarbaz" * 50,
        )
        dataset.append_datetime_column(
            "now",
            optional=True,
            description="[optional, editable] Current datetime.",
        )
        dataset.append_array_column("to_number")
        dataset.append_sequence_1d_column("sequence_to_number", optional=True)
        dataset.append_sequence_1d_column(
            "sequence_1_100_to_number",
            description="scaled offset `sequence_to_number`.",
        )
        dataset.append_sequence_1d_column(
            "sequence_2_100_to_number",
            description="scaled offset `sequence_to_number`.",
        )
        dataset.append_sequence_1d_column(
            "sequence_different_end_to_number",
            description="`sequence_to_number` with different ends and starts.",
        )
        dataset.append_sequence_1d_column("sequence_tiny")
        dataset.append_sequence_1d_column("sequence_huge")
        dataset.append_mesh_column("mesh", optional=True, description="optional")
        dataset.append_mesh_column("mesh_animated", description="with animation")
        dataset.append_mesh_column("mesh_interpolated")
        dataset.append_embedding_column("encoded", optional=True)

        dataset.append_audio_column(
            "audio",
            optional=True,
            lookup={"3": _audio_signal(3), "7": _audio_signal(7)},
        )
        dataset.append_video_column("video", optional=True)

        videos_lookup: Dict[int, Union[str, None, Video]] = {
            number: None for number in list(range(1, 10))
        }
        videos_lookup[1] = Video.empty()
        for i, filename in enumerate(list(os.listdir("data/videos"))):
            videos_lookup[i + 2] = os.path.join("data/videos", filename)

        for image, label, encoded_row in list(
            zip(digits.images, digits.target, encoded)
        )[:number_of_images]:
            mesh_interpolated = _mesh(label, animate=True)
            mesh_interpolated.interpolate_point_displacements(20)
            sequence_start = 15 if label % 4 < 2 else 0
            sequence_stop = 35 if label % 2 == 0 else 50
            dataset.append_row(
                even=bool(label % 2 == 0),
                number=int(label) if label > 0 else None,
                length=float(label) if label > 0 else float("nan"),
                even_text="even" if label % 2 == 0 else "odd",
                now=datetime.datetime.utcnow() if label > 0 else None,
                to_number=np.array([float(i) for i in range(label)]),
                sequence_to_number=_sequence(label) if label > 0 else None,
                sequence_1_100_to_number=_sequence((1 + label) * 100),
                sequence_2_100_to_number=_sequence((2 + label) * 100),
                sequence_different_end_to_number=_sequence(
                    label, start=sequence_start, stop=sequence_stop
                ),
                sequence_tiny=_sequence_lin(label * 0.000001),
                sequence_huge=_sequence_lin(label * 100000),
                mesh=_mesh(label) if label > 0 else None,
                mesh_animated=_mesh(label, animate=True),
                mesh_interpolated=mesh_interpolated,
                encoded=encoded_row if label > 0 else None,
                image=_image(image, label) if label > 0 else None,
                audio=_audio_signal(label) if label > 0 else None,
                number_cat=_category(label) if label > 0 else None,
                video=videos_lookup[int(label)] if label > 0 else None,
            )
        windows = np.random.uniform(0, 0.5, (len(dataset), 2))
        windows[:3, 0] = np.nan
        windows[3:6, 1] = np.nan
        windows[6:9] = np.nan
        dataset.append_window_column("window", windows, tags=["editable"])
        dataset.append_window_column(
            "window2", windows, optional=True, tags=["editable", "optional"]
        )
        dataset.append_window_column(
            "window_frozen", windows, optional=True, editable=False, tags=["optional"]
        )
        dataset.set_column_attributes("mesh", tags=["quick_view"])
        dataset.set_column_attributes("to_number", tags=["quick_view"])
        dataset.set_column_attributes(
            "sequence_1_100_to_number", tags=["quick_view", "advanced_view"]
        )
        dataset.set_column_attributes(
            "sequence_2_100_to_number", tags=["advanced_view"]
        )
        dataset.set_column_attributes("mesh_animated", tags=["advanced_view"])


def _category(number: int) -> str:
    return [
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
        "ten",
    ][number]


def _sequence(target_number: int, start: int = 0, stop: int = 50) -> Sequence1D:
    x = np.linspace(start=start, stop=stop, num=100)
    y = np.sin(x) * np.exp(-x / 10) + target_number
    return Sequence1D(x, y)


def _sequence_lin(target_number: int) -> Sequence1D:
    x = np.linspace(start=0, stop=50, num=100)
    y = (x / 50) * target_number
    return Sequence1D(x, y)


def _audio_signal(target_number: int) -> Union[Audio, str]:
    filepath = f"data/audio/{target_number}.wav"
    if target_number % 2:
        return filepath
    samplingrate, audio_signal = wavfile.read(filepath)
    return Audio(samplingrate, audio_signal)


def _mesh(length: int, animate: bool = False) -> Mesh:
    if length == 0:
        length = 10
    translation = [2, 0, 0]
    trimesh_mesh = trimesh.creation.box(extents=[1, 10, 1])
    for _ in range(length - 1):
        trimesh_mesh.apply_translation(translation)
        trimesh_mesh = trimesh_mesh + trimesh.creation.box(extents=[1, 10, 1])

    points = trimesh_mesh.vertices
    faces = trimesh_mesh.faces
    step_displacements = np.array(
        [[0, length % 2 - 1, length % 2] for _ in range(len(points))]
    )
    displacements = [i * step_displacements for i in range(10)] if animate else None
    attr1 = np.array([i // 10 for i in range(len(points))])
    return Mesh(
        points,
        faces,
        point_displacements=displacements,
        point_attributes={"attr1": attr1},
    )


def _image(digits_image: np.ndarray, label: Optional[int] = None) -> Image:
    image = (np.ones_like(digits_image) * 255 - (digits_image / 16 * 255)).astype(
        np.uint8
    )
    # scale image along each dimension in order to display it in the browser
    scale = 24
    if label is not None:
        scale += label
    image = np.repeat(image, scale, axis=1)
    image = np.repeat(image, scale, axis=0)
    # transpose and convert grey scale to rgb
    # image_rgb = np.swapaxes(np.array(3 * [image.T * 10], dtype=np.uint8), 0, 2)
    if label is not None:
        if label > 2:
            # 3-dimensional grayscale image with the last dimension equal to 1.
            image = np.expand_dims(image, axis=-1)
        if label > 4:
            # RGB image
            image = np.concatenate([image] * 3, axis=-1)
        if label > 7:
            # RGBA image with alpha-channel equal to 200
            image = np.append(
                image, np.full((*image.shape[:2], 1), 200, image.dtype), axis=-1
            )
    return Image(image)


if __name__ == "__main__":
    generate_tallymarks_dataset()  # type: ignore
