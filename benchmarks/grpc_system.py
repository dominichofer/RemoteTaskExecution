import multiprocessing
import threading
import time
from rte import Server, GrpcServer, RemoteServer, Worker, BatchClient


class TrivialWorker(Worker):
    def execute_task(self, task: bytes) -> bytes:
        return task

    def on_cancel(self) -> None:
        pass


def work(server):
    worker = TrivialWorker(server, refresh_time=1)
    worker.run()


def throuput(thread_count: int) -> float:
    num_tasks = 1000
    tasks = [i.to_bytes(4) for i in range(num_tasks)]
    server = Server(task_timeout=10)
    grpc_server = GrpcServer(server, 50051)
    grpc_server.start()
    remote_server = RemoteServer("localhost:50051")

    threads = []
    for _ in range(thread_count):
        threads.append(threading.Thread(target=work, args=(remote_server,)))
    for t in threads:
        t.start()

    client = BatchClient(remote_server, refresh_time=0.001)
    start = time.perf_counter()
    client.solve(tasks)
    end = time.perf_counter()

    server.release_waiting_workers()
    server.stop()

    for t in threads:
        t.join()

    grpc_server.stop()

    return num_tasks / (end - start)


if __name__ == "__main__":
    for i in range(1, multiprocessing.cpu_count() + 1):
        print(f"Throuput with {i} threads: {throuput(i)}")
