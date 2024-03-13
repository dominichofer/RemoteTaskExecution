import time
from threading import Event, Lock, Thread


class Heart:
    "Thread-safe beating heart."

    def __init__(self, period: float, on_beat, *args, **kwargs) -> None:
        self._period = period
        self._on_beat = on_beat
        self._stop_event = Event()
        self._thread = Thread(target=self._beat, args=args, kwargs=kwargs)
        self._thread.start()

    def _beat(self, *args, **kwargs) -> None:
        while not self._stop_event.wait(self._period):
            self._on_beat(*args, **kwargs)

    def stop(self) -> None:
        self._stop_event.set()

    def join(self) -> None:
        self._thread.join()


class Heartbeat:
    "Thread-safe heartbeat."

    def __init__(self, threshold: float) -> None:
        self._threshold = threshold
        self._lock = Lock()
        self._last_beat = time.time()

    def beat(self) -> None:
        with self._lock:
            self._last_beat = time.time()

    def is_alive(self) -> bool:
        with self._lock:
            return time.time() - self._last_beat < self._threshold


class HeartbeatMonitor:
    "Thread-safe heartbeat monitor."

    def __init__(self, threshold: float, on_death=lambda: None) -> None:
        self._heartbeat = Heartbeat(threshold)
        self._period = threshold / 2
        self._on_death = on_death
        self._stop_event = Event()
        self._thread = Thread(target=self._check_heartbeat)
        self._thread.start()

    def _check_heartbeat(self) -> None:
        while not self._stop_event.wait(self._period):
            if not self._heartbeat.is_alive():
                self._on_death()

    def beat(self) -> None:
        self._heartbeat.beat()

    def is_alive(self) -> bool:
        return self._heartbeat.is_alive()

    def stop(self) -> None:
        self._stop_event.set()

    def join(self) -> None:
        self._thread.join()


class MultiHeartbeatMonitor:
    "Thread-safe multi-heartbeat monitor."

    def __init__(self, threshold: float, on_death=lambda _: None) -> None:
        self._threshold = threshold
        self._period = threshold / 2
        self._on_death = on_death
        self._stop_event = Event()
        self._lock = Lock()  # Protects the heartbeats
        self._heartbeats: dict[int, Heartbeat] = {}
        self._thread = Thread(target=self._check_heartbeats)
        self._thread.start()

    def _check_heartbeats(self) -> None:
        while not self._stop_event.wait(self._period):
            with self._lock:
                for heart_id, heartbeat in list(self._heartbeats.items()):
                    if not heartbeat.is_alive():
                        self._heartbeats.pop(heart_id, None)
                        self._on_death(heart_id)

    def add(self, heart_id: int) -> None:
        with self._lock:
            self._heartbeats[heart_id] = Heartbeat(self._threshold)

    def remove(self, heart_id: int) -> None:
        with self._lock:
            self._heartbeats.pop(heart_id, None)

    def beat(self, heart_id: int) -> None:
        with self._lock:
            if heart_id in self._heartbeats:
                self._heartbeats[heart_id].beat()

    def is_alive(self, heart_id: int) -> bool:
        with self._lock:
            if heart_id in self._heartbeats:
                return self._heartbeats[heart_id].is_alive()
            return False

    def stop(self) -> None:
        self._stop_event.set()

    def join(self) -> None:
        self._thread.join()
