import logging
from dataclasses import dataclass
from time import sleep
from collections import deque
from abc import ABC, abstractmethod
from typing import Optional
from .entities import Task, Result
from .server import ClientInterface


class Client(ABC):
    def __init__(self, server: ClientInterface, refresh_time: float) -> None:
        self._server = server
        self._refresh_time = refresh_time
        self._pending_task_ids: set[int] = set()

    @abstractmethod
    def on_request(self, task_id: int) -> Optional[Task]:
        "Triggered when the client needs a new task."

    @abstractmethod
    def on_result(self, result: Result) -> None:
        "Triggered when a task is finished."

    @abstractmethod
    def is_finished(self) -> bool:
        "Returns True iff the client has no more tasks to process."

    def _process_tasks(self) -> bool:
        """
        Requests a new task from the server.
        Returns True if a task was received and added.
        """
        task_id = self._server.get_next_id()
        logging.debug("Client received task id: %s", task_id)
        if task_id is None:
            return False

        task = self.on_request(task_id)
        if task is None:
            logging.debug("Client is returning task id: %s", task_id)
            self._server.return_id(task_id)
            return False
        else:
            logging.info("Client is adding task: %s", task)
            self._server.add_task(task)
            self._pending_task_ids.add(task.id)
            return True

    def _process_results(self) -> bool:
        """
        Requests results from the server.
        Returns True if any results were received.
        """
        if not self._pending_task_ids:
            return False
        results = self._server.get_results(list(self._pending_task_ids))
        logging.debug("Client received results: %s", results)
        any_result = False
        for result in results:
            if result is not None:
                any_result = True
                logging.info("Client received result: %s", result)
                self.on_result(result)
                self._pending_task_ids.remove(result.task_id)
        return any_result

    def run(self) -> None:
        while not self.is_finished():
            added_task = self._process_tasks()
            received_result = self._process_results()
            if not added_task and not received_result:
                # Sleep if there was no activity
                sleep(self._refresh_time)

    def cancel_task(self, task_id: int) -> None:
        logging.info("Client is canceling task: %s", task_id)
        self._server.cancel_task(task_id)


@dataclass
class _Task:
    index: int
    attempts: int
    data: bytes


class BatchClient(Client):
    def __init__(self, server: ClientInterface, refresh_time: float, attempts: int = 1) -> None:
        super().__init__(server, refresh_time)
        self._attempts = attempts
        self._tasks: deque[_Task]
        self._sent_tasks: dict[int, _Task]  # task_id -> task
        self._results: list[Optional[bytes]]

    def solve(self, tasks: list[bytes]) -> list[Optional[bytes]]:
        self._tasks = deque(_Task(i, 0, task) for i, task in enumerate(tasks))
        self._sent_tasks = {}
        self._results = [None] * len(tasks)
        super().run()
        return self._results

    def on_request(self, task_id: int) -> Optional[Task]:
        if not self._tasks:
            return None
        task = self._tasks.popleft()
        self._sent_tasks[task_id] = task
        return Task(task_id, task.data)

    def on_result(self, result: Result) -> None:
        task = self._sent_tasks.pop(result.task_id)
        task.attempts += 1
        if result.success:
            self._results[task.index] = result.data
        else:
            if task.attempts < self._attempts:
                # Retry task
                self._tasks.appendleft(task)
            else:
                # Task failed
                self._results[task.index] = None

    def is_finished(self) -> bool:
        return not self._tasks and not self._sent_tasks
