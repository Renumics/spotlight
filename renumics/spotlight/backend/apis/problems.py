"""
Problems API endpoints
"""

from typing import List

from fastapi import APIRouter, Request

from renumics.spotlight.analysis import find_problems, DatasetProblem
from renumics.spotlight.backend.types import SpotlightApp

router = APIRouter(tags=["problems"])


@router.get("/", response_model=List[DatasetProblem], operation_id="get_all")
async def get_all(request: Request) -> List[DatasetProblem]:
    """
    Get all problems.
    """

    app: SpotlightApp = request.app

    if not app.data_source:
        return []

    data_source = app.data_source
    problems = find_problems(data_source.df, dtypes=data_source.dtype)  # type: ignore
    return problems
