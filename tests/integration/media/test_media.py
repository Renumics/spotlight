"""
Test custom data types.
"""
import io
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import numpy as np
import pytest

from renumics.spotlight import Audio, Embedding, Mesh, Sequence1D, Image, Video
from ..dataset.conftest import approx


SEED = 42
BASE_URL = "https://spotlightpublic.blob.core.windows.net/internal-test-data/"


class TestEmbedding:
    """
    Test `renumics.spotlight.Embedding` class.
    """

    @pytest.mark.parametrize("length", [1, 10, 100])
    @pytest.mark.parametrize("dtype", ["float32", "float64", "uint16", "int32"])
    @pytest.mark.parametrize("input_type", ["array", "list", "tuple"])
    def test_embedding(self, length: int, dtype: str, input_type: str) -> None:
        """
        Test Embedding class initialization and to/from array conversion.
        """
        np_dtype = np.dtype(dtype)
        if np_dtype.str[1] == "f":
            np.random.seed(SEED)
            array = np.random.uniform(0, 1, length).astype(dtype)
        else:
            np.random.seed(SEED)
            array = np.random.randint(  # type: ignore
                np.iinfo(np_dtype).min, np.iinfo(np_dtype).max, length, dtype
            )
        if input_type == "list":
            array = array.tolist()
        elif input_type == "tuple":
            array = tuple(array.tolist())  # type: ignore
        embedding = Embedding(array)

        assert approx(array, embedding.data, "Embedding")
        encoded_embedding = embedding.encode()
        decoded_embedding = Embedding.decode(encoded_embedding)
        assert approx(embedding, decoded_embedding.data, "Embedding")

    @pytest.mark.parametrize("input_type", ["array", "list", "tuple"])
    def test_zero_length_embedding(self, input_type: str) -> None:
        """
        Test if `Embedding` fails with zero-length data.
        """
        array = np.empty(0)
        if input_type == "list":
            array = array.tolist()
        elif input_type == "tuple":
            array = tuple(array.tolist())  # type: ignore
        with pytest.raises(ValueError):
            _ = Embedding(array)

    @pytest.mark.parametrize("num_dims", [0, 2, 3, 4])
    def test_multidimensional_embedding(self, num_dims: int) -> None:
        """
        Test if `Embedding` fails with not one-dimensional data.
        """
        np.random.seed(SEED)
        dims = np.random.randint(1, 20, num_dims)
        np.random.seed(SEED)
        array = np.random.uniform(0, 1, dims)
        with pytest.raises(ValueError):
            _ = Embedding(array)


@pytest.mark.parametrize("length", [1, 10, 100])
@pytest.mark.parametrize("input_type", ["array", "list", "tuple"])
def test_sequence_1d(length: int, input_type: str) -> None:
    """
    Test `renumics.spotlight.Sequence1D` class.
    """
    index = np.random.rand(length)
    value = np.random.rand(length)
    if input_type == "list":
        index = index.tolist()
        value = value.tolist()
    elif input_type == "tuple":
        index = tuple(index.tolist())  # type: ignore
        value = tuple(value.tolist())  # type: ignore
    # Initialization with index and value.
    sequence_1d = Sequence1D(index, value)
    assert approx(index, sequence_1d.index, "array")
    assert approx(value, sequence_1d.value, "array")
    encoded_sequence_1d = sequence_1d.encode()
    decoded_sequence_1d = Sequence1D.decode(encoded_sequence_1d)
    assert approx(sequence_1d, decoded_sequence_1d, "Sequence1D")
    # Initialization with value only.
    sequence_1d = Sequence1D(value)
    assert approx(np.arange(len(value)), sequence_1d.index, "array")
    assert approx(value, sequence_1d.value, "array")
    encoded_sequence_1d = sequence_1d.encode()
    decoded_sequence_1d = Sequence1D.decode(encoded_sequence_1d)
    assert approx(sequence_1d, decoded_sequence_1d, "Sequence1D")


