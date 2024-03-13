import unittest
from rte.id_generator import IdGenerator


class TestIdGenerator(unittest.TestCase):
    def setUp(self) -> None:
        self.id_gen = IdGenerator()

    def test_id_generator(self):
        self.assertEqual(self.id_gen(), 0)
        self.assertEqual(self.id_gen(), 1)
        self.assertEqual(self.id_gen(), 2)
