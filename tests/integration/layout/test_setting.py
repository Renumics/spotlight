"""
test that layout can be set via environment
"""

import httpx
import pandas as pd
from pytest import MonkeyPatch

from renumics import spotlight
from renumics.spotlight import layout, settings


def test_settings_layout_is_used(monkeypatch: MonkeyPatch) -> None:
    """
    Test if the layout set via env var is actually used in the frontend.
    """
    # set settings layout
    env_layout = layout.parse([layout.table(name="env_layout_table")]).json(
        by_alias=True
    )
    monkeypatch.setattr(settings, "layout", env_layout)

    print(settings.layout)

    # launch spotlight without layout parameter
    viewer = spotlight.show(pd.DataFrame({"a": [0]}), wait=False, no_browser=True)

    # check if layout is used
    app_layout = httpx.get(f"{viewer.url}api/layout", follow_redirects=True).text
    print(app_layout)
    assert "env_layout_table" in app_layout


def test_layout_from_params_has_priority(monkeypatch: MonkeyPatch) -> None:
    """
    Test if the layout set via layout= param in spotlight.show is preferred
    over the layout set via env.
    """
    # set settings layout
    env_layout = layout.parse([layout.table(name="env_layout_table")]).json(
        by_alias=True
    )
    monkeypatch.setattr(settings, "layout", env_layout)

    # launch spotlight with another layout parameter
    param_layout = layout.parse([layout.table(name="param_layout_table")]).json(
        by_alias=True
    )
    viewer = spotlight.show(
        pd.DataFrame({"a": [0]}), wait=False, layout=param_layout, no_browser=True
    )

    # check that the layout set via parameter is used
    app_layout = httpx.get(f"{viewer.url}api/layout", follow_redirects=True).text
    print(app_layout)
    assert "param_layout_table" in app_layout
