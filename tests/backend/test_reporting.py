"""
test reporting module
"""
from renumics.spotlight.reporting import skip_analytics
from renumics.spotlight.settings import settings


def test_opt_out(monkeypatch) -> None:
    """test opt_out is true"""

    monkeypatch.delenv("CI", raising=False)
    settings.opt_out = True
    assert skip_analytics() is True


def test_opt_in(monkeypatch):
    """
    test opt_in is true opt_out also
    as opt_in is False by default
    dont opt_out
    """

    monkeypatch.delenv("CI", raising=False)
    settings.opt_out = True
    settings.opt_in = True
    assert skip_analytics() is False


def test_opt_in_and_opt_out(monkeypatch):
    """if opt_out is true and opt_in is false
    skip analytics"""

    monkeypatch.delenv("CI", raising=False)
    settings.opt_out = True
    settings.opt_in = False
    assert skip_analytics() is True


def test_opt_in_and_ci(monkeypatch):
    """when ci is true always skip analytics"""

    settings.opt_out = False
    settings.opt_in = True
    monkeypatch.setenv("CI", "True")
    assert skip_analytics() is True
