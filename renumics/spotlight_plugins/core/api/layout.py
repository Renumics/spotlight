"""
Layout API endpoints
"""

from typing import Dict, Optional, cast, Union
from typing_extensions import Annotated

from fastapi import APIRouter, Request, Cookie
from pydantic import BaseModel  # pylint: disable=no-name-in-module

from renumics.spotlight.backend.types import SpotlightApp
from renumics.spotlight.layout.default import DEFAULT_LAYOUT

router = APIRouter()

CURRENT_LAYOUT_KEY = "layout.current"


@router.get("/", tags=["layout"], response_model=Dict, operation_id="get_layout")
async def get_layout(
    request: Request, browser_id: Annotated[Union[str, None], Cookie()] = None
) -> Optional[Dict]:
    """
    Get layout.
    """
    app: SpotlightApp = request.app
    if app.data_source is None:
        return None
    dataset_uid = app.data_source.get_uid()
    layout = await app.config.get(
        CURRENT_LAYOUT_KEY, dataset=dataset_uid, user=browser_id or ""
    )
    layout = cast(Optional[Dict], layout)
    if layout is None:
        layout = (app.layout or DEFAULT_LAYOUT).dict(by_alias=True)
        await app.config.set(
            CURRENT_LAYOUT_KEY, layout, dataset=dataset_uid, user=browser_id or ""
        )
    return layout


@router.put(
    "/reset",
    tags=["layout"],
    response_model=Dict,
    operation_id="reset_layout",
)
async def reset_layout(
    request: Request, browser_id: Annotated[Union[str, None], Cookie()] = None
) -> Dict:
    """
    Get layout.
    """
    app: SpotlightApp = request.app
    layout = app.layout or DEFAULT_LAYOUT
    if app.data_source:
        dataset_uid = app.data_source.get_uid()
        await app.config.set(
            CURRENT_LAYOUT_KEY,
            layout.dict(by_alias=True),
            dataset=dataset_uid,
            user=browser_id or "",
        )
    return layout.dict(by_alias=True)


class SetLayoutRequest(BaseModel):
    """
    Set layout request model.
    """

    # pylint: disable=too-few-public-methods

    layout: Dict


@router.put("/", tags=["layout"], response_model=Dict, operation_id="set_layout")
async def set_layout(
    request: Request,
    set_layout_request: SetLayoutRequest,
    browser_id: Annotated[Union[str, None], Cookie()] = None,
) -> Dict:
    """
    Get layout.
    """
    app: SpotlightApp = request.app
    if app.data_source:
        dataset_uid = app.data_source.get_uid()
        await app.config.set(
            CURRENT_LAYOUT_KEY,
            set_layout_request.layout,
            dataset=dataset_uid,
            user=browser_id or "",
        )
    return set_layout_request.layout
