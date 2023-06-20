"""
Problems API endpoints
"""

from typing import List

from fastapi import APIRouter

from renumics.spotlight.analysis import ISSUES, DataIssue

router = APIRouter(tags=["issues"])


@router.get("/", response_model=List[DataIssue], operation_id="get_all")
async def get_all() -> List[DataIssue]:
    """
    Get all data issues.
    """
    return ISSUES
