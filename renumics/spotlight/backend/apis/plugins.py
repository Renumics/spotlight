"""
Spotlight Plugin API
"""

from typing import List, Optional

from fastapi import APIRouter, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel

from renumics.spotlight.backend.exceptions import Problem
from renumics.spotlight.plugin_loader import load_plugins

router = APIRouter(tags=["plugins"])


class Plugin(BaseModel):
    """
    Frontend representation of a spotlight plugin
    """

    name: str
    priority: int
    dev: bool
    entrypoint: Optional[str]


@router.get("/", response_model=List[Plugin], operation_id="get_plugins")
async def _() -> List[Plugin]:
    """
    Get a list of all the installed spotlight plugins
    """

    plugins = load_plugins()
    return [
        Plugin(
            name=p.name,
            priority=p.priority,
            dev=p.dev,
            entrypoint=(
                f"../api/plugins/{p.name}/main.js" if p.frontend_entrypoint else None
            ),
        )
        for p in plugins
    ]


@router.get("/{name:str}/main.js", operation_id="get_entrypoint")
async def _(name: str) -> Response:
    """
    Get the frontend entrypoint for a plugin
    """

    plugins = load_plugins()
    plugin = next((p for p in plugins if p.name == name), None)

    if not plugin:
        raise Problem(
            title="Plugin not found", detail=f"Can't find plugin with name: {name}."
        )

    if plugin.frontend_entrypoint is None:
        return Response("export default {}", media_type="text/javascript")

    return FileResponse(plugin.frontend_entrypoint, media_type="text/javascript")
