import unittest
from ustrid import ustrid


class Test(unittest.TestCase):
    def test(self):
        cache = set()
        for i in range(10000):
            r = ustrid()
            with self.subTest("Test {}".format(i)):
                n_dashes = len([x for x in r if x == "-"])
                self.assertFalse(r in cache)
                self.assertTrue(len(r) >= 38)
                self.assertEqual(5, n_dashes)
                cache.add(r)


if __name__ == '__main__':
    unittest.main()
