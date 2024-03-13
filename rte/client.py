import logging
from time import sleep
from abc import ABC, abstractmethod
from typing import Optional
from .entities import Task, Result
from .server import ClientInterface


class Client(ABC):
    def __init__(self, server: ClientInterface, refresh_time: float, retries: int = 0) -> None:
        self._server = server
        self._refresh_time = refresh_time
        self._retries = retries
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

    def _process_tasks(self) -> None:
        task_id = self._server.get_next_id()
        logging.debug("Client received task id: %s", task_id)
        if task_id is None:
            return

        task = self.on_request(task_id)
        if task is None:
            logging.debug("Client is returning task id: %s", task_id)
            self._server.return_id(task_id)
        else:
            logging.debug("Client is adding task: %s", task)
            self._server.add_task(task)
            self._pending_task_ids.add(task.id)

    def _process_results(self) -> None:
        if not self._pending_task_ids:
            return
        results = self._server.get_results(list(self._pending_task_ids))
        logging.debug("Client received results: %s", results)
        for result in results:
            if result:
                self.on_result(result)
                self._pending_task_ids.remove(result.task_id)

    def run(self) -> None:
        while not self.is_finished():
            self._process_tasks()
            self._process_results()
            sleep(self._refresh_time)

    def cancel_task(self, task_id: int) -> None:
        logging.debug("Client is canceling task: %s", task_id)
        self._server.cancel_task(task_id)


class BatchClient(Client):
    def __init__(self, server: ClientInterface, refresh_time: float) -> None:
        super().__init__(server, refresh_time)
        self._tasks: list[bytes]
        self._results: dict[int, Optional[bytes]]
        self._task_ids: list[int]

    def solve(self, tasks: list[bytes]) -> list[Optional[bytes]]:
        self._tasks = tasks
        self._results = {}
        self._task_ids = []
        super().run()
        return [self._results[tid] for tid in self._task_ids]

    def on_request(self, task_id: int) -> Optional[Task]:
        if not self._tasks:
            return None
        self._task_ids.append(task_id)
        return Task(task_id, self._tasks.pop(0))

    def on_result(self, result: Result) -> None:
        self._results[result.task_id] = result.data

    def is_finished(self) -> bool:
        return (not self._tasks) and (len(self._results) == len(self._task_ids))