class TestImage:
    """
    Test `renumics.spotlight.Image` class.
    """

    data_folder = Path("data/images")

    @pytest.mark.parametrize("size", [1, 10, 100])
    @pytest.mark.parametrize("num_channels", [None, 1, 3, 4])
    @pytest.mark.parametrize("dtype", ["float32", "float64", "uint8", "int32"])
    @pytest.mark.parametrize("input_type", ["array", "list", "tuple"])
    def test_image_from_array(
        self, size: int, num_channels: Optional[int], dtype: str, input_type: str
    ) -> None:
        """
        Test image creation.
        """
        shape = (size, size) if num_channels is None else (size, size, num_channels)
        np_dtype = np.dtype(dtype)
        if np_dtype.str[1] == "f":
            np.random.seed(SEED)
            array = np.random.uniform(0, 1, shape).astype(dtype)
            target = (255 * array).round().astype("uint8")
        else:
            np.random.seed(SEED)
            array = np.random.randint(0, 256, shape, dtype)  # type: ignore
            target = array.astype("uint8")
        if num_channels == 1:
            target = target.squeeze(axis=2)
        if input_type == "list":
            array = array.tolist()
        elif input_type == "tuple":
            array = tuple(array.tolist())  # type: ignore
        image = Image(array)

        assert approx(target, image.data, "Image")
        encoded_image = image.encode()
        decoded_image = Image.decode(encoded_image)
        assert approx(image, decoded_image, "Image")

    @pytest.mark.parametrize(
        "filename",
        [
            "nature-256p.ico",
            "nature-360p.bmp",
            "nature-360p.gif",
            "nature-360p.jpg",
            "nature-360p.png",
            "nature-360p.tif",
            "nature-360p.webp",
            "nature-720p.jpg",
            "nature-1080p.jpg",
            "sea-360p.gif",
            "sea-360p.apng",
        ],
    )
    def test_image_from_filepath(self, filename: str) -> None:
        """
        Test reading image from an existing file.
        """
        filepath = self.data_folder / filename
        assert filepath.is_file()
        _ = Image.from_file(str(filepath))
        _ = Image.from_file(filepath)

    @pytest.mark.parametrize(
        "filename",
        [
            "nature-256p.ico",
            "nature-360p.bmp",
            "nature-360p.gif",
            "nature-360p.jpg",
            "nature-360p.png",
            "nature-360p.tif",
            "nature-360p.webp",
            "nature-720p.jpg",
            "nature-1080p.jpg",
            "sea-360p.gif",
            "sea-360p.apng",
        ],
    )
    def test_image_from_file(self, filename: str) -> None:
        """
        Test reading image from a file descriptor.
        """
        filepath = self.data_folder / filename
        assert filepath.is_file()
        with filepath.open("rb") as file:
            _ = Image.from_file(file)

    @pytest.mark.parametrize(
        "filename",
        [
            "nature-256p.ico",
            "nature-360p.bmp",
            "nature-360p.gif",
            "nature-360p.jpg",
            "nature-360p.png",
            "nature-360p.tif",
            "nature-360p.webp",
            "nature-720p.jpg",
            "nature-1080p.jpg",
            "sea-360p.gif",
            "sea-360p.apng",
        ],
    )
    def test_image_from_io(self, filename: str) -> None:
        """
        Test reading image from an IO object.
        """
        filepath = self.data_folder / filename
        assert filepath.is_file()
        with filepath.open("rb") as file:
            blob = file.read()
            buffer = io.BytesIO(blob)
            _ = Image.from_file(buffer)

    @pytest.mark.parametrize(
        "filename",
        [
            "nature-256p.ico",
            "nature-360p.bmp",
            "nature-360p.gif",
            "nature-360p.jpg",
            "nature-360p.png",
            "nature-360p.tif",
            "nature-360p.webp",
            "nature-720p.jpg",
            "nature-1080p.jpg",
            "sea-360p.gif",
            "sea-360p.apng",
        ],
    )
    def test_image_from_bytes(self, filename: str) -> None:
        """
        Test reading image from bytes.
        """
        filepath = self.data_folder / filename
        assert filepath.is_file()
        with filepath.open("rb") as file:
            blob = file.read()
            _ = Image.from_bytes(blob)

    @pytest.mark.parametrize(
        "filename",
        [
            "nature-256p.ico",
            "nature-360p.bmp",
            "nature-360p.gif",
            "nature-360p.jpg",
            "nature-360p.png",
            "nature-360p.tif",
            "nature-360p.webp",
            "nature-720p.jpg",
            "nature-1080p.jpg",
            "sea-360p.gif",
            "sea-360p.apng",
        ],
    )
    def test_image_from_url(self, filename: str) -> None:
        """
        Test reading image from a URL.
        """
        url = urljoin(BASE_URL, filename)
        _ = Image.from_file(url)


