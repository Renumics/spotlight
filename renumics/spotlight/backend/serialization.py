from typing import Any, cast

import numpy as np
import pandas as pd

from renumics.spotlight.typing import is_iterable


def _sanitize_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if isinstance(value, (bool, int, float, str, bytes)):
        return value
    try:
        # Assume `value` is a `numpy` object.
        return value.tolist()
    except AttributeError:
        # Try to send `value` as is.
        return value


def sanitize_values(values: Any) -> Any:
    """
    sanitize values for serialization
    e.g. replace inf, -inf and NaN in float data
    """

    if not is_iterable(values):
        return _sanitize_value(values)
    if isinstance(values, list):
        return [sanitize_values(x) for x in values]
    # At the moment, `values` should be a `numpy` array.
    values = cast(np.ndarray, values)
    if issubclass(values.dtype.type, np.inexact):
        return np.where(np.isfinite(values), values, np.array(None)).tolist()
    return values.tolist()
