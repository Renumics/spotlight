"""
Layout API endpoints
"""

from typing import Dict

from fastapi import APIRouter, Request
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from renumics.spotlight.layout.default import DEFAULT_LAYOUT


router = APIRouter()

CURRENT_LAYOUT_KEY = "layout.current"


@router.get("/", tags=["layout"], response_model=Dict, operation_id="get_layout")
async def get_layout(request: Request) -> Dict:
    """
    Get layout.
    """
    dataset_uid = request.app.data_source.get_uid()
    layout = await request.app.config.get(CURRENT_LAYOUT_KEY, dataset=dataset_uid)
    if layout is None:
        layout = (request.app.layout or DEFAULT_LAYOUT).dict(by_alias=True)
        await request.app.config.set(CURRENT_LAYOUT_KEY, layout, dataset=dataset_uid)
    return layout


@router.put(
    "/reset",
    tags=["layout"],
    response_model=Dict,
    operation_id="reset_layout",
)
async def reset_layout(request: Request) -> Dict:
    """
    Get layout.
    """
    layout = request.app.layout or DEFAULT_LAYOUT
    dataset_uid = request.app.data_source.get_uid()
    await request.app.config.set(
        CURRENT_LAYOUT_KEY, layout.dict(by_alias=True), dataset=dataset_uid
    )
    return layout.dict(by_alias=True)


class SetLayoutRequest(BaseModel):
    """
    Set layout request model.
    """

    # pylint: disable=too-few-public-methods

    layout: Dict


@router.put("/", tags=["layout"], response_model=Dict, operation_id="set_layout")
async def set_layout(set_layout_request: SetLayoutRequest, request: Request) -> Dict:
    """
    Get layout.
    """
    dataset_uid = request.app.data_source.get_uid()
    await request.app.config.set(
        CURRENT_LAYOUT_KEY, set_layout_request.layout, dataset=dataset_uid
    )
    return set_layout_request.layout
