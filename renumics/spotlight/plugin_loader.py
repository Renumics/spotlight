"""
    Facilities for plugin loading and registration.
"""

import importlib
import pkgutil
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, List, Optional

from fastapi import FastAPI

import renumics.spotlight_plugins as plugins_namespace
from renumics.spotlight.app_config import AppConfig
from renumics.spotlight.develop.project import get_project_info
from renumics.spotlight.io.path import is_path_relative_to
from renumics.spotlight.settings import settings


@dataclass
class Plugin:
    """
    Information about an installed and loaded Spotlight Plugin
    """

    name: str
    priority: int
    module: ModuleType
    init: Callable[[], None]
    activate: Callable[[FastAPI], None]
    update: Callable[[FastAPI, AppConfig], None]
    dev: bool
    frontend_entrypoint: Optional[Path]


_plugins: Optional[List[Plugin]] = None


def load_plugins() -> List[Plugin]:
    """
    Automatically load, register and initialize plugins
    inside the renumics.spotlight.plugins namespace package.
    """

    global _plugins

    if _plugins is not None:
        return _plugins

    def noop(*_args: Any, **_kwargs: Any) -> None:
        """
        noop impl for plugin hooks
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
            init=getattr(module, "__register__", noop),
            activate=getattr(module, "__activate__", noop),
            update=getattr(module, "__update__", noop),
            module=module,
            dev=dev,
            frontend_entrypoint=main_js if main_js.exists() else None,
        )

    _plugins = sorted(plugins.values(), key=lambda p: p.priority)
    for plugin in _plugins:
        plugin.init()

    return _plugins
