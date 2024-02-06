"""
performance and crash reporting
"""

import datetime
import platform
import sys
import threading
import time
from functools import wraps
from os import environ
from typing import Any, Callable, Dict, Optional, Union
from uuid import uuid4

import machineid
import requests
from loguru import logger

from renumics.spotlight import __version__
from renumics.spotlight.plugin_loader import load_plugins
from renumics.spotlight.settings import settings

ANALYTICS_URL = "https://analytics.renumics.com/v1/spotlight"


def _get_node() -> str:
    """
    get the anonymized (hashed) unique node id for this machine
    'spotlight' is added to the hash in order to prevent tracking across different apps
    """
    try:
        return machineid.hashed_id("spotlight")
    except Exception:
        logger.debug("Unable to obtain machine ID")
        return "UNKNOWN"


TOKEN = _get_node()


def skip_analytics() -> bool:
    """
    analytics will be skipped when opt_in is false and opt_out is true
    or CI environment variable is set
    """

    if environ.get("CI", False):
        logger.debug("analytics skipped because CI environment variable is set")
        return True

    # if opt_in is set (which is not default) dont skip
    if settings.opt_in:
        return False

    return settings.opt_out


def _get_python_runtime() -> str:
    # try to determine what python runtime we are running in
    # plain python, ipython, ipython in colab, ipython in kaggle
    try:
        python_runtime = "python"

        try:
            ipython_kernel = get_ipython()  # type:ignore
            python_runtime = "ipython"
            if "google.colab" in str(ipython_kernel):
                python_runtime += "_colab"
            elif "KAGGLE_KERNEL_RUN_TYPE" in environ:
                python_runtime += (
                    f"_kaggle_{environ.get('KAGGLE_KERNEL_RUN_TYPE', None)}"
                )
            elif "SPACE_ID" in environ:
                python_runtime += "huggingface"
        except NameError:
            pass

    except Exception as e:
        python_runtime = "error get_python_runtime_" + python_runtime + "_" + str(e)
        logger.warning("could not determine python runtime", python_runtime)

    return f"{python_runtime}_{sys.version}"


key_map = {
    "type": "t",
    "date": "d",
    "pathname": "p",
    "event_id": "eId",
    "runtime_s": "rts",
    "timed_fn": "tfn",
    "detail": "det",
    "platform": "pl",
    "python_version": "pyv",
    "version": "v",
    "plugins": "pls",
    "token": "tk",
    "space_id": "spid",
}

event_type_key_map = {
    "spotlight_timing": "spt",
    "spotlight_startup": "sps",
    "spotlight_exit": "spe",
    "spotlight_exception": "spex",
}


def report_event(event: Dict[str, Any]) -> None:
    """
    Report an event to the analytics server.
    """

    if skip_analytics():
        logger.info("analytics skipped")
        return

    event["date"] = datetime.datetime.now().isoformat()
    event["token"] = TOKEN
    event["event_id"] = str(uuid4())
    event["version"] = str(__version__)
    event["python_version"] = _get_python_runtime()
    event["space_id"] = environ.get("SPACE_ID", None)
    event["type"] = event_type_key_map[event["type"]]
    event["plugins"] = []
    if settings.dev:
        event["dev"] = settings.dev

    loaded_plugins = load_plugins()
    if loaded_plugins is not None:
        for plugin in loaded_plugins:
            try:
                plugin_version = plugin.module.__version__
            except AttributeError:
                plugin_version = "n/a"

            event["plugins"].append(f"{plugin.name}__{plugin_version}")

    # compress and base64 encode the event
    encoded = {key_map[k] if k in key_map else k: v for k, v in event.items()}

    logger.debug("sending analytics event")

    def _post_request() -> None:
        try:
            # post request to analytics server with minimal timeout (to prevent blocking)
            requests.post(
                ANALYTICS_URL,
                json={"events": [encoded]},
                timeout=20,
            )
        except requests.exceptions.ReadTimeout:
            pass
        except requests.exceptions.ConnectionError:
            logger.warning("could not connect to analytics server")

    threading.Thread(target=_post_request).start()


def emit_startup_event() -> None:
    """
    Emit a start event.
    """
    report_event({"type": "spotlight_startup"})


def emit_exit_event() -> None:
    """
    Emit a start event.
    """
    report_event({"type": "spotlight_exit"})


def emit_exception_event() -> None:
    """
    Emit an exception event.
    """
    ex_type, ex_value, _ = sys.exc_info()
    detail = str(ex_value)
    if ex_type is not None:
        detail = f"{ex_type.__name__}: {ex_value}"
    report_event(
        {
            "type": "spotlight_exception",
            "detail": detail,
            "platform": platform.platform(),
        }
    )


FuncType = Callable[..., Any]


def emit_timed_event(
    orig_func: FuncType, *, func_name: Optional[str] = None
) -> Union[FuncType, Callable[..., FuncType]]:
    """
    Wrap a function in order to emit a timed event when it completes.

    This decorator can be used with an explicit name of the event to emit, or
    it will use the name of the function.
    """

    def _decorator(func: FuncType) -> FuncType:
        @wraps(func)
        def _wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            result = func(*args, **kwargs)
            name = func_name or func.__name__
            report_event(
                {
                    "type": "spotlight_timing",
                    "runtime_s": time.time() - start_time,
                    "timed_fn": name,
                }
            )
            return result

        return _wrapper

    if orig_func is not None:
        return _decorator(orig_func)

    return _decorator
