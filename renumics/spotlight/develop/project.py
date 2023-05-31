"""
Functionality for (plugin) development
"""

from pathlib import Path
from typing import Optional
import subprocess
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
    venv: Optional[Path]


def get_project_info() -> ProjectInfo:
    """
    Determine location for dev mode

    "core": Inside the main spotlight project.
    "plugin": Inside a spotlight plugin project.
    None: neither.
    """

    pyproject_toml = _find_upwards("pyproject.toml", Path.cwd())
    if not pyproject_toml:
        return ProjectInfo(name="", type=None, root=None, venv=None)

    pyproject_content = toml.load(pyproject_toml)

    project_name = pyproject_content["tool"]["poetry"]["name"]

    if project_name == "renumics-spotlight":
        project_type = "core"
    else:
        project_type = "plugin"

    # for now, assume that every dev uses poetry for venv management
    poetry_env = Path(
        subprocess.run(
            ["poetry", "env", "info", "--path"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    )
    venv = poetry_env if poetry_env.exists() else None

    return ProjectInfo(
        name=project_name, type=project_type, root=pyproject_toml.parent, venv=venv
    )


def find_spotlight_repository() -> Optional[Path]:
    """
    Find the cloned spotlight repository.
    Returns the path to the repo or None, if it could not be located.
    """
    project = get_project_info()

    if project.type == "core":
        # already in the spotlight repo!
        return project.root

    if project.type == "plugin" and project.venv:
        # find .pth file of the editable install, read it and return repo path
        try:
            pth = next(project.venv.glob("**/renumics_spotlight.pth"))
            return Path(pth.read_text().strip())
        except StopIteration:
            return None

    return None
