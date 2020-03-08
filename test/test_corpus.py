import unittest

from ds import corpus


class TestCorpus(unittest.TestCase):
    def test_get_corpus(self):
        qts = corpus.get_corpus('qts')
        self.assertTrue(all('author' in poem for poem in qts))
        self.assertTrue(all('title' in poem for poem in qts))
        self.assertTrue(all('paragraphs' in poem for poem in qts))
        self.assertGreater(len(qts), 50000)
