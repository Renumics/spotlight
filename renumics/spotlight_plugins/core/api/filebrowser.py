"""
filebrowser api endpoints
"""

from pathlib import Path
from typing import Literal, TypeAlias

from fastapi import APIRouter, Request
from pydantic import BaseModel

from renumics.spotlight.backend.exceptions import (
    FilebrowsingNotAllowed,
    InvalidPath,
)
from renumics.spotlight.io.path import is_path_relative_to

router = APIRouter()

FileType: TypeAlias = Literal["file", "folder"]


class FileEntry(BaseModel):
    """
    A file entry
    """

    name: str
    path: str
    type: FileType
    size: int


class Folder(BaseModel):
    """
    A single folder
    """

    name: str
    path: str
    parent: str | None
    files: list[FileEntry]


@router.get(
    "/{path:path}",
    tags=["filebrowser"],
    summary="File Browser API",
    operation_id="get_folder",
)
def get_folder(path: str, request: Request) -> Folder:
    """
    fetch a folder
    """

    if not request.app.filebrowsing_allowed:
        raise FilebrowsingNotAllowed()

    project_root = Path(request.app.project_root).resolve()
    full_path = (project_root / path).resolve()

    # assert that the path is inside our project root
    if not is_path_relative_to(full_path, project_root):
        raise InvalidPath(path)

    relative_path = full_path.relative_to(project_root)

    name = full_path.name
    files = [
        {
            "name": f.name,
            "path": str(f.relative_to(project_root)),
            "type": "file" if f.is_file() else "folder",
            "size": f.stat().st_size if f.is_file() else 0,
        }
        for f in full_path.iterdir()
    ]

    parent = (
        str(relative_path.parent) if relative_path.parent != relative_path else None
    )

    return Folder(name=name, path=str(relative_path), parent=parent, files=files)
