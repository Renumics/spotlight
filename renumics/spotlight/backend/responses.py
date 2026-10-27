"""
Responses of the API
"""

from typing import Any

import orjson
from fastapi.responses import JSONResponse


class ORJSONResponse(JSONResponse):
    """
    A JSON response serialized by `orjson`, which also serializes numpy values.

    FastAPI deprecated its own `ORJSONResponse` in favor of response models, which
    Spotlight cannot use for the values of the table (numpy arrays).
    """

    def render(self, content: Any) -> bytes:
        return orjson.dumps(
            content, option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY
        )
