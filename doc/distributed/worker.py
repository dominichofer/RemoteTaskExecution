from rte import Worker, RemoteServer


class ToUpperWorker(Worker):
    def execute_task(self, task: bytes) -> bytes:
        return task.upper()

    def on_cancel(self) -> None:
        pass


if __name__ == "__main__":
    server = RemoteServer("localhost:50051")

    worker = ToUpperWorker(server, refresh_time=0.5)
    worker.run()
