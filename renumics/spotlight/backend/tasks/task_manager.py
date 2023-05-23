"""
This module provides a simple managment class for long running tasks
"""

import asyncio
import multiprocessing
from concurrent.futures import Future, ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from typing import Any, Callable, List, Optional, Sequence, TypeVar, Union

from .exceptions import TaskCancelled
from .task import Task

T = TypeVar("T")


class TaskManager:
    """
    Handles task creation, deletion and cleanup
    """

    tasks: List[Task]
    pool: ProcessPoolExecutor

    def __init__(self) -> None:
        self.tasks = []
        self.pool = ProcessPoolExecutor(2, multiprocessing.get_context("spawn"))

    def create_task(
        self,
        func: Callable,
        args: Sequence[Any],
        name: Optional[str] = None,
        tag: Optional[Union[str, int]] = None,
    ) -> Task:
        """
        create and launch a new task
        """
        # cancel running task with same name
        self.cancel(name=name)

        future = self.pool.submit(func, *args)

        task = Task(name, tag, future)
        self.tasks.append(task)

        def _cleanup(_: Future) -> None:
            try:
                self.tasks.remove(task)
            except ValueError:
                # task won't be in list when already cancelled. this is fine
                pass

        future.add_done_callback(_cleanup)

        return task

    async def run_async(
        self,
        func: Callable[..., T],
        args: Sequence[Any],
        name: Optional[str] = None,
        tag: Optional[Union[str, int]] = None,
    ) -> T:
        """
        Launch a new task. Await and return result.
        """

        task = self.create_task(func, args, name, tag)
        try:
            return await asyncio.wrap_future(task.future)
        except BrokenProcessPool as e:
            raise TaskCancelled from e

    def cancel(
        self, name: Optional[str] = None, tag: Optional[Union[str, int]] = None
    ) -> None:
        """
        Cancel running and queued tasks.
        """

        tasks_to_remove = []

        if name is not None and tag is not None:
            for task in self.tasks:
                if task.name == name and task.tag == tag:
                    tasks_to_remove.append(task)
        elif name is not None:
            for task in self.tasks:
                if task.name == name:
                    tasks_to_remove.append(task)
        elif tag is not None:
            for task in self.tasks:
                if task.tag == tag:
                    tasks_to_remove.append(task)

        for task in tasks_to_remove:
            task.future.cancel()
            try:
                self.tasks.remove(task)
            except ValueError:
                # task won't be in list when already cancelled. this is fine
                pass

    def cancel_all(self) -> None:
        """
        Cancel all running and queued tasks.
        """
        for task in self.tasks:
            task.future.cancel()
        self.tasks.clear()

    def shutdown(self) -> None:
        """
        Shutdown and cleanup tasks and internal process pool.
        This task manager instance won't work after this operation!
        """
        self.cancel_all()
        self.pool.shutdown(wait=True)
