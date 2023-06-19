"""
Problems API endpoints
"""

from typing import List

from fastapi import APIRouter, Request

from renumics.spotlight.analysis import find_issues, DatasetIssue
from renumics.spotlight.backend.types import SpotlightApp

router = APIRouter(tags=["issues"])


@router.get("/", response_model=List[DatasetIssue], operation_id="get_all")
async def get_all(request: Request) -> List[DatasetIssue]:
    """
    Get all data issues.
    """

    app: SpotlightApp = request.app

    if not app.data_source:
        return []

    data_source = app.data_source
    issues = find_issues(data_source, dtypes=data_source.dtype)  # type: ignore
    return issues
