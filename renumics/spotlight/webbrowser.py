"""
Launch browser.
"""

import threading
import time
import webbrowser

import requests
from loguru import logger


def wait_for(url: str) -> None:
    """Wait until the service at url is reachable."""
    while True:
        try:
            requests.head(url, timeout=10, verify=False)
            break
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)


def launch_browser_in_thread(url: str) -> threading.Thread:
    """Open the app in a browser in background once it runs."""
    thread = threading.Thread(target=launch_browser, args=(url,))
    thread.start()
    return thread


def launch_browser(url: str) -> None:
    """Open the app in a browser once it runs."""
    wait_for(url)  # wait also for socket?
    try:
        webbrowser.open(url)
    except Exception:
        logger.warning(
            f"Couldn't launch browser automatically, you can reach Spotlight at {url}."
        )
