"""
start flask development server
"""

import asyncio
import re
from pathlib import Path
from typing import Any, Union
import uuid

from fastapi import Request, status, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger
from typing_extensions import Annotated

from renumics.spotlight.backend.exceptions import Problem
from renumics.spotlight.develop.project import get_project_info
from renumics.spotlight.plugin_loader import load_plugins
from renumics.spotlight.reporting import (
    emit_exception_event,
    emit_exit_event,
    emit_startup_event,
)
from renumics.spotlight.settings import settings

from .apis import plugins as plugin_api
from .apis import websocket
from .middlewares.timing import add_timing_middleware
from .types import SpotlightApp
from .websockets import WebsocketManager


def create_app() -> SpotlightApp:
    """
    create app
    """

    app = SpotlightApp()
    app.include_router(websocket.router, prefix="/api")
    app.include_router(plugin_api.router, prefix="/api/plugins")

    @app.exception_handler(Exception)
    async def _(_: Request, e: Exception) -> JSONResponse:
        if settings.verbose:
            logger.exception(e)
        else:
            logger.info(e)
        emit_exception_event()
        class_name = type(e).__name__
        title = re.sub(r"([a-z])([A-Z])", r"\1 \2", class_name)
        return JSONResponse(
            {"title": title, "detail": str(e), "type": class_name},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @app.exception_handler(Problem)
    async def _(_: Request, problem: Problem) -> JSONResponse:
        if settings.verbose:
            logger.exception(problem)
        else:
            logger.info(problem)
        return JSONResponse(
            {
                "title": problem.title,
                "detail": problem.detail,
                "type": type(problem).__name__,
            },
            status_code=problem.status_code,
        )

    for plugin in load_plugins():
        plugin.activate(app)

    @app.on_event("startup")
    def _() -> None:
        loop = asyncio.get_running_loop()
        app.websocket_manager = WebsocketManager(loop)
        emit_startup_event()

    @app.on_event("shutdown")
    def _() -> None:
        app.task_manager.shutdown()
        emit_exit_event()

    try:
        app.mount(
            "/static",
            StaticFiles(packages=["renumics.spotlight.backend"]),
            name="assets",
        )
    except AssertionError:
        logger.warning("Frontend folder does not exist. No frontend will be served.")

    templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

    @app.get("/")
    def _(
        request: Request, browser_id: Annotated[Union[str, None], Cookie()] = None
    ) -> Any:
        response = templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "dev": settings.dev,
                "dev_location": get_project_info().type,
                "vite_url": request.app.vite_url,
                "filebrowsing_allowed": request.app.filebrowsing_allowed,
            },
        )
        response.set_cookie(
            "browser_id", browser_id or str(uuid.uuid4()), samesite="none", secure=True
        )
        return response

    if settings.dev:
        logger.info("Running in dev mode")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        add_timing_middleware(app)

    return app
