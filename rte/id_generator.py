from threading import Lock


class IdGenerator:
    "Thread-safe ID generator."

    def __init__(self, start_id: int = 0) -> None:
        self._lock = Lock()
        self._id = start_id

    def __call__(self) -> int:
        with self._lock:
            result = self._id
            self._id += 1
            return result
