from time import sleep
from typing import Optional
from rte import WorkerInterface, ClientInterface, ServerInterface, Worker, Task, Result, Client


def wait_for_next_id(server: ClientInterface) -> int:
    "Get the next task id from the server."
    for _ in range(10):
        task_id = server.get_next_id()
        if task_id is not None:
            return task_id
        sleep(0.1)
    raise RuntimeError("No task id available")


class ServerStub(ServerInterface):
    def get_next_id(self) -> Optional[int]:
        raise NotImplementedError

    def return_id(self, task_id: int) -> None:
        raise NotImplementedError

    def add_task(self, task: Task) -> None:
        raise NotImplementedError

    def get_task(self) -> Optional[Task]:
        raise NotImplementedError

    def set_result(self, result: Result) -> None:
        raise NotImplementedError

    def get_results(self, task_ids: list[int]) -> list[Optional[Result]]:
        raise NotImplementedError

    def cancel_task(self, task_id: int) -> None:
        raise NotImplementedError

    def is_task_canceled(self, task_id: int) -> bool:
        raise NotImplementedError

    def release_waiting_workers(self) -> None:
        raise NotImplementedError


class TrivialClient(Client):
    def __init__(self, server: ClientInterface, refresh_time: float) -> None:
        super().__init__(server, refresh_time)
        self.tasks: list[Optional[bytes]] = [b"task"]
        self.results: list[Optional[Result]] = []

    def on_request(self, task_id: int) -> Optional[Task]:
        if not self.tasks:
            return None
        data = self.tasks.pop(0)
        if data is None:
            return None
        return Task(task_id, data)

    def on_result(self, result: Result) -> None:
        self.results.append(result)

    def is_finished(self) -> bool:
        if self.tasks:
            return False
        return not self._pending_task_ids


class TrivialWorker(Worker):
    def execute_task(self, task: bytes) -> bytes:
        return task

    def on_cancel(self) -> None:
        pass


class LongRunningWorker(Worker):
    def execute_task(self, task: bytes) -> bytes:
        sleep(0.3)
        return task

    def on_cancel(self) -> None:
        pass


class RaisingWorker(Worker):
    def execute_task(self, task: bytes) -> bytes:
        raise RuntimeError("Dying")

    def on_cancel(self) -> None:
        pass


class CancellableWorker(Worker):
    def __init__(self, server: WorkerInterface, refresh_time: float) -> None:
        super().__init__(server, refresh_time)
        self._canceled = False

    def execute_task(self, task: bytes) -> bytes:
        sleep(0.3)
        if self._canceled:
            raise RuntimeError("Canceled")
        return task

    def on_cancel(self) -> None:
        self._canceled = True


class DyingWorker(Worker):
    def execute_task(self, task: bytes) -> bytes:
        self._refresher.stop()
        sleep(self._refresh_time * 6)
        return task

    def on_cancel(self) -> None:
        pass
