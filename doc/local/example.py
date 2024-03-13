from threading import Thread
from rte import Server, Worker, BatchClient


class ToUpperWorker(Worker):
    def execute_task(self, task: bytes) -> bytes:
        return task.upper()

    def on_cancel(self) -> None:
        pass


if __name__ == "__main__":
    server = Server(task_timeout=1)

    worker = ToUpperWorker(server, refresh_time=0.5)
    worker_thread = Thread(target=worker.run)
    worker_thread.start()

    client = BatchClient(server, refresh_time=0.5)
    results = client.solve([b"task_1", b"task_2", b"task_3"])
    print(results)
    assert results == [b"TASK_1", b"TASK_2", b"TASK_3"]

    server.release_waiting_workers()
    server.stop()
    worker_thread.join()
