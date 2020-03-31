import os
import tempfile
import unittest

from ds import authors

authors.AUTHORS = {'qts': 'test/authors.tang.json'}


class TestAuthors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_cache_file = authors.AUTHOR_CACHE
        with tempfile.NamedTemporaryFile(delete=False) as g:
            cls.cache_file = g.name
        authors.AUTHOR_CACHE = g.name
        authors.cache_authors('qts')

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.cache_file)
        authors.AUTHOR_CACHE = cls.original_cache_file

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

    def test_filter_by_area(self):
        auths = authors.load_authors('qts')
        auths = [auths['歐陽詹'][0], auths['韓愈'][0]]

        north = authors.filter_by_area(authors.NORTH, auths)
        south = authors.filter_by_area(authors.SOUTH, auths)

        self.assertEquals(1, len(north))
        self.assertEquals(1, len(south))
        self.assertEquals('韓愈', north[0]['c_name_chn'])
        self.assertEquals('歐陽詹', south[0]['c_name_chn'])

    def test_filter_by_province(self):
        auths = authors.load_authors('qts')
        auths = [auths['歐陽詹'][0], auths['韓愈'][0]]

        fujian = authors.filter_by_area('福建', auths)
        shaanxi = authors.filter_by_area('陝西', auths)

        self.assertEquals(1, len(fujian))
        self.assertEquals(1, len(shaanxi))
        self.assertEquals('韓愈', shaanxi[0]['c_name_chn'])
        self.assertEquals('歐陽詹', fujian[0]['c_name_chn'])

    def test_filter_by_time_range(self):
        auths = authors.load_authors('qts')
        self.assertEquals(802, auths['歐陽詹'][0]['c_index_year'])
        self.assertEquals(825, auths['韓愈'][0]['c_index_year'])

        auths = [auths['歐陽詹'][0], auths['韓愈'][0]]

        early = authors.filter_by_time_range(range(618, 810), auths)
        late = authors.filter_by_time_range(range(810, 907), auths)

        self.assertEquals(1, len(early))
        self.assertEquals(1, len(late))
        self.assertEquals('韓愈', late[0]['c_name_chn'])
        self.assertEquals('歐陽詹', early[0]['c_name_chn'])
