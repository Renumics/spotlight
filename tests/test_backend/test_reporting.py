"""
test reporting module
"""
from renumics.spotlight.reporting import skip_analytics
from renumics.spotlight.settings import settings


def test_opt_out() -> None:
    """test opt_out is true"""

    settings.opt_out = True
    assert skip_analytics() is True


def test_opt_in():
    """
    test opt_in is true opt_out also
    as opt_in is False by default
    dont opt_out
    """

    settings.opt_out = True
    settings.opt_in = True
    assert skip_analytics() is False


def test_opt_in_and_opt_out():
    """if opt_out is true and opt_in is false
    skip analytics"""

    settings.opt_out = True
    settings.opt_in = False
    assert skip_analytics() is True


def test_opt_in_and_ci(monkeypatch):
    """when ci is true always skip analytics"""

    settings.opt_out = False
    settings.opt_in = True
    monkeypatch.setenv("CI", "true")
    assert skip_analytics() is True
