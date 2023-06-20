"""
Problems API endpoints
"""

from typing import List

from fastapi import APIRouter, Request

from renumics.spotlight.analysis import DataIssue

router = APIRouter(tags=["issues"])


@router.get("/", response_model=List[DataIssue], operation_id="get_all")
async def get_all(request: Request) -> List[DataIssue]:
    """
    Get all data issues.
    """
    return request.app.issues
