import unittest

from ds import cbdb


class TestCbdb(unittest.TestCase):
    def test_rows2dicts(self):
        with cbdb.get_cursor() as cursor:
            cursor.execute('SELECT * FROM status_data LIMIT 10')
            dict_lst = cbdb.rows2dicts(cursor.fetchall())

        cols = set(dict_lst[0].keys())
        for dic in dict_lst:
            self.assertEquals(set(dic.keys()), cols)

    def test_query_name(self):
        ret = cbdb.rows2dicts(cbdb.query_name('歐陽詹'))
        self.assertEquals(2, len(ret))
        self.assertTrue(all(row['c_name_chn'] == '歐陽詹' for row in ret))

    def test_filter_by_alternative_names(self):
        rows = cbdb.query_name('歐陽詹')
        ret = cbdb.filter_by_alternative_name(rows, zis=['行周'])
        self.assertEqual(1, len(ret))
        self.assertEqual(757, ret[0]['c_birthyear'])

    def test_filter_by_job(self):
        rows = cbdb.query_name('歐陽詹')
        ret = cbdb.filter_by_job(rows, job='poet')
        self.assertEqual(1, len(ret))
        self.assertEqual(757, ret[0]['c_birthyear'])


class TestFilterByPeriod(unittest.TestCase):
    def test_filter_by_period(self):
        allowed_span = range(cbdb.DYNASTIES['唐'][0] - cbdb.LIFE_SPAN,
                             cbdb.DYNASTIES['唐'][-1] + cbdb.LIFE_SPAN)

        persons = cbdb.get_person('劉濟')  # no dynasty restriction
        self.assertFalse(all(p['c_index_year'] is None or
                             p['c_index_year'] in allowed_span
                             for p in persons))

        persons = cbdb.get_person('劉濟', dyn='唐')
        self.assertTrue(all(p['c_index_year'] is None or
                            p['c_index_year'] in allowed_span
                            for p in persons))
