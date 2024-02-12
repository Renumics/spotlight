import pandas as pd

from renumics import spotlight


def test_read_df() -> None:
    df = pd.DataFrame({"foo": range(4)})
    viewer = spotlight.show(df, wait=False, no_browser=True)
    df_after_close = viewer.df
    viewer.close()
    assert df_after_close is not None
    assert "foo" in df_after_close


def test_read_df_after_close() -> None:
    df = pd.DataFrame({"foo": range(4)})
    viewer = spotlight.show(df, wait=False, no_browser=True)
    viewer.close()
    df_after_close = viewer.df
    assert df_after_close is not None
    assert "foo" in df_after_close
