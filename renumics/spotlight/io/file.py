"""
File-related IO.
"""

import contextlib
import io
import os
from typing import IO, Iterator

import requests
import validators

from renumics.spotlight.media import exceptions
from renumics.spotlight.requests import headers
from renumics.spotlight.typing import FileType


@contextlib.contextmanager
def as_file(filepath: FileType) -> Iterator[IO]:
    """
    If a path is given, open the given file.
    If an URL is given, download and open the given file.
    If an IO object is given, pass as is.
    """
    if isinstance(filepath, (str, os.PathLike)):
        str_filepath = str(filepath)
        if validators.url(str_filepath):
            response = requests.get(str_filepath, headers=headers, timeout=30)
            if not response.ok:
                raise exceptions.InvalidFile(f"URL {str_filepath} does not exist.")
            with io.BytesIO(response.content) as file:
                yield file
        elif os.path.isfile(str_filepath):
            with open(filepath, "rb") as file:
                yield file
        else:
            raise exceptions.InvalidFile(
                f"File {str_filepath} is neither an existing file nor an existing URL."
            )
    else:
        yield filepath