class TestMesh:
    """
    Test `renumics.spotlight.Mesh` class.
    """

    seed = 42
    data_folder = Path("data/meshes")

    @pytest.mark.parametrize("num_points", [10, 100, 10000])
    @pytest.mark.parametrize("num_triangles", [10, 100, 10000])
    def test_mesh_from_array(self, num_points: int, num_triangles: int) -> None:
        """
        Test mesh creation.
        """
        points = np.random.random((num_points, 3))
        triangles = np.random.randint(0, num_points, (num_triangles, 3))
        mesh = Mesh(
            points,
            triangles,
            {
                "float32": np.random.rand(num_points).astype("float32"),
                "float64_3": np.random.rand(num_points, 3).astype("float64"),
                "float16_4": np.random.rand(num_points, 4).astype("float16"),
                "uint64_1": np.random.randint(0, num_points, (num_points, 1), "uint64"),
                "int16": np.random.randint(-10000, 10000, num_points, "int16"),
            },
            {
                "float32_1": np.random.rand(num_triangles, 1).astype("float32"),
                "float64_3": np.random.rand(num_triangles, 3).astype("float64"),
                "float32_4": np.random.rand(num_triangles, 4).astype("float32"),
                "uint32": np.random.randint(
                    0, np.iinfo("uint32").max, num_triangles, "uint32"
                ),
                "int64_1": np.random.randint(
                    -10000, 10000, (num_triangles, 1), "int64"
                ),
            },
            [np.random.random((num_points, 3)) for _ in range(10)],
        )
        assert len(mesh.points) <= len(triangles) * 3
        assert len(mesh.triangles) <= len(triangles)
        encoded_mesh = mesh.encode()
        decoded_mesh = Mesh.decode(encoded_mesh)
        assert approx(mesh, decoded_mesh, "Mesh")

    @pytest.mark.parametrize(
        "filename",
        [
            "tree.ascii.stl",
            "tree.glb",
            "tree.gltf",
            "tree.obj",
            "tree.off",
            "tree.ply",
            "tree.stl",
        ],
    )
    def test_mesh_from_filepath(self, filename: str) -> None:
        """
        Test reading mesh from an existing file.
        """
        filepath = self.data_folder / filename
        assert filepath.is_file()
        _ = Mesh.from_file(str(filepath))
        _ = Mesh.from_file(filepath)

    @pytest.mark.parametrize(
        "filename",
        [
            "tree.ascii.stl",
            "tree.glb",
            "tree.gltf",
            "tree.obj",
            "tree.off",
            "tree.ply",
            "tree.stl",
        ],
    )
    def test_mesh_from_url(self, filename: str) -> None:
        """
        Test reading mesh from a URL.
        """
        url = urljoin(BASE_URL, filename)
        _ = Mesh.from_file(url)


