import os
import tempfile
import unittest

from ds import authors

authors.AUTHORS = {'qts': 'test/authors.tang.json'}


class TestAuthors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.NamedTemporaryFile(delete=False) as g:
            cls.cache_file = g.name
        authors.AUTHOR_CACHE = g.name
        authors.cache_authors('qts')

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.cache_file)

    def test_get_alternative_names(self):
        auths = authors.get_authors('qts')
        self.assertEquals('歐陽詹', auths[0]['name'])
        self.assertEquals({'行周'}, authors.get_zis(auths[0]))

        self.assertEquals('韓愈', auths[1]['name'])
        self.assertEquals({'文', '退之'}, authors.get_zis(auths[1]))
        
    def test_load_authors(self):
        auths = authors.load_authors('qts')
        self.assertEquals(1, len(auths['歐陽詹']))

    def test_keep_unambiguous(self):
        auths = authors.load_authors('qts')
        self.assertEquals(3, len(auths))
        # Wang Rong is in the list, but is an ambiguous name
        self.assertIn('王融', auths)
        self.assertLess(1, len(auths['王融']))

        auths = authors.keep_only_unambiguous(auths)
        # after removal of ambiguous names, he's not in the list any more
        self.assertEquals(2, len(auths))
        self.assertNotIn('王融', auths)
