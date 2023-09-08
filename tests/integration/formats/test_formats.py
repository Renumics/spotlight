"""
Test various supported data formats
"""
from pathlib import Path
import pytest
from renumics import spotlight


@pytest.mark.parametrize("extension", ["csv", "feather", "parquet", "orc"])
def test_successful_load(extension: str, project_root: Path) -> None:
    """
    Check if the file loads without error when calling spotlight.show
    """
    source = project_root / "data" / extension / f"multimodal-random-small.{extension}"
    viewer = spotlight.show(source, wait=False, no_browser=True)
    viewer.close()
