# Remote Task Execution

## Description
This project is about executing tasks remotely. It allows users to run tasks on a remote machine from their local machine.

## Installation
Use pip.

## Usage
Create a worker and a client, by implementing their abstract methods.
```python
from abc import ABC, abstractmethod


class Client(ABC):
    @abstractmethod
    def on_request(self, task_id: int) -> Optional[Task]:
        "Triggered when the client needs a new task."

    @abstractmethod
    def on_result(self, result: Result) -> None:
        "Triggered when a task is finished."

    @abstractmethod
    def is_finished(self) -> bool:
        "Returns True iff the client has no more tasks to process."


class Worker(ABC):
    @abstractmethod
    def execute_task(self, task: bytes) -> bytes:
        pass

    @abstractmethod
    def on_cancel(self) -> None:
        pass
```
To process a batch of tasks, use `BatchClient`.

### Locally
Running the server, worker and client locally, is straight forward.
```python
from threading import Thread
from rte import Server, Worker, BatchClient


class ToUpperWorker(Worker):
    def execute_task(self, task: bytes) -> bytes:
        return task.upper()

    def on_cancel(self) -> None:
        pass


if __name__ == "__main__":
    # Create a server
    server = Server(task_timeout=1)

    # Create a worker and run it in a thread
    worker = ToUpperWorker(server, refresh_time=0.5)
    worker_thread = Thread(target=worker.run)
    worker_thread.start()

    # Create a client and submit tasks
    client = BatchClient(server, refresh_time=0.5)
    results = client.solve([b"task_1", b"task_2", b"task_3"])
    print(results)

    # Release all workers that are waiting for a task
    server.release_waiting_workers()
    server.stop()

    worker_thread.join()
```
from `doc/local/example.py`.

### Distributed
To run the server, worker and client distributed, grpc is used.
An example is provided in `doc/distributed/`.
```python
from rte import Server, GrpcServer


if __name__ == "__main__":
    # Create a server
    server = Server(task_timeout=1)

    # Create and start the grpc server on port 50051
    rpc_server = GrpcServer(server, port=50051)
    rpc_server.start()
```
```python
from rte import Worker, RemoteServer


class ToUpperWorker(Worker):
    def execute_task(self, task: bytes) -> bytes:
        return task.upper()

    def on_cancel(self) -> None:
        pass


if __name__ == "__main__":
    # Create a connection to the remote server
    server = RemoteServer("localhost:50051")

    # Create and run the worker
    worker = ToUpperWorker(server, refresh_time=0.5)
    worker.run()
```
```python
from rte import BatchClient, RemoteServer


if __name__ == "__main__":
    # Create a connection to the remote server
    server = RemoteServer("localhost:50051")

    # Create and use the client
    client = BatchClient(server, refresh_time=0.5)
    results = client.solve([b"task_1", b"task_2", b"task_3"])

    # Print and verify the results
    print(results)
    assert results == [b"TASK_1", b"TASK_2", b"TASK_3"]
```
