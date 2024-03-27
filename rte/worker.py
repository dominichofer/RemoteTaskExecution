import logging
from abc import ABC, abstractmethod
from typing import Optional
from .server import WorkerInterface
from .heartbeat import Heart
from .entities import Result


class Worker(ABC):
    def __init__(self, server: WorkerInterface, refresh_time: float) -> None:
        self._server = server
        self._refresh_time = refresh_time
        self._refresher: Heart

    @abstractmethod
    def execute_task(self, task: bytes) -> bytes:
        pass

    @abstractmethod
    def on_cancel(self) -> None:
        pass

    def _check_task(self, task_id: int) -> None:
        logging.debug("Worker is checking task: %s", task_id)
        if self._server.is_task_canceled(task_id):
            logging.info("Task %s was canceled", task_id)
            self._refresher.stop()
            self.on_cancel()

    def run(self, num_tasks: Optional[int] = None) -> None:
        while num_tasks is None or num_tasks > 0:
            task = self._server.get_task()
            logging.info("Worker received task: %s", task)
            if task is None:
                break

            self._refresher = Heart(self._refresh_time, self._check_task, task.id)
            try:
                logging.debug("Worker is executing task: %s", task.id)
                ret = self.execute_task(task.data)
                logging.info("Worker finished task: %s", task.id)
                result = Result(task.id, success=True, data=ret)
            except Exception as _:
                logging.info("Worker failed task: %s", task.id)
                result = Result(task.id, success=False, data=b"")
            self._refresher.stop()
            self._refresher.join()
            self._server.set_result(result)
            if num_tasks is not None:
                num_tasks -= 1
