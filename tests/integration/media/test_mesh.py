"""
Test `renumics.spotlight.media.Mesh` class.
"""
from urllib.parse import urljoin

import pytest

from renumics.spotlight.media import Mesh

from .data import BASE_URL


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
def test_mesh_from_url(filename: str) -> None:
    """
    Test reading mesh from a URL.
    """
    url = urljoin(BASE_URL, filename)
    _ = Mesh.from_file(url)
