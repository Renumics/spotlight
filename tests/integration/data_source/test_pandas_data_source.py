import numpy as np
import pandas as pd
import pytest

from renumics.spotlight_plugins.core.pandas_data_source import PandasDataSource


@pytest.mark.parametrize(
    "df",
    [
        pd.DataFrame(
            {
                "bool": pd.Series([True, False, None, None, pd.NA]),
                "int": pd.Series([0, 1, None, None, pd.NA]),
                "float": pd.Series(
                    [0.0, float("inf"), float("nan"), None, None, pd.NA]
                ),
                "str": pd.Series(["foo", "foo bar", None, pd.NA]),
                "dt": pd.Series([pd.Timestamp(2000, 7, 15), pd.NaT, None, None, pd.NA]),
                "object": pd.Series([[0, 1], [2, 3], None, None, pd.NA]),
            }
        ),
        pd.DataFrame(
            np.random.random((4, 4)),
            index=pd.MultiIndex.from_product([[1, 2], ["foo", "bar"]]),
            columns=pd.MultiIndex.from_product([[3, 4], ["baz", "foobar"]]),
        ),
        pd.DataFrame(
            np.random.random((4, 4)),
            index=pd.MultiIndex.from_product([[1, 2], ["foo", "foo"]]),
            columns=pd.MultiIndex.from_product([[3, 3], ["baz", "foobar"]]),
        ),
    ],
    ids=["df", "multiindex-df", "duplicated-multiindex-df"],
)
def test_pandas_data_source(df: pd.DataFrame) -> None:
    data_source = PandasDataSource(df)
    assert len(data_source) == len(df)
    column_names = data_source.column_names
    assert len(column_names) == len(df.columns)

    for column_name in column_names:
        _metadata = data_source.get_column_metadata(column_name)
        _values = data_source.get_column_values(column_name)
