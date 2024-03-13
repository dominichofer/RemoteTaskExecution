import unittest
from time import sleep
from threading import Thread
from rte import Server, Result
from .stubs import TrivialClient


class TestServerClient(unittest.TestCase):
    def setUp(self) -> None:
        self.server = Server(task_timeout=0.1)
        self.client = TrivialClient(self.server, 0.05)
        self.thread = Thread(target=self.client.run)
        self.thread.start()

    def tearDown(self) -> None:
        self.server.stop()

    def test_successfull_task(self) -> None:
        task = self.server.get_task()
        if task is None:
            self.fail("No task available")
        result = Result(task.id, True, b"result")
        self.server.set_result(result)
        self.thread.join()

        self.assertEqual(self.client.results[0], result)

    def test_long_running_task(self) -> None:
        task = self.server.get_task()
        if task is None:
            self.fail("No task available")

        for _ in range(5):
            sleep(0.05)
            self.server.is_task_canceled(task.id)

        result = Result(task.id, True, b"result")
        self.server.set_result(result)
        self.thread.join()

        self.assertEqual(self.client.results[0], result)

    def test_task_time_out(self) -> None:
        task = self.server.get_task()
        if task is None:
            self.fail("No task available")

        sleep(0.3)  # Wait for the task to time out
        self.thread.join()

        if self.client.results[0] is None:
            self.fail("No result available")
        self.assertFalse(self.client.results[0].success)
