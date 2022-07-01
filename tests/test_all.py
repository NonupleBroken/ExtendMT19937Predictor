import unittest
import os
import random
import sys
from extend_mt19937_predictor import ExtendMT19937Predictor


class PythonStdlibTest(unittest.TestCase):
    def test_twist(self):
        random.seed(os.urandom(32))

        predictor = ExtendMT19937Predictor()

        for _ in range(624):
            predictor.setrandbits(random.getrandbits(32), 32)

        for _ in range(1024):
            origin = predictor._mt[::]
            predictor._twist()
            predictor._untwist()
            untwist = predictor._mt[::]
            self.assertEqual(origin, untwist)

    def test_predict(self):
        random.seed(os.urandom(32))

        predictor = ExtendMT19937Predictor()

        for _ in range(624):
            predictor.setrandbits(random.getrandbits(32), 32)

        for _ in range(1024):
            self.assertEqual(predictor.predict_getrandbits(32), random.getrandbits(32))

        predictor = ExtendMT19937Predictor()

        for _ in range(156):
            predictor.setrandbits(random.getrandbits(128), 128)

        for _ in range(1024):
            self.assertEqual(predictor.predict_getrandbits(256), random.getrandbits(256))
        for _ in range(1024):
            self.assertEqual(predictor.predict_getrandbits(80), random.getrandbits(80))
        for _ in range(1024):
            self.assertEqual(predictor.predict_getrandbits(1), random.getrandbits(1))

    def test_backtrack(self):
        random.seed(os.urandom(32))

        numbers1 = [random.getrandbits(70) for _ in range(1024)]
        numbers2 = [random.getrandbits(128) for _ in range(1024)]

        predictor = ExtendMT19937Predictor()

        for _ in range(78):
            predictor.setrandbits(random.getrandbits(256), 256)

        _ = [predictor.backtrack_getrandbits(256) for _ in range(78)]

        for number in numbers2[::-1]:
            self.assertEqual(predictor.backtrack_getrandbits(128), number)
        for number in numbers1[::-1]:
            self.assertEqual(predictor.backtrack_getrandbits(70), number)

        for number in numbers1:
            self.assertEqual(predictor.predict_getrandbits(70), number)
        for number in numbers2:
            self.assertEqual(predictor.predict_getrandbits(128), number)

    def test_check(self):
        random.seed(os.urandom(32))

        predictor = ExtendMT19937Predictor()

        for _ in range(1024):
            predictor.setrandbits(random.getrandbits(32), 32)
        for _ in range(1024):
            predictor.setrandbits(random.getrandbits(512), 512)

        for _ in range(1024):
            self.assertEqual(predictor.predict_getrandbits(256), random.getrandbits(256))

        predictor = ExtendMT19937Predictor(check=False)

        for _ in range(1024):
            predictor.setrandbits(random.getrandbits(32), 32)
        for _ in range(1024):
            predictor.setrandbits(random.getrandbits(512), 512)

        for _ in range(1024):
            self.assertEqual(predictor.predict_getrandbits(256), random.getrandbits(256))

    def test_other_functions(self):
        random.seed(os.urandom(32))

        numbers1 = [random.random() for _ in range(1024)]
        numbers2 = [random.uniform(1, 10) for _ in range(1024)]

        predictor = ExtendMT19937Predictor()

        for _ in range(1024):
            predictor.setrandbits(random.getrandbits(32), 32)

        _ = [predictor.backtrack_getrandbits(32) for _ in range(1024)]

        for number in numbers2[::-1]:
            self.assertEqual(predictor.backtrack_uniform(1, 10), number)
        for number in numbers1[::-1]:
            self.assertEqual(predictor.backtrack_random(), number)

        for number in numbers1:
            self.assertEqual(predictor.predict_random(), number)
        for number in numbers2:
            self.assertEqual(predictor.predict_uniform(1, 10), number)

        _ = [predictor.predict_getrandbits(32) for _ in range(1024)]

        for _ in range(1024):
            self.assertEqual(predictor.predict_random(), random.random())
        for i in range(1024):
            self.assertEqual(predictor.predict_uniform(0, i),  random.uniform(0, i))
        for i in range(1024):
            self.assertEqual(predictor.predict_randint(0, 2 ** i), random.randint(0, 2 ** i))
        for i in range(1024):
            self.assertEqual(predictor.predict_randrange(0, 2 ** i), random.randrange(0, 2 ** i))

    def test_randbytes(self):
        if sys.version_info[0] == 2:
            return

        random.seed(os.urandom(32))

        numbers = [random.randbytes(1024) for _ in range(1024)]

        predictor = ExtendMT19937Predictor()

        for _ in range(1024):
            predictor.setrandbits(random.getrandbits(32), 32)

        _ = [predictor.backtrack_getrandbits(32) for _ in range(1024)]

        for number in numbers[::-1]:
            self.assertEqual(predictor.backtrack_randbytes(1024), number)

        for number in numbers:
            self.assertEqual(predictor.predict_randbytes(1024), number)

        _ = [predictor.predict_getrandbits(32) for _ in range(1024)]

        for _ in range(1024):
            self.assertEqual(predictor.predict_randbytes(512), random.randbytes(512))
