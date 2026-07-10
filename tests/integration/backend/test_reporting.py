"""
test reporting module
"""

import pytest

from renumics.spotlight import reporting
from renumics.spotlight.reporting import skip_analytics
from renumics.spotlight.settings import settings


@pytest.fixture(autouse=True)
def _configure_analytics_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """configure an analytics URL and reset opt_in/opt_out to defaults"""

    monkeypatch.setattr(reporting, "ANALYTICS_URL", "https://example.com/spotlight")
    monkeypatch.setattr(settings, "opt_in", False)
    monkeypatch.setattr(settings, "opt_out", False)


def test_no_analytics_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """skip analytics when no analytics URL is configured"""

    monkeypatch.delenv("CI", raising=False)
    monkeypatch.setattr(reporting, "ANALYTICS_URL", None)
    settings.opt_out = False
    settings.opt_in = True
    assert skip_analytics() is True


def test_opt_out(monkeypatch: pytest.MonkeyPatch) -> None:
    """test opt_out is true"""

    monkeypatch.delenv("CI", raising=False)
    settings.opt_out = True
    assert skip_analytics() is True


def test_opt_in(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    test opt_in is true opt_out also
    as opt_in is False by default
    dont opt_out
    """

    monkeypatch.delenv("CI", raising=False)
    settings.opt_out = True
    settings.opt_in = True
    assert skip_analytics() is False


def test_opt_in_and_opt_out(monkeypatch: pytest.MonkeyPatch) -> None:
    """if opt_out is true and opt_in is false
    skip analytics"""

    monkeypatch.delenv("CI", raising=False)
    settings.opt_out = True
    settings.opt_in = False
    assert skip_analytics() is True


def test_opt_in_and_ci(monkeypatch: pytest.MonkeyPatch) -> None:
    """when ci is true always skip analytics"""

    settings.opt_out = False
    settings.opt_in = True
    monkeypatch.setenv("CI", "True")
    assert skip_analytics() is True
