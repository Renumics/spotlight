"""
Functionality for (plugin) development
"""

from pathlib import Path
from typing import Optional
import dataclasses

import toml


def _find_upwards(filename: str, folder: Path) -> Optional[Path]:
    """
    Find first matching file upwards in parent folders.
    """
    if folder == folder.parent:
        return None

    path = folder / filename
    if path.exists():
        return path

    return _find_upwards(filename, folder.parent)


@dataclasses.dataclass
class ProjectInfo:
    """
    Info about the current dev project
    """

    name: str
    type: Optional[str]
    root: Optional[Path]


def get_project_info() -> ProjectInfo:
    """
    Determine location for dev mode

    "core": Inside the main spotlight project.
    "plugin": Inside a spotlight plugin project.
    None: neither.
    """

    pyproject_toml = _find_upwards("pyproject.toml", Path.cwd())
    if not pyproject_toml:
        return ProjectInfo(name="", type=None, root=None)

    pyproject_content = toml.load(pyproject_toml)

    project_name = pyproject_content["tool"]["poetry"]["name"]

    if project_name == "renumics-spotlight":
        project_type = "core"
    else:
        project_type = "plugin"

    return ProjectInfo(name=project_name, type=project_type, root=pyproject_toml.parent)
