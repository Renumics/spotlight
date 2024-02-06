"""
Layout API endpoints
"""

from typing import Dict, Optional, Union

from fastapi import APIRouter, Cookie, Request
from pydantic import BaseModel
from typing_extensions import Annotated

from renumics.spotlight.app import CURRENT_LAYOUT_KEY, SpotlightApp

router = APIRouter()


@router.get(
    "/", tags=["layout"], response_model=Optional[Dict], operation_id="get_layout"
)
async def get_layout(
    request: Request, browser_id: Annotated[Union[str, None], Cookie()] = None
) -> Optional[Dict]:
    """
    Get layout.
    """
    return await request.app.get_current_layout_dict(browser_id or "")


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
    layout = app.layout
    if app.data_store:
        dataset_uid = app.data_store.uid
        await app.config.set(
            CURRENT_LAYOUT_KEY,
            layout.model_dump(by_alias=True),
            dataset=dataset_uid,
            user=browser_id or "",
        )
    return layout.model_dump(by_alias=True)


class SetLayoutRequest(BaseModel):
    """
    Set layout request model.
    """

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
    if app.data_store:
        dataset_uid = app.data_store.uid
        await app.config.set(
            CURRENT_LAYOUT_KEY,
            set_layout_request.layout,
            dataset=dataset_uid,
            user=browser_id or "",
        )
    return set_layout_request.layout
