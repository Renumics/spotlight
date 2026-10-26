"""
filebrowser api endpoints
"""

from pathlib import Path
from typing import Literal, TypeAlias

from fastapi import APIRouter, Request
from pydantic import BaseModel

from renumics.spotlight.backend.exceptions import (
    FilebrowsingNotAllowed,
)

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
async def get_folder(path: str, request: Request) -> Folder:
    """
    fetch a folder
    """

    if not request.app.filebrowsing_allowed:
        raise FilebrowsingNotAllowed()

    full_path = Path(request.app.project_root) / path
    relative_path = full_path.relative_to(request.app.project_root)

    name = full_path.name
    files = [
        {
            "name": f.name,
            "path": str(f.relative_to(request.app.project_root)),
            "type": "file" if f.is_file() else "folder",
            "size": f.stat().st_size if f.is_file() else 0,
        }
        for f in full_path.iterdir()
    ]

    parent = (
        str(relative_path.parent) if relative_path.parent != relative_path else None
    )

    return Folder(name=name, path=str(relative_path), parent=parent, files=files)
