"""
Launch browser.
"""
import os
import sys
import threading
import time
import webbrowser

import requests
from loguru import logger

from renumics.spotlight.environ import set_temp_environ


def wait_for(url: str) -> None:
    """Wait until the service at url is reachable."""
    while True:
        try:
            requests.head(url, timeout=10)
            break
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)


def launch_browser_in_thread(host: str, port: int) -> threading.Thread:
    """Open the app in a browser in background once it runs."""
    thread = threading.Thread(target=launch_browser, args=(host, port))
    thread.start()
    return thread


def launch_browser(host: str, port: int) -> None:
    """Open the app in a browser once it runs."""
    app_url = f"http://{host}:{port}/"
    wait_for(app_url)  # wait also for socket?

    # If we want to launch firefox with the webbrowser module,
    # we need to restore LD_LIBRARY_PATH if running through pyinstaller.
    # The original LD_LIBRARY_PATH is stored as LD_LIBRARY_PATH_ORIG.
    # See https://github.com/pyinstaller/pyinstaller/issues/6334
    try:
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            with set_temp_environ(
                LD_LIBRARY_PATH=os.environ.get("LD_LIBRARY_PATH_ORIG")
            ):
                webbrowser.open(app_url)
        else:
            webbrowser.open(app_url)
    except Exception:  # pylint: disable=broad-except
        logger.warning(
            f"Couldn't launch browser automatically, you can reach Spotlight at {app_url}."
        )
