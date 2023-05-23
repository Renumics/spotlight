"""
    middleware for timing requests
"""

import time
from typing import Callable
from fastapi import FastAPI, Request, Response
from loguru import logger


def _cpu_time() -> float:
    """
    get combined cpu time (user+system)
    """
    # pylint: disable=import-outside-toplevel
    import resource

    usage = resource.getrusage(resource.RUSAGE_SELF)
    return usage[0] + usage[1]


def add_timing_middleware(app: FastAPI) -> None:
    """
    add a middleware that prints cpu and wall times for all endpoints
    """

    @app.middleware("http")
    async def _(request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        start_cpu_time = _cpu_time()

        response = await call_next(request)

        cpu_time = _cpu_time() - start_cpu_time
        wall_time = time.time() - start_time

        if "route" in request.scope:
            endpoint = request.scope["route"].name

            logger.info(
                "TIMING | Wall: {wall:6.1f} | CPU: {cpu:6.1f} | {endpoint}",
                wall=1000 * wall_time,
                cpu=1000 * cpu_time,
                endpoint=endpoint,
            )

        return response
