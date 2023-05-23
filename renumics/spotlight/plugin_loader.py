"""
    Facilities for plugin loading and registration.
"""

import importlib
import pkgutil
from dataclasses import dataclass
from types import ModuleType
from pathlib import Path
from typing import Callable, List, Optional

from renumics.spotlight.backend.types import SpotlightApp
from renumics.spotlight.settings import settings
from renumics.spotlight.develop.project import get_project_info
from renumics.spotlight.io.path import is_path_relative_to

import renumics.spotlight_plugins as plugins_namespace


@dataclass
class Plugin:
    """
    Information about an installed and loaded Spotlight Plugin
    """

    name: str
    priority: int
    module: ModuleType
    init: Callable[[], None]
    activate: Callable[[SpotlightApp], None]
    dev: bool
    frontend_entrypoint: Optional[Path]


# pylint: disable=global-statement
_plugins: Optional[List[Plugin]] = None


def load_plugins() -> List[Plugin]:
    """
    Automatically load, register and initialize plugins
    inside the renumics.spotlight.plugins namespace package.
    """

    global _plugins

    if _plugins is not None:
        return _plugins

    def noinit() -> None:
        """
        noop impl for __init__
        """

    def noactivate(_: SpotlightApp) -> None:
        """
        noop impl for __activate__
        """

    plugins = {}
    for _, name, _ in pkgutil.iter_modules(plugins_namespace.__path__):
        module = importlib.import_module(plugins_namespace.__name__ + "." + name)

        project = get_project_info()

        dev = bool(
            settings.dev
            and project.root
            and is_path_relative_to(module.__path__[0], project.root)
        )

        main_js = Path(module.__path__[0]) / "frontend" / "main.js"

        plugins[name] = Plugin(
            name=name,
            priority=getattr(module, "__priority__", 1000),
            init=getattr(module, "__register__", noinit),
            activate=getattr(module, "__activate__", noactivate),
            module=module,
            dev=dev,
            frontend_entrypoint=main_js if main_js.exists() else None,
        )

    _plugins = sorted(plugins.values(), key=lambda p: p.priority)
    for plugin in _plugins:
        plugin.init()

    return _plugins
