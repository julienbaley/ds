import unittest

from ds import authors, corpus


class TestCorpus(unittest.TestCase):
    def test_get_corpus(self):
        qts = corpus.get_corpus('qts')
        self.assertTrue(all('author' in poem for poem in qts))
        self.assertTrue(all('title' in poem for poem in qts))
        self.assertTrue(all('paragraphs' in poem for poem in qts))
        self.assertGreater(len(qts), 50000)

    def test_filter_by_single_author(self):
        qts = corpus.get_corpus('qts')
        auths = authors.load_authors('qts')
        auths = [auths['歐陽詹'][0], auths['韓愈'][0]]

        oyz = corpus.filter_by_authors('歐陽詹', qts)

        self.assertTrue(poem['author'] == '歐陽詹'
                        for poem in oyz)

    def test_filter_by_multiple_string_authors(self):
        qts = corpus.get_corpus('qts')
        auths = authors.load_authors('qts')
        auths = [auths['歐陽詹'][0], auths['韓愈'][0]]

        oyz_hy = corpus.filter_by_authors({'歐陽詹', '韓愈'}, qts)

        self.assertNotEqual(0, len(oyz_hy))
        self.assertTrue(poem['author'] == '歐陽詹' or poem['author'] == '韓愈'
                        for poem in oyz_hy)

    def test_filter_by_multiple_dict_authors(self):
        qts = corpus.get_corpus('qts')
        auths = authors.load_authors('qts')
        auths = [auths['歐陽詹'][0], auths['韓愈'][0]]

        oyz_hy = corpus.filter_by_authors(auths, qts)

        self.assertNotEqual(0, len(oyz_hy))
        self.assertTrue(poem['author'] == '歐陽詹' or poem['author'] == '韓愈'
                        for poem in oyz_hy)