class TestAudio:
    """
    Test `renumics.spotlight.Audio` class.
    """

    data_folder = Path("data/audio")

    @pytest.mark.parametrize("sampling_rate", [100, 8000, 44100, 48000, 96000])
    @pytest.mark.parametrize("channels", [1, 2, 5])
    @pytest.mark.parametrize("length", [0.5, 1.0, 2.0])
    @pytest.mark.parametrize("dtype", ["f4", "i2", "u1"])
    @pytest.mark.parametrize("target", ["wav", "flac"])
    def test_lossless_audio(
        self,
        sampling_rate: int,
        channels: int,
        length: float,
        dtype: str,
        target: Optional[str],
    ) -> None:
        """
        Test audio creation and lossless saving.
        """

        time = np.linspace(0.0, length, round(sampling_rate * length))
        y = 0.4 * np.sin(2.0 * np.pi * 100 * time)
        if dtype.startswith("f"):
            data = y.astype(dtype)
        elif dtype.startswith("i"):
            data = (y * np.iinfo(dtype).max).astype(dtype)
        elif dtype.startswith("u"):
            data = ((y + 1) * np.iinfo(dtype).max / 2).astype(dtype)
        else:
            assert False
        if channels > 1:
            data = np.broadcast_to(data[:, np.newaxis], (len(data), channels))
        audio = Audio(sampling_rate, data)

        encoded_audio = audio.encode(target)
        decoded_audio = Audio.decode(encoded_audio)

        decoded_sr = decoded_audio.sampling_rate
        decoded_data = decoded_audio.data

        assert decoded_sr == sampling_rate
        assert decoded_data.shape == (len(y), channels)

    @pytest.mark.parametrize("sampling_rate", [32000, 44100, 48000])
    @pytest.mark.parametrize("channels", [1, 2])
    @pytest.mark.parametrize("length", [0.5, 1.0, 2.0])
    @pytest.mark.parametrize("dtype", ["f4", "i2", "u1"])
    def test_lossy_audio(
        self, sampling_rate: int, channels: int, length: float, dtype: str
    ) -> None:
        """
        Test audio creation and lossy saving.
        """
        time = np.linspace(0.0, length, round(sampling_rate * length))
        y = 0.4 * np.sin(2.0 * np.pi * 100 * time)
        if dtype.startswith("f"):
            data = y.astype(dtype)
        elif dtype.startswith("i"):
            data = (y * np.iinfo(dtype).max).astype(dtype)
        elif dtype.startswith("u"):
            data = ((y + 1) * np.iinfo(dtype).max / 2).astype(dtype)
        else:
            assert False
        if channels > 1:
            data = np.broadcast_to(data[:, np.newaxis], (len(data), channels))
        audio = Audio(sampling_rate, data)

        encoded_audio = audio.encode("ogg")
        decoded_audio = Audio.decode(encoded_audio)

        decoded_sr = decoded_audio.sampling_rate
        _decoded_data = decoded_audio.data

        assert decoded_sr == sampling_rate

    @pytest.mark.parametrize(
        "filename",
        [
            "gs-16b-1c-44100hz.aac",
            "gs-16b-1c-44100hz.ac3",
            "gs-16b-1c-44100hz.aiff",
            "gs-16b-1c-44100hz.flac",
            "gs-16b-1c-44100hz.m4a",
            "gs-16b-1c-44100hz.mp3",
            "gs-16b-1c-44100hz.ogg",
            "gs-16b-1c-44100hz.ogx",
            "gs-16b-1c-44100hz.wav",
            "gs-16b-1c-44100hz.wma",
        ],
    )
    def test_audio_from_filepath_mono(self, filename: str) -> None:
        """
        Test `Audio.from_file` method on mono data.
        """
        filepath = self.data_folder / "mono" / filename
        assert filepath.is_file()
        _ = Audio.from_file(str(filepath))
        _ = Audio.from_file(filepath)

    @pytest.mark.parametrize(
        "filename",
        [
            "gs-16b-2c-44100hz.aac",
            "gs-16b-2c-44100hz.ac3",
            "gs-16b-2c-44100hz.aiff",
            "gs-16b-2c-44100hz.flac",
            "gs-16b-2c-44100hz.m4a",
            "gs-16b-2c-44100hz.mp3",
            "gs-16b-2c-44100hz.mp4",
            "gs-16b-2c-44100hz.ogg",
            "gs-16b-2c-44100hz.ogx",
            "gs-16b-2c-44100hz.wav",
            "gs-16b-2c-44100hz.wma",
        ],
    )
    def test_audio_from_filepath_stereo(self, filename: str) -> None:
        """
        Test `Audio.from_file` method on stereo data.
        """
        filepath = self.data_folder / "stereo" / filename
        assert filepath.is_file()
        _ = Audio.from_file(str(filepath))
        _ = Audio.from_file(filepath)

    @pytest.mark.parametrize(
        "filename",
        [
            "gs-16b-2c-44100hz.aac",
            "gs-16b-2c-44100hz.ac3",
            "gs-16b-2c-44100hz.aiff",
            "gs-16b-2c-44100hz.flac",
            "gs-16b-2c-44100hz.m4a",
            "gs-16b-2c-44100hz.mp3",
            "gs-16b-2c-44100hz.mp4",
            "gs-16b-2c-44100hz.ogg",
            "gs-16b-2c-44100hz.ogx",
            "gs-16b-2c-44100hz.wav",
            "gs-16b-2c-44100hz.wma",
        ],
    )
    def test_audio_from_file(self, filename: str) -> None:
        """
        Test reading audio from a file descriptor.
        """
        filepath = self.data_folder / "stereo" / filename
        assert filepath.is_file()
        with filepath.open("rb") as file:
            _ = Audio.from_file(file)

    @pytest.mark.parametrize(
        "filename",
        [
            "gs-16b-2c-44100hz.aac",
            "gs-16b-2c-44100hz.ac3",
            "gs-16b-2c-44100hz.aiff",
            "gs-16b-2c-44100hz.flac",
            "gs-16b-2c-44100hz.m4a",
            "gs-16b-2c-44100hz.mp3",
            "gs-16b-2c-44100hz.mp4",
            "gs-16b-2c-44100hz.ogg",
            "gs-16b-2c-44100hz.ogx",
            "gs-16b-2c-44100hz.wav",
            "gs-16b-2c-44100hz.wma",
        ],
    )
    def test_audio_from_io(self, filename: str) -> None:
        """
        Test reading audio from an IO object.
        """
        filepath = self.data_folder / "stereo" / filename
        assert filepath.is_file()
        with filepath.open("rb") as file:
            blob = file.read()
            buffer = io.BytesIO(blob)
            _ = Audio.from_file(buffer)

    @pytest.mark.parametrize(
        "filename",
        [
            "gs-16b-2c-44100hz.aac",
            "gs-16b-2c-44100hz.ac3",
            "gs-16b-2c-44100hz.aiff",
            "gs-16b-2c-44100hz.flac",
            "gs-16b-2c-44100hz.m4a",
            "gs-16b-2c-44100hz.mp3",
            "gs-16b-2c-44100hz.mp4",
            "gs-16b-2c-44100hz.ogg",
            "gs-16b-2c-44100hz.ogx",
            "gs-16b-2c-44100hz.wav",
            "gs-16b-2c-44100hz.wma",
        ],
    )
    def test_audio_from_bytes(self, filename: str) -> None:
        """
        Test reading audio from bytes.
        """
        filepath = self.data_folder / "stereo" / filename
        assert filepath.is_file()
        with filepath.open("rb") as file:
            blob = file.read()
            _ = Audio.from_bytes(blob)

    @pytest.mark.parametrize(
        "filename",
        [
            "gs-16b-2c-44100hz.aac",
            "gs-16b-2c-44100hz.ac3",
            "gs-16b-2c-44100hz.aiff",
            "gs-16b-2c-44100hz.flac",
            "gs-16b-2c-44100hz.mp3",
            "gs-16b-2c-44100hz.ogg",
            "gs-16b-2c-44100hz.ogx",
            "gs-16b-2c-44100hz.ts",
            "gs-16b-2c-44100hz.wav",
            "gs-16b-2c-44100hz.wma",
        ],
    )
    def test_audio_from_url(self, filename: str) -> None:
        """
        Test reading audio from a URL.
        """
        url = urljoin(BASE_URL, filename)
        _ = Audio.from_file(url)


