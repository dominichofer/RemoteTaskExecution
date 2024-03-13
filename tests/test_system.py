import unittest
from threading import Thread
from rte import Server
from .stubs import TrivialClient, TrivialWorker


class TestSystem(unittest.TestCase):
    def test_one_worker_one_client(self) -> None:
        server = Server(0.02)
        client = TrivialClient(server, 0.01)
        client.tasks = [b"task" for _ in range(100)]
        worker = TrivialWorker(server, 0.01)

        worker_thread = Thread(target=worker.run)
        worker_thread.start()

        client.run()
        server.release_waiting_workers()
        server.stop()
        worker_thread.join()

        self.assertEqual(len(client.results), 100)
        for result in client.results:
            if result is None:
                self.fail("Result is None")
            self.assertEqual(result.success, True)
            self.assertEqual(result.data, b"task")

    def test_many_workers_one_producer(self) -> None:
        server = Server(0.02)
        client = TrivialClient(server, 0.01)
        client.tasks = [b"task" for _ in range(100)]
        workers = [TrivialWorker(server, 0.01) for _ in range(10)]

        worker_threads = [Thread(target=worker.run) for worker in workers]
        for worker_thread in worker_threads:
            worker_thread.start()

        client.run()
        server.release_waiting_workers()
        server.stop()
        for worker_thread in worker_threads:
            worker_thread.join()

        self.assertEqual(len(client.results), 100)
        for result in client.results:
            if result is None:
                self.fail("Result is None")
            self.assertEqual(result.success, True)
            self.assertEqual(result.data, b"task")

    def test_many_workers_many_producers(self) -> None:
        server = Server(0.02)
        clients = [TrivialClient(server, 0.01) for _ in range(10)]
        for client in clients:
            client.tasks = [b"task" for _ in range(10)]
        workers = [TrivialWorker(server, 0.01) for _ in range(10)]

        worker_threads = [Thread(target=worker.run) for worker in workers]
        for worker_thread in worker_threads:
            worker_thread.start()

        client_threads = [Thread(target=client.run) for client in clients]
        for client_thread in client_threads:
            client_thread.start()

        for client_thread in client_threads:
            client_thread.join()
        server.release_waiting_workers()
        server.stop()
        for worker_thread in worker_threads:
            worker_thread.join()

        for client in clients:
            self.assertEqual(len(client.results), 10)
            for result in client.results:
                if result is None:
                    self.fail("Result is None")
                self.assertEqual(result.success, True)
                self.assertEqual(result.data, b"task")
