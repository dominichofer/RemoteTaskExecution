import unittest
from rte import WorkerInterface, Task, Result
from .stubs import TrivialWorker, LongRunningWorker, RaisingWorker, CancellableWorker


class FakeServer(WorkerInterface):
    def __init__(self) -> None:
        self.result: Result
        self.refreshs = 0
        self.cancel = False

    def get_task(self) -> Task | None:
        return Task(0, b"task")

    def set_result(self, result: Result) -> None:
        self.result = result

    def is_task_canceled(self, task_id: int) -> bool:
        self.refreshs += 1
        return self.cancel


class TestWorker(unittest.TestCase):
    def setUp(self) -> None:
        self.server = FakeServer()

    def test_short_task(self) -> None:
        worker = TrivialWorker(self.server, 0.05)
        worker.run(1)
        self.assertEqual(self.server.result.data, b"task")

    def test_long_task_refreshes(self) -> None:
        worker = LongRunningWorker(self.server, 0.05)
        worker.run(1)
        self.assertEqual(self.server.result.data, b"task")
        self.assertGreater(self.server.refreshs, 0)

    def test_catches_raising_task(self) -> None:
        worker = RaisingWorker(self.server, 0.05)
        worker.run(1)
        self.assertFalse(self.server.result.success)

    def test_canceled_task(self) -> None:
        self.server.cancel = True
        worker = CancellableWorker(self.server, 0.05)
        worker.run(1)
        self.assertFalse(self.server.result.success)
