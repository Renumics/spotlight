"""
Functionality for (plugin) development
"""

import dataclasses
import site
from pathlib import Path
from typing import Optional

import toml

from ..settings import settings


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

    if not settings.dev:
        return ProjectInfo(name="", type=None, root=None)

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


def find_spotlight_repository() -> Optional[Path]:
    """
    Find the cloned spotlight repository.
    Returns the path to the repo or None, if it could not be located.
    """
    project = get_project_info()

    if project.type == "core":
        # already in the spotlight repo!
        return project.root

    if project.type == "plugin":
        # find .pth file of the editable install, read it and return repo path
        for site_packages_folder in site.getsitepackages():
            try:
                pth = next(Path(site_packages_folder).glob("**/renumics_spotlight.pth"))
                return Path(pth.read_text().strip())
            except StopIteration:
                return None

    return None
