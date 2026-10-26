"""
Config API endpoints
"""

from typing import Annotated

from fastapi import APIRouter, Cookie, Request
from pydantic import BaseModel

from renumics.spotlight.backend.config import ConfigValue

router = APIRouter(tags=["config"])


@router.get("/{name}", operation_id="get_value")
async def get_value(
    request: Request,
    name: str,
    browser_id: Annotated[str | None, Cookie()] = None,
) -> ConfigValue | None:
    """
    get config value by name
    """
    return await request.app.config.get(name, user=browser_id)


class SetConfigRequest(BaseModel):
    """
    Set config request model.
    """

    value: ConfigValue | None


@router.put("/{name}", operation_id="set_value")
async def set_value(
    name: str,
    set_config_request: SetConfigRequest,
    request: Request,
    browser_id: Annotated[str | None, Cookie()] = None,
) -> None:
    """
    Set config value by name.
    """
    await request.app.config.set(name, set_config_request.value, user=browser_id)


@router.delete("/{name}", operation_id="remove")
async def remove_value(
    name: str,
    request: Request,
    browser_id: Annotated[str | None, Cookie()] = None,
) -> None:
    """
    Remove config value by name.
    """
    await request.app.config.remove(name, user=browser_id)
