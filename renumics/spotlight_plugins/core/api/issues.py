"""
Problems API endpoints
"""

from typing import List, Optional

from fastapi import APIRouter, Request

from renumics.spotlight.analysis import DataIssue

router = APIRouter(tags=["issues"])


@router.get("/", response_model=Optional[List[DataIssue]], operation_id="get_all")
async def get_all(request: Request) -> Optional[List[DataIssue]]:
    """
    Get all data issues.
    """

    if request.app.issues is None:
        if request.app.custom_issues:
            return request.app.custom_issues
        return None

    return request.app.issues + request.app.custom_issues
