"""
Test `renumics.spotlight.media.Mesh` class.
"""
import numpy as np
import pytest

from renumics.spotlight.media import Mesh

from .data import MESHES_FOLDER
from ...integration.helpers import approx


@pytest.mark.parametrize("num_points", [10, 100, 10000])
@pytest.mark.parametrize("num_triangles", [10, 100, 10000])
def test_mesh_from_array(num_points: int, num_triangles: int) -> None:
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
            "int64_1": np.random.randint(-10000, 10000, (num_triangles, 1), "int64"),
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
def test_mesh_from_filepath(filename: str) -> None:
    """
    Test reading mesh from an existing file.
    """
    filepath = MESHES_FOLDER / filename
    assert filepath.is_file()
    _ = Mesh.from_file(str(filepath))
    _ = Mesh.from_file(filepath)
