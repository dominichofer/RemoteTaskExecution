import unittest
import time
from threading import Event
from rte.heartbeat import Heart, Heartbeat, HeartbeatMonitor, MultiHeartbeatMonitor


class TestHeart(unittest.TestCase):
    def setUp(self) -> None:
        self.beats = 0

        def on_beat():
            self.beats += 1

        self.heart = Heart(period=0.05, on_beat=on_beat)

    def tearDown(self) -> None:
        self.heart.stop()

    def test_heart_beats(self):
        time.sleep(0.1)
        self.assertGreater(self.beats, 0)

    def test_stopped_heart_does_not_beat(self):
        self.heart.stop()
        time.sleep(0.1)
        beats = self.beats
        time.sleep(0.1)
        self.assertEqual(self.beats, beats)


class TestHeartbeat(unittest.TestCase):
    def test_heartbeat_is_alive(self):
        heartbeat = Heartbeat(threshold=0.1)
        self.assertTrue(heartbeat.is_alive())
        time.sleep(0.07)  # Before the threshold
        self.assertTrue(heartbeat.is_alive())
        time.sleep(0.07)  # After the threshold
        self.assertFalse(heartbeat.is_alive())

    def test_beats_keep_heartbeat_alive(self):
        heartbeat = Heartbeat(threshold=0.11)
        time.sleep(0.07)  # Less than the threshold
        self.assertTrue(heartbeat.is_alive())

        heartbeat.beat()
        time.sleep(0.07)  # More than the threshold

        self.assertTrue(heartbeat.is_alive())


class TestHeartbeatMonitor(unittest.TestCase):
    def setUp(self) -> None:
        self.death = Event()

        def on_death():
            self.death.set()

        self.monitor = HeartbeatMonitor(threshold=0.1, on_death=on_death)

    def tearDown(self) -> None:
        self.monitor.stop()

    def test_dead_heart_dies(self):
        time.sleep(0.2)  # Above the threshold
        self.assertTrue(self.death.is_set())
        self.assertFalse(self.monitor.is_alive())

    def test_beating_heart_is_alive(self):
        time.sleep(0.07)  # Below the threshold
        self.monitor.beat()
        time.sleep(0.07)  # Above the threshold
        self.assertFalse(self.death.is_set())
        self.assertTrue(self.monitor.is_alive())


class TestMultiHeartbeatMonitor(unittest.TestCase):
    def setUp(self) -> None:
        self.dead_ids: list[int] = []

        def on_death(heart_id):
            self.dead_ids.append(heart_id)

        self.monitor = MultiHeartbeatMonitor(threshold=0.1, on_death=on_death)

    def tearDown(self) -> None:
        self.monitor.stop()

    def test_dead_hearts_die(self):
        self.monitor.add(1)
        self.monitor.add(2)
        time.sleep(0.07)  # Below the thresholds

        # Both are alive
        self.assertTrue(not self.dead_ids)
        self.assertTrue(self.monitor.is_alive(1))
        self.assertTrue(self.monitor.is_alive(2))

        self.monitor.beat(1)
        # 2 doesn't beat
        time.sleep(0.07)  # Above the thresholds

        # 2 is dead
        self.assertTrue(self.dead_ids == [2])
        self.assertTrue(self.monitor.is_alive(1))
        self.assertFalse(self.monitor.is_alive(2))


# Integration tests
class TestHeartBeatHeart(unittest.TestCase):
    def setUp(self) -> None:
        self.heartbeat = Heartbeat(threshold=0.1)
        self.heart = Heart(period=0.05, on_beat=self.heartbeat.beat)

    def tearDown(self) -> None:
        self.heart.stop()

    def test_beating_heart_has_heartbeat(self):
        time.sleep(0.2)
        self.assertTrue(self.heartbeat.is_alive())

    def test_dead_heart_kills_heartbeat(self):
        time.sleep(0.2)
        self.assertTrue(self.heartbeat.is_alive())

        self.heart.stop()
        time.sleep(0.2)

        self.assertFalse(self.heartbeat.is_alive())


# Integration tests
class TestHeartBeatMonitorHeart(unittest.TestCase):
    def setUp(self) -> None:
        self.monitor = HeartbeatMonitor(threshold=0.1)
        self.heart = Heart(period=0.05, on_beat=self.monitor.beat)

    def tearDown(self) -> None:
        self.heart.stop()
        self.monitor.stop()

    def test_beating_heart_keeps_monitor_alive(self):
        time.sleep(0.2)
        self.assertTrue(self.monitor.is_alive())

    def test_dead_heart_kills_monitor(self):
        self.heart.stop()
        time.sleep(0.2)

        self.assertFalse(self.monitor.is_alive())


# Integration tests
class TestMultiHeartBeatMonitorHeart(unittest.TestCase):
    def setUp(self) -> None:
        self.dead_ids: list[int] = []

        def on_death(heart_id):
            self.dead_ids.append(heart_id)

        self.monitor = MultiHeartbeatMonitor(threshold=0.1, on_death=on_death)
        self.heart1 = Heart(period=0.05, on_beat=lambda: self.monitor.beat(1))
        self.heart2 = Heart(period=0.06, on_beat=lambda: self.monitor.beat(2))
        self.monitor.add(1)
        self.monitor.add(2)

    def tearDown(self) -> None:
        self.heart1.stop()
        self.heart2.stop()
        self.monitor.stop()

    def test_beating_heart_keeps_monitor_alive(self):
        time.sleep(0.2)  # Above the thresholds
        self.assertTrue(self.monitor.is_alive(1))
        self.assertTrue(self.monitor.is_alive(2))

    def test_dead_hearts_die(self):
        time.sleep(0.2)  # Above the thresholds

        self.heart2.stop()
        time.sleep(0.2)  # Above the thresholds

        self.assertEqual(self.dead_ids, [2])
        self.assertTrue(self.monitor.is_alive(1))
        self.assertFalse(self.monitor.is_alive(2))


if __name__ == "__main__":
    unittest.main(verbosity=2)
