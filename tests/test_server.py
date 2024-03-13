import unittest
from threading import Thread
from time import sleep
from rte import Server, Task, Result
from .stubs import wait_for_next_id


class ServerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.server = Server(task_timeout=0.1)

    def tearDown(self) -> None:
        self.server.stop()


class TestEmptyServer(ServerTestCase):
    "Test the server when it has no tasks or results."

    def test_no_result(self) -> None:
        self.assertIsNone(self.server.get_results([0])[0])

    def test_no_results(self) -> None:
        self.assertEqual([None] * 3, self.server.get_results([0, 1, 2]))

    def test_no_canceled_task(self) -> None:
        self.assertFalse(self.server.is_task_canceled(0))


class TestServer(ServerTestCase):
    def test_release_waiting_workers(self) -> None:
        thread = Thread(target=self.server.get_task)
        thread.start()

        self.server.release_waiting_workers()
        thread.join()

    def test_get_next_id(self) -> None:
        thread = Thread(target=self.server.get_task)
        thread.start()

        self.assertEqual(0, wait_for_next_id(self.server))

        self.server.add_task(Task(0, b"task"))
        thread.join()

    def test_can_get_added_task(self) -> None:
        task = Task(0, b"task")
        self.server.add_task(task)
        self.assertEqual(task, self.server.get_task())

    def test_can_get_added_result(self) -> None:
        result = Result(0, True, b"result")
        self.server.set_result(result)
        self.assertEqual(result, self.server.get_results([0])[0])

    def test_cancel_task(self) -> None:
        self.server.add_task(Task(0, b"task"))
        self.server.cancel_task(0)
        self.assertTrue(self.server.is_task_canceled(0))

    def test_get_failed_result(self) -> None:
        result = Result(0, False, b"error")
        self.server.set_result(result)
        self.assertEqual(result, self.server.get_results([0])[0])

    def test_time_out(self) -> None:
        self.server.add_task(Task(0, b"task"))
        self.server.get_task()

        sleep(0.2)  # Wait for the task to time out
        result = self.server.get_results([0])[0]

        self.assertIsNotNone(result)
        if result is not None:
            self.assertFalse(result.success)


# Integration Server Client Worker
# 1 - 1
# test successfull task
# test failing task
# test long-running task
# test dying worker
# test task cancel
# test many tasks
# n - n
# test mayhem
