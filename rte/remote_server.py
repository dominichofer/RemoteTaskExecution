from typing import Optional
import grpc
from .entities import Task, Result
from .server import WorkerInterface, ClientInterface
from .rte_pb2 import (
    Empty as EmptyProto,
    Task as TaskProto,
    TaskId as TaskIdProto,
    TaskIds as TaskIdsProto,
    Result as ResultProto,
)
from .rte_pb2_grpc import RteStub


class RemoteServer(WorkerInterface, ClientInterface):
    """RemoteServer is a client that communicates with the server using gRPC."""

    def __init__(self, target) -> None:
        channel = grpc.insecure_channel(target)
        self.server = RteStub(channel)

    def get_next_id(self) -> Optional[int]:
        msg = EmptyProto()
        next_id = self.server.get_next_id(msg)
        if next_id.HasField("value"):
            return next_id.value
        return None

    def return_id(self, task_id: int) -> None:
        msg = TaskIdProto(value=task_id)
        self.server.return_id(msg)

    def add_task(self, task: Task) -> None:
        msg = TaskProto(id=task.id, data=task.data)
        self.server.add_task(msg)

    def get_task(self) -> Optional[Task]:
        msg = EmptyProto()
        task = self.server.get_task(msg)
        if task.HasField("id"):
            return Task(id=task.id, data=task.data)
        return None

    def set_result(self, result: Result) -> None:
        msg = ResultProto(task_id=result.task_id, success=result.success, data=result.data)
        self.server.set_result(msg)

    def get_results(self, task_ids: list[int]) -> list[Optional[Result]]:
        msg = TaskIdsProto(ids=task_ids)
        response = self.server.get_results(msg)
        return [
            Result(task_id=r.task_id, success=r.success, data=r.data)
            if r.HasField("task_id")
            else None
            for r in response.results
        ]

    def cancel_task(self, task_id: int) -> None:
        msg = TaskIdProto(value=task_id)
        self.server.cancel_task(msg)

    def is_task_canceled(self, task_id: int) -> bool:
        msg = TaskIdProto(value=task_id)
        response = self.server.is_task_canceled(msg)
        return response.value

    def release_waiting_workers(self) -> None:
        msg = EmptyProto()
        self.server.release_waiting_workers(msg)
