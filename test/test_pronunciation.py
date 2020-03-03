import os
import tempfile
import unittest

from ds import pronunciation


class TestPronunciation(unittest.TestCase):
    def setUp(self):
        with tempfile.NamedTemporaryFile(delete=False) as g:
            self.cache_file = g.name
        pronunciation.CACHE_FILE = self.cache_file

    def tearDown(self):
        os.remove(self.cache_file)

    def test_query_edoc(self):
        s = '東方'
        rets = pronunciation.query_edoc(s)
        for c, ret in zip(s, rets):
            self.assertEqual(c, ret['Graph'])

    def test_get_pronunciation(self):
        s = '東方'
        rets = pronunciation.get_pronunciation(s)
        for c in s:
            self.assertEqual(c, rets[c][0]['Graph'])
