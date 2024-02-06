from pathlib import Path

import pytest


@pytest.fixture
def project_root() -> Path:
    return Path(__file__).parent.parent
