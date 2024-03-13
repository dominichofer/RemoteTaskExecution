import unittest
from unittest.mock import MagicMock, patch
from threading import Thread
from rte import Server, GrpcServer, RemoteServer, Task, Result
from .stubs import ServerStub, TrivialClient, TrivialWorker


PORT: int = 50051


class TestGrpc(unittest.TestCase):
    def setUp(self) -> None:
        self.test_server = ServerStub()
        self.grpc_server = GrpcServer(self.test_server, PORT)
        self.grpc_server.start()
        self.server = RemoteServer(f"localhost:{PORT}")

    def tearDown(self) -> None:
        self.grpc_server.stop(0)

    def test_get_next_id(self):
        task_id = 12  # arbitrary
        self.test_server.get_next_id = MagicMock(return_value=task_id)
        result = self.server.get_next_id()
        self.assertEqual(result, task_id)

    def test_return_id(self):
        task_id = 13  # arbitrary
        with patch.object(self.test_server, "return_id") as mock_return_id:
            self.server.return_id(task_id)
            mock_return_id.assert_called_once_with(task_id)

    def test_add_task(self):
        task = Task(14, b"task")  # arbitrary
        with patch.object(self.test_server, "add_task") as mock_add_task:
            self.server.add_task(task)
            mock_add_task.assert_called_once_with(task)

    def test_get_task(self):
        task = Task(15, b"task")  # arbitrary
        self.test_server.get_task = MagicMock(return_value=task)
        result = self.server.get_task()
        self.assertEqual(result, task)

    def test_set_result(self):
        result = Result(16, True, b"result")  # arbitrary
        with patch.object(self.test_server, "set_result") as mock_set_result:
            self.server.set_result(result)
            mock_set_result.assert_called_once_with(result)

    def test_get_results(self):
        task_ids = [17, 18]  # arbitrary
        results = [Result(tid, True, b"result") for tid in task_ids]
        self.test_server.get_results = MagicMock(return_value=results)
        result = self.server.get_results(task_ids)
        self.assertEqual(result, results)

    def test_cancel_task(self):
        task_id = 19  # arbitrary
        with patch.object(self.test_server, "cancel_task") as mock_cancel_task:
            self.server.cancel_task(task_id)
            mock_cancel_task.assert_called_once_with(task_id)

    def test_is_task_canceled(self):
        for value in [True, False]:
            self.test_server.is_task_canceled = MagicMock(return_value=value)
            result = self.server.is_task_canceled(20)
            self.assertEqual(result, value)


class TestGrpcSystem(unittest.TestCase):
    def setUp(self) -> None:
        self.remote_server = Server(task_timeout=0.02)
        self.rpc_server = GrpcServer(self.remote_server, port=PORT)
        self.rpc_server.start()
        self.server = RemoteServer(f"localhost:{PORT}")

    def tearDown(self) -> None:
        self.rpc_server.stop(0)

    def test_one_worker_one_client(self) -> None:
        client = TrivialClient(self.remote_server, 0.01)
        client.tasks = [b"task" for _ in range(100)]
        worker = TrivialWorker(self.remote_server, 0.01)

        worker_thread = Thread(target=worker.run)
        worker_thread.start()

        client.run()
        self.server.release_waiting_workers()
        self.remote_server.stop()
        worker_thread.join()

        self.assertEqual(len(client.results), 100)
        for result in client.results:
            if result is None:
                self.fail("Result is None")
            self.assertEqual(result.success, True)
            self.assertEqual(result.data, b"task")

    def test_many_workers_many_clients(self) -> None:
        clients = [TrivialClient(self.remote_server, 0.01) for _ in range(10)]
        for client in clients:
            client.tasks = [b"task" for _ in range(10)]
        workers = [TrivialWorker(self.remote_server, 0.01) for _ in range(10)]

        worker_threads = [Thread(target=worker.run) for worker in workers]
        for thread in worker_threads:
            thread.start()

        client_threads = [Thread(target=client.run) for client in clients]
        for thread in client_threads:
            thread.start()

        for thread in client_threads:
            thread.join()

        self.server.release_waiting_workers()
        self.remote_server.stop()
        for thread in worker_threads:
            thread.join()

        for client in clients:
            self.assertEqual(len(client.results), 10)
            for result in client.results:
                if result is None:
                    self.fail("Result is None")
                self.assertEqual(result.success, True)
                self.assertEqual(result.data, b"task")
