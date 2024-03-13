import unittest
from time import sleep
from threading import Thread
from typing import Optional
from rte import Server, Task, Result
from .stubs import (
    TrivialWorker,
    LongRunningWorker,
    RaisingWorker,
    CancellableWorker,
    DyingWorker,
    wait_for_next_id,
)


class TestServerWorker(unittest.TestCase):
    def setUp(self) -> None:
        self.server = Server(task_timeout=0.1)

    def tearDown(self) -> None:
        self.server.stop()

    def test_full_workflow(self) -> None:
        worker = TrivialWorker(self.server, 0.05)
        worker_thread = Thread(target=worker.run, args=(1,))
        worker_thread.start()

        task_id = wait_for_next_id(self.server)
        if task_id is None:
            self.fail("No task id available")
        self.server.add_task(Task(task_id, b"test"))
        worker_thread.join()
        result = self.server.get_results([task_id])[0]

        if result is None:
            self.fail("No result available")
        self.assertEqual(result.data, b"test")

    def test_successfull_task(self) -> None:
        worker = TrivialWorker(self.server, 0.05)

        self.server.add_task(Task(0, b"test"))
        worker.run(1)
        result = self.server.get_results([0])[0]

        if result is None:
            self.fail("No result available")
        self.assertEqual(result.data, b"test")

    def test_long_running_task(self) -> None:
        "Tests that long running tasks are not timed out."
        worker = LongRunningWorker(self.server, 0.05)

        self.server.add_task(Task(0, b"test"))
        worker.run(1)
        result = self.server.get_results([0])[0]

        if result is None:
            self.fail("No result available")
        self.assertEqual(result.data, b"test")

    def test_raising_task(self) -> None:
        worker = RaisingWorker(self.server, 0.05)

        self.server.add_task(Task(0, b"test"))
        worker.run(1)
        result = self.server.get_results([0])[0]

        if result is None:
            self.fail("No result available")
        self.assertFalse(result.success)

    def test_cancellable_task_without_cancel(self) -> None:
        worker = CancellableWorker(self.server, 0.05)

        self.server.add_task(Task(0, b"test"))
        worker.run(1)
        result = self.server.get_results([0])[0]

        if result is None:
            self.fail("No result available")
        self.assertEqual(result.data, b"test")

    def test_cancellable_task_with_cancel(self) -> None:
        worker = CancellableWorker(self.server, 0.05)

        self.server.add_task(Task(0, b"test"))
        self.server.cancel_task(0)
        worker.run(1)
        result = self.server.get_results([0])[0]

        if result is None:
            self.fail("No result available")
        self.assertFalse(result.success)

    def test_dying_worker(self) -> None:
        worker = DyingWorker(self.server, 0.05)
        worker_thread = Thread(target=worker.run, args=(1,))
        worker_thread.start()

        self.server.add_task(Task(0, b"test"))
        sleep(0.2)  # Wait for the server to timeout the task
        result = self.server.get_results([0])[0]

        if result is None:
            self.fail("No result available")
        self.assertFalse(result.success)

        worker_thread.join()

    def test_many_workers(self) -> None:
        workers = [
            TrivialWorker(self.server, 0.05),
            LongRunningWorker(self.server, 0.05),
            RaisingWorker(self.server, 0.05),
        ]
        tasks_per_worker = 10
        num_tasks = len(workers) * tasks_per_worker
        worker_threads = [Thread(target=worker.run, args=(tasks_per_worker,)) for worker in workers]
        for t in worker_threads:
            t.start()

        for _ in range(num_tasks):
            task_id = wait_for_next_id(self.server)
            if task_id is None:
                self.fail("No task id available")
            self.server.add_task(Task(task_id, b"test"))

        results: list[Optional[Result]] = [None] * num_tasks
        while not all(results):
            for tid in range(num_tasks):
                if results[tid] is None:
                    results[tid] = self.server.get_results([tid])[0]

        successfull = [x for x in results if x and x.success]
        unsuccessful = [x for x in results if x and not x.success]
        self.assertEqual(len(successfull), 2 * tasks_per_worker)
        self.assertEqual(len(unsuccessful), 1 * tasks_per_worker)

        for t in worker_threads:
            t.join()
