"""
Helpers for HuggingFace formats.
"""

from typing import Any, Dict


def prepare_hugging_face_dict(x: Dict) -> Any:
    """
    Prepare HuggingFace format for files to be used in Spotlight.
    """
    if x.keys() != {"bytes", "path"}:
        return x
    blob = x["bytes"]
    if blob is not None:
        return blob
    return x["path"]
