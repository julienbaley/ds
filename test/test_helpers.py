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
