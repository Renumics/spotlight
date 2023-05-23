"""
    filebrowser api endpoints
"""

from pathlib import Path
from typing import Optional, List
from typing_extensions import Literal
from fastapi import APIRouter, Request
from pydantic import BaseModel  # pylint: disable=no-name-in-module

router = APIRouter()

FileType = Literal["file", "folder"]


# pylint: disable=too-few-public-methods
class FileEntry(BaseModel):
    """
    A file entry
    """

    name: str
    path: str
    type: FileType
    size: int


# pylint: disable=too-few-public-methods
class Folder(BaseModel):
    """
    A single folder
    """

    name: str
    path: str
    parent: Optional[str]
    files: List[FileEntry]


@router.get(
    "/{path:path}",
    tags=["filebrowser"],
    summary="File Browser APi",
    response_model=Folder,
    operation_id="get_folder",
)
async def get_folder(path: str, request: Request) -> Folder:
    """
    fetch a folder
    """

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
