import unittest
from typing import Optional
from rte import ClientInterface, BatchClient, Task, Result
from .stubs import TrivialClient


class ServerStub(ClientInterface):
    def __init__(self, next_ids: list[Optional[int]], results: list[Optional[Result]]) -> None:
        self.next_ids = next_ids
        self.results = results
        self.tasks: list[Task] = []
        self.returned_ids: list[int] = []
        self.canceled_ids: list[int] = []

    def get_next_id(self) -> Optional[int]:
        if self.next_ids:
            return self.next_ids.pop(0)
        return None

    def return_id(self, task_id: int) -> None:
        self.returned_ids.append(task_id)

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def get_results(self, task_ids: list[int]) -> list[Optional[Result]]:
        return [self.results.pop(0) if self.results else None for _ in task_ids]

    def cancel_task(self, task_id: int) -> None:
        self.canceled_ids.append(task_id)


class TestClient(unittest.TestCase):
    def test_successfull_workflow(self) -> None:
        server = ServerStub([13], [Result(13, True, b"result")])
        client = TrivialClient(server, 0.05)

        client.run()

        if len(client.results) < 1:
            self.fail("No result available")
        if client.results[0] is None:
            self.fail("Result is None")
        self.assertEqual(client.results[0].success, True)
        self.assertEqual(client.results[0].data, b"result")

    def test_retry_on_delayed_next_id(self) -> None:
        server = ServerStub([None, 13], [Result(13, True, b"result")])
        client = TrivialClient(server, 0.05)

        client.run()

        if len(client.results) < 1:
            self.fail("No result available")
        if client.results[0] is None:
            self.fail("Result is None")
        self.assertEqual(client.results[0].success, True)
        self.assertEqual(client.results[0].data, b"result")

    def test_retry_on_delayed_task(self) -> None:
        server = ServerStub([12, 13], [Result(13, True, b"result")])
        client = TrivialClient(server, 0.05)
        client.tasks = [None, b"task"]

        client.run()

        if len(client.results) < 1:
            self.fail("No result available")
        if client.results[0] is None:
            self.fail("Result is None")
        self.assertEqual(client.results[0].success, True)
        self.assertEqual(client.results[0].data, b"result")
        self.assertEqual(server.returned_ids, [12])


class TestBatchClient(unittest.TestCase):
    def test_successfull_task(self) -> None:
        server = ServerStub([13], [Result(13, True, b"result")])
        client = BatchClient(server, 0.05)

        results = client.solve([b"task"])

        if len(results) < 1:
            self.fail("No result available")
        if results[0] is None:
            self.fail("Result is None")
        self.assertEqual(results[0], b"result")

    def test_failed_task(self) -> None:
        server = ServerStub([13], [Result(13, False, b"")])
        client = BatchClient(server, 0.05)

        results = client.solve([b"task"])

        if len(results) < 1:
            self.fail("No result available")
        self.assertEqual(results[0], None)

    def test_retry_on_delayed_next_id(self) -> None:
        server = ServerStub([None, 13], [Result(13, True, b"result")])
        client = BatchClient(server, 0.05)

        results = client.solve([b"task"])

        if len(results) < 1:
            self.fail("No result available")
        if results[0] is None:
            self.fail("Result is None")
        self.assertEqual(results[0], b"result")
