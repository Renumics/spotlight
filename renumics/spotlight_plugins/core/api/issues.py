"""
Problems API endpoints
"""

from typing import List

from fastapi import APIRouter, Request
from pydantic.dataclasses import dataclass

from renumics.spotlight.analysis import DataIssue

router = APIRouter(tags=["issues"])


@dataclass
class AnalysisInfo:
    """
    The current analysis status with all issues
    """

    running: bool
    issues: List[DataIssue]


@router.get("/", response_model=AnalysisInfo, operation_id="get_all")
async def get_all(request: Request) -> AnalysisInfo:
    """
    Get all data issues.
    """

    return AnalysisInfo(
        running=request.app.issues is None,
        issues=request.app.custom_issues + (request.app.issues or []),
    )
