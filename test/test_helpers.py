import unittest

from ds import helpers


class TestWindow(unittest.TestCase):
    def test_window(self):
        self.assertEqual(['a', 'b', 'c', 'd', 'e'],
                         helpers.window('abcde', 1))
        self.assertEqual(['ab', 'bc', 'cd', 'de'],
                         helpers.window('abcde', 2))
        self.assertEqual(['abc', 'bcd', 'cde'],
                         helpers.window('abcde', 3))

    def test_window_empty(self):
        self.assertEqual([], helpers.window('', 1))

    def test_window_combination(self):
        self.assertEqual({('a', 'b'), ('b', 'c'), ('c', 'd'), ('d', 'e')},
                         helpers.window_combinations('abcde', 2))
        self.assertEqual({('a', 'b'), ('b', 'c'), ('c', 'd'), ('d', 'e'),
                          ('a', 'c'), ('a', 'd'), ('a', 'e'),
                          ('b', 'd'), ('b', 'e'),
                          ('c', 'e')
                          },
                         helpers.window_combinations('abcde', len('abcde')))


class TestHelpers(unittest.TestCase):
    def test_get_precision_vector(self):
        relevant = ['a', 'b', 'c', 'd', 'e', 'f']
        found = ['a', 'z', 'b', 'c', 'd', 'e', 'y', 'x', 'w', 'f']

        self.assertEquals([1, 1/2, 2/3, 3/4, 4/5, 5/6, 5/7, 5/8, 5/9, 6/10],
                          helpers.get_precision_vector(found, relevant))

    def test_get_precision_vector2(self):
        relevant = ['a', 'b', 'c', 'd', 'e', 'f']
        found = ['z', 'a', 'y', 'x', 'b', 'c', 'd', 'w', 'e', 'f']

        self.assertEquals([0, 1/2, 1/3, 1/4, 2/5, 3/6, 4/7, 4/8, 5/9, 6/10],
                          helpers.get_precision_vector(found, relevant))

    def test_get_average_precision(self):
        relevant = ['a', 'b', 'c', 'd', 'e', 'f']
        found = ['a', 'z', 'b', 'c', 'd', 'e', 'y', 'x', 'w', 'f']

        self.assertAlmostEqual(0.775,
                               helpers.get_average_precision(found, relevant),
                               places=3)

    def test_get_average_precision2(self):
        relevant = ['a', 'b', 'c', 'd', 'e', 'f']
        found = ['z', 'a', 'y', 'x', 'b', 'c', 'd', 'w', 'e', 'f']

        self.assertAlmostEqual(0.521,
                               helpers.get_average_precision(found, relevant),
                               places=3)
