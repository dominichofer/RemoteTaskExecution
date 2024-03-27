import logging
from abc import ABC, abstractmethod
from queue import Queue, Empty
from threading import Lock
from typing import Optional
from .heartbeat import MultiHeartbeatMonitor
from .entities import Task, Result
from .id_generator import IdGenerator


class WorkerInterface(ABC):
    @abstractmethod
    def get_task(self) -> Optional[Task]:
        "Returns a task for the worker to execute or None."

    @abstractmethod
    def set_result(self, result: Result) -> None:
        "Sets the result of a task."

    @abstractmethod
    def is_task_canceled(self, task_id: int) -> bool:
        """
        Returns True iff the task is canceled.
        If so, the task is removed from the list of canceled tasks.
        Refreshs the task's heartbeat.
        """


class ClientInterface(ABC):
    @abstractmethod
    def get_next_id(self) -> Optional[int]:
        "Returns an available task ID or None."

    @abstractmethod
    def return_id(self, task_id: int) -> None:
        "Returns a task ID to the server."

    @abstractmethod
    def add_task(self, task: Task) -> None:
        "Adds a task to the server."

    @abstractmethod
    def get_results(self, task_ids: list[int]) -> list[Optional[Result]]:
        "Returns the results of the tasks with the given IDs."

    @abstractmethod
    def cancel_task(self, task_id: int) -> None:
        "Cancels a task."


class ServerInterface(WorkerInterface, ClientInterface):
    pass


class Server(ServerInterface):
    def __init__(self, task_timeout: float) -> None:
        self._lock = Lock()
        self._unassigned_ids: Queue[int] = Queue()
        self._tasks: Queue[Optional[Task]] = Queue()
        self._next_id = IdGenerator()
        self._results: dict[int, Result] = {}
        self._canceled: set[int] = set()
        self._heartbeats = MultiHeartbeatMonitor(task_timeout, self._on_task_timeout)

    def _on_task_timeout(self, task_id: int) -> None:
        with self._lock:
            logging.info("Task %s timed out", task_id)
            self._results[task_id] = Result(task_id, success=False, data=b"")
            if task_id in self._canceled:
                self._canceled.remove(task_id)

    def get_next_id(self) -> Optional[int]:
        try:
            task_id = self._unassigned_ids.get_nowait()
            logging.info("Server sends task id: %s", task_id)
            return task_id
        except Empty:
            logging.debug("Server has no task ids")
            return None

    def return_id(self, task_id: int) -> None:
        logging.debug("Server received returned task id: %s", task_id)
        self._unassigned_ids.put(task_id)

    def add_task(self, task: Task) -> None:
        logging.info("Server received task: %s", task.id)
        self._tasks.put(task)

    def get_task(self) -> Optional[Task]:
        logging.debug("Server received task request")
        self._unassigned_ids.put(self._next_id())
        task = self._tasks.get()
        if task is None:
            logging.debug("Server has no tasks")
            return None
        with self._lock:
            self._heartbeats.add(task.id)
            logging.info("Server sends task for id: %s", task.id)
            return task

    def set_result(self, result: Result) -> None:
        logging.info("Server received result for task: %s", result.task_id)
        tid = result.task_id
        with self._lock:
            self._heartbeats.remove(tid)
            self._results[tid] = result
            if tid in self._canceled:
                self._canceled.remove(tid)

    def get_results(self, task_ids: list[int]) -> list[Optional[Result]]:
        logging.debug("Server received results request for tasks: %s", task_ids)
        with self._lock:
            return [self._results.pop(tid, None) for tid in task_ids]

    def cancel_task(self, task_id: int) -> None:
        logging.info("Server cancels task: %s", task_id)
        with self._lock:
            self._heartbeats.remove(task_id)
            self._canceled.add(task_id)

    def is_task_canceled(self, task_id: int) -> bool:
        logging.debug("Server checks if task is canceled: %s", task_id)
        with self._lock:
            self._heartbeats.beat(task_id)
            if task_id in self._canceled:
                logging.info("Server confirms task is canceled: %s", task_id)
                self._canceled.remove(task_id)
                return True
            return False

    def release_waiting_workers(self) -> None:
        "Releases all waiting workers."
        while True:
            try:
                self._unassigned_ids.get_nowait()
            except Empty:
                break
            logging.info("Server releases a waiting worker")
            self._tasks.put(None)

    def stop(self) -> None:
        "Stops the server."
        logging.debug("Server stops")
        self._heartbeats.stop()
