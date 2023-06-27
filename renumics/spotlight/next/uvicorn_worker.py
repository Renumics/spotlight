import time
import threading
from typing import List, Any, Dict, Optional
import signal
import os
import multiprocessing.connection
from uvicorn.workers import UvicornWorker

# per process worker instance
worker: Optional["RestartableUvicornWorker"] = None


class ReloaderThread(threading.Thread):
    def __init__(self, worker: UvicornWorker, sleep_interval: float = 1.0):
        super().__init__()
        self.setDaemon(True)
        self._worker = worker
        self._interval = sleep_interval

    def run(self) -> None:
        while True:
            if not self._worker.alive:
                os.kill(os.getpid(), signal.SIGINT)
            time.sleep(self._interval)


class RestartableUvicornWorker(UvicornWorker):
    CONFIG_KWARGS = {"loop": "uvloop", "http": "httptools"}

    def __init__(self, *args: List[Any], **kwargs: Dict[str, Any]):
        super().__init__(*args, **kwargs)
        self._reloader_thread = ReloaderThread(self)

    def run(self) -> None:
        if self.cfg.reload:
            self._reloader_thread.start()

        global worker
        worker = self

        super().run()

    @property
    def connection(self) -> multiprocessing.connection.Connection:
        return self.app.connection
