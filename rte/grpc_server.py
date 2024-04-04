from concurrent import futures
from typing import Optional
import grpc
from .entities import Task, Result
from .server import ServerInterface
from .rte_pb2 import (
    Empty as EmptyProto,
    Bool as BoolProto,
    Task as TaskProto,
    OptionalTask as OptionalTaskProto,
    TaskId as TaskIdProto,
    TaskIds as TaskIdsProto,
    OptionalTaskId as OptionalTaskIdProto,
    Result as ResultProto,
    OptionalResult as OptionalResult,
    OptionalResults as OptionalResults,
)
from .rte_pb2_grpc import RteServicer, add_RteServicer_to_server


class GrpcServer(RteServicer):
    """GrpcServer is a server that communicates with the client using gRPC."""

    def __init__(self, server: ServerInterface, port: int) -> None:
        self.server = server
        self.grpc_server = grpc.server(futures.ThreadPoolExecutor(1_000_000_000))
        add_RteServicer_to_server(self, self.grpc_server)
        self.grpc_server.add_insecure_port(f"[::]:{port}")

    def start(self) -> None:
        self.grpc_server.start()

    def wait_for_termination(self) -> None:
        self.grpc_server.wait_for_termination()

    def stop(self, grace: Optional[float] = None) -> None:
        self.grpc_server.stop(grace)

    def get_next_id(self, request: EmptyProto, context) -> OptionalTaskIdProto:
        next_id = self.server.get_next_id()
        if next_id is not None:
            return OptionalTaskIdProto(value=next_id)
        return OptionalTaskIdProto()

    def return_id(self, request: TaskIdProto, context) -> EmptyProto:
        self.server.return_id(request.value)
        return EmptyProto()

    def add_task(self, request: TaskProto, context) -> EmptyProto:
        self.server.add_task(Task(id=request.id, data=request.data))
        return EmptyProto()

    def get_task(self, request: EmptyProto, context) -> OptionalTaskProto:
        task = self.server.get_task()
        if task is None:
            return OptionalTaskProto()
        return OptionalTaskProto(id=task.id, data=task.data)

    def set_result(self, request: ResultProto, context) -> EmptyProto:
        self.server.set_result(
            Result(task_id=request.task_id, success=request.success, data=request.data)
        )
        return EmptyProto()

    def get_results(self, request: TaskIdsProto, context) -> OptionalResults:
        results = self.server.get_results(request.ids)
        return OptionalResults(
            results=[
                OptionalResult(
                    task_id=r.task_id, success=r.success, data=r.data
                )
                if r is not None
                else OptionalResult()
                for r in results
            ]
        )

    def cancel_task(self, request: TaskIdProto, context) -> EmptyProto:
        self.server.cancel_task(request.value)
        return EmptyProto()

    def is_task_canceled(self, request: TaskIdProto, context) -> BoolProto:
        return BoolProto(value=self.server.is_task_canceled(request.value))

    def release_waiting_workers(self, request: EmptyProto, context) -> EmptyProto:
        self.server.release_waiting_workers()
        return EmptyProto()
