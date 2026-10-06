"""
Test caching of UMAP results.
"""

import sys
from pathlib import Path
from types import ModuleType
from typing import Any, List, Tuple, cast

import numpy as np
import pytest

from renumics import spotlight
from renumics.spotlight import appdirs
from renumics.spotlight.backend.tasks import reduction
from renumics.spotlight.cache import Cache
from renumics.spotlight.data_store import DataStore

INDICES = list(range(20))


class FakeUMAP:
    """
    Stands in for `umap.UMAP`, counts the fits and gives a different result every time.
    """

    fits: List[Tuple[int, str, float]] = []

    def __init__(
        self, n_neighbors: int, metric: str, min_dist: float, random_state: int
    ) -> None:
        self.parameters = (n_neighbors, metric, min_dist)

    def fit_transform(self, data: np.ndarray) -> np.ndarray:
        """Remember the call, return the first two columns shifted by the number of fits"""
        self.fits.append(self.parameters)
        return data[:, :2] + len(self.fits)


@pytest.fixture(autouse=True)
def isolated_umap_cache(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Use an empty cache directory and a fake UMAP"""
    monkeypatch.setattr(appdirs, "cache_dir", tmp_path)
    monkeypatch.setattr(reduction, "reduction_cache", Cache("reduction"))
    fake_umap = ModuleType("umap")
    fake_umap.UMAP = FakeUMAP  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "umap", fake_umap)
    FakeUMAP.fits = []


def use_data(
    monkeypatch: pytest.MonkeyPatch, data: np.ndarray, indices: List[int]
) -> None:
    """Make the data of the table what `align_data` returns"""
    monkeypatch.setattr(reduction, "align_data", lambda *_args: (data.copy(), indices))


def compute(
    n_neighbors: int = 15, metric: str = "euclidean", min_dist: float = 0.1
) -> Tuple[np.ndarray, List[int]]:
    """Compute UMAP with the data store not used by the fake `align_data`"""
    return reduction.compute_umap(
        cast(DataStore, None), ["a", "b", "c"], INDICES, n_neighbors, metric, min_dist
    )


@pytest.fixture
def data() -> np.ndarray:
    """A table of 20 rows with 3 columns"""
    return np.random.default_rng(0).normal(size=(20, 3))


def test_same_input_is_computed_once(
    monkeypatch: pytest.MonkeyPatch, data: np.ndarray
) -> None:
    """
    Test the second request for the same input gives the stored result, also with a new cache object.
    """
    use_data(monkeypatch, data, INDICES)
    first, first_indices = compute()
    assert len(FakeUMAP.fits) == 1

    second, second_indices = compute()
    assert len(FakeUMAP.fits) == 1
    np.testing.assert_array_equal(second, first)
    assert second_indices == first_indices == INDICES

    # a restart of the app: the result is read from disk
    monkeypatch.setattr(reduction, "reduction_cache", Cache("reduction"))
    third, _ = compute()
    assert len(FakeUMAP.fits) == 1
    np.testing.assert_array_equal(third, first)


@pytest.mark.parametrize(
    "parameters",
    [
        {"n_neighbors": 5},
        {"metric": "cosine"},
        {"min_dist": 0.5},
    ],
)
def test_other_parameters_are_computed_again(
    monkeypatch: pytest.MonkeyPatch, data: np.ndarray, parameters: Any
) -> None:
    """
    Test a change of a parameter of UMAP is a miss.
    """
    use_data(monkeypatch, data, INDICES)
    first, _ = compute()
    second, _ = compute(**parameters)
    assert len(FakeUMAP.fits) == 2
    assert not np.array_equal(first, second)


def test_other_data_is_computed_again(
    monkeypatch: pytest.MonkeyPatch, data: np.ndarray
) -> None:
    """
    Test changed values, other rows with the same values and other shape are misses.
    """
    use_data(monkeypatch, data, INDICES)
    compute()
    assert len(FakeUMAP.fits) == 1

    changed = data.copy()
    changed[7, 1] += 1e-9
    use_data(monkeypatch, changed, INDICES)
    compute()
    assert len(FakeUMAP.fits) == 2

    use_data(monkeypatch, data, list(range(1, 21)))
    _, indices = compute()
    assert len(FakeUMAP.fits) == 3
    assert indices == list(range(1, 21))

    use_data(monkeypatch, data[:, :3].reshape(30, 2), INDICES + list(range(20, 30)))
    reduction.compute_umap(cast(DataStore, None), ["a"], INDICES, 15, "euclidean", 0.1)
    assert len(FakeUMAP.fits) == 3  # two columns are shown as they are, not by UMAP


def test_data_of_another_type_is_computed_again(
    monkeypatch: pytest.MonkeyPatch, data: np.ndarray
) -> None:
    """
    Test data is hashed as it is (embeddings of 32 bits are not copied to 64 bits for the
    key): the same data of 32 bits is found again, and is not the data of 64 bits.
    """
    data32 = data.astype(np.float32)
    use_data(monkeypatch, data32, INDICES)
    compute()
    compute()
    assert len(FakeUMAP.fits) == 1

    use_data(monkeypatch, data32.astype(np.float64), INDICES)
    compute()
    assert len(FakeUMAP.fits) == 2


def test_scaled_metrics_use_the_scaled_data(
    monkeypatch: pytest.MonkeyPatch, data: np.ndarray
) -> None:
    """
    Test the cache key is made from the scaled data: scaled by standardization or not.
    """
    use_data(monkeypatch, data, INDICES)
    compute(metric="euclidean")
    compute(metric="standardized euclidean")
    compute(metric="robust euclidean")
    assert len(FakeUMAP.fits) == 3
    compute(metric="standardized euclidean")
    compute(metric="robust euclidean")
    assert len(FakeUMAP.fits) == 3


def test_clear_caches_clears_the_results(
    monkeypatch: pytest.MonkeyPatch, data: np.ndarray
) -> None:
    """
    Test clearing all caches removes stored UMAP results.
    """
    use_data(monkeypatch, data, INDICES)
    compute()
    compute()
    assert len(FakeUMAP.fits) == 1

    spotlight.clear_caches()
    compute()
    assert len(FakeUMAP.fits) == 2
