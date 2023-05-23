#!/usr/bin/env python3
"""
    Command line entrypoint for the renumics-spotlight jupyter notebook
"""
import os
import sys
import shutil
from pathlib import Path
from typing import List, Iterator, Tuple

import importlib_resources
from loguru import logger
from notebook.notebookapp import NotebookApp

from renumics.spotlight import __version__
from renumics.spotlight import appdirs
from renumics.spotlight.environ import set_temp_environ


def _iter_package_files(
    package: str, subfolder: Path = Path()
) -> Iterator[Tuple[os.PathLike, importlib_resources.abc.Traversable]]:
    folder = importlib_resources.files(package) / subfolder
    for file in folder.iterdir():
        yield subfolder / file.name, file
        if file.is_dir():
            for entry in _iter_package_files(package, subfolder / file.name):
                yield entry


def install_spotlight_theme() -> str:
    """
    install the spotlight theme to spotlight's jupyter config folder and get
    its path
    """

    jupyter_config_folder = Path(appdirs.config_dir) / "jupyter"
    jupyter_theme_folder = jupyter_config_folder / "custom"

    jupyter_theme_folder.mkdir(exist_ok=True, parents=True)

    for location, source_file in _iter_package_files(
        "renumics.spotlight.notebook.theme"
    ):
        destination_path = jupyter_theme_folder / location

        if source_file.is_dir():
            destination_path.mkdir(exist_ok=True, parents=True)
        else:
            with source_file.open("rb") as source:
                with destination_path.open("wb") as destination:
                    shutil.copyfileobj(source, destination)

    return str(jupyter_config_folder)


def launch_notebook(args: List[str]) -> None:
    """
    launch the jupyter notebook
    """
    app = NotebookApp()
    app.initialize(["-y", *args])
    app.start()


def main() -> None:
    """
    search for notebook custom folder and run notebook
    """
    args = sys.argv[1:]

    if len(args) > 0 and args[0] == "--version":
        print(f"spotlight, version {__version__}")
        return

    jupyter_config_folder = install_spotlight_theme()
    with set_temp_environ(JUPYTER_CONFIG_DIR=jupyter_config_folder):
        launch_notebook(args)

    logger.info("Exiting Spotlight Notebook.")


if __name__ == "__main__":
    main()