class TestVideo:
    """
    Test `renumics.spotlight.Mesh` class.
    """

    data_folder = Path("data/videos")

    @pytest.mark.parametrize(
        "filename",
        [
            "sea-360p.avi",
            "sea-360p.mkv",
            "sea-360p.mov",
            "sea-360p.mp4",
            "sea-360p.mpg",
            "sea-360p.ogg",
            "sea-360p.webm",
            "sea-360p.wmv",
            "sea-360p-10s.mp4",
        ],
    )
    def test_video_from_filepath(self, filename: str) -> None:
        """
        Test reading video from an existing file.
        """
        filepath = self.data_folder / filename
        assert filepath.is_file()
        _ = Video.from_file(str(filepath))
        _ = Video.from_file(filepath)

    @pytest.mark.parametrize(
        "filename",
        [
            "sea-360p.avi",
            "sea-360p.mkv",
            "sea-360p.mov",
            "sea-360p.mp4",
            "sea-360p.mpg",
            "sea-360p.ogg",
            "sea-360p.webm",
            "sea-360p.wmv",
            "sea-360p-10s.mp4",
        ],
    )
    def test_video_from_bytes(self, filename: str) -> None:
        """
        Test reading video from bytes.
        """
        filepath = self.data_folder / filename
        assert filepath.is_file()
        with filepath.open("rb") as file:
            blob = file.read()
            _ = Video.from_bytes(blob)

    @pytest.mark.parametrize(
        "filename",
        [
            "sea-360p.avi",
            "sea-360p.mkv",
            "sea-360p.mov",
            "sea-360p.mp4",
            "sea-360p.mpg",
            "sea-360p.ogg",
            "sea-360p.webm",
            "sea-360p.wmv",
            "sea-360p-10s.mp4",
        ],
    )
    def test_video_from_url(self, filename: str) -> None:
        """
        Test reading video from an URL.
        """
        url = urljoin(BASE_URL, filename)
        _ = Video.from_file(url)
