"""
Config API endpoints
"""

from typing import Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from renumics.spotlight.backend.config import ConfigValue


router = APIRouter(tags=["config"])


@router.get("/{name}", response_model=Optional[ConfigValue], operation_id="get")
async def get_value(name: str, request: Request) -> Optional[ConfigValue]:
    """
    get config value by name
    """
    return await request.app.config.get(name)


class SetConfigRequest(BaseModel):
    """
    Set config request model.
    """

    # pylint: disable=too-few-public-methods

    value: Optional[ConfigValue]


@router.put("/{name}", operation_id="set")
async def set_value(
    name: str, set_config_request: SetConfigRequest, request: Request
) -> None:
    """
    Set config value by name.
    """
    await request.app.config.set(name, set_config_request.value)


@router.delete("/{name}", operation_id="remove")
async def remove_value(name: str, request: Request) -> None:
    """
    Remove config value by name.
    """
    await request.app.config.remove(name)
