import unittest

from ds import gis


class TestGis(unittest.TestCase):
    def test_get_province(self):
        for y, x, province in [(24.907, 118.587, '福建'),  # Quanzhou
                               (31.228, 121.474, '上海'),  # Shanghai
                               (34.265, 108.954, '陝西'),  # Xi'an
                               (30.25, 120.166, '浙江'),  # Hangzhou
                               ]:
            self.assertEquals(province, gis.get_province(x=x, y=y))

    def test_get_province_prefecture(self):
        for y, x, province in [(24.966, 118.383, '泉州市'),  # Nan'an
                               ]:
            self.assertEquals(province, gis.get_province(x=x, y=y,
                                                         type='prefecture'))
