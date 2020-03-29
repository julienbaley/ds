import unittest
from collections import Counter

from ds import community


class TestGetCommunityRhymeCategories(unittest.TestCase):
    def test_get_community_rhyme_categories(self):
        prons = {
            '深': [{'GY Rhyme': '侵'}, {'GY Rhyme': '沁'}],
            '心': [{'GY Rhyme': '侵'}],
            '金': [{'GY Rhyme': '侵'}],
            '簪': [{'GY Rhyme': '侵'}, {'GY Rhyme': '覃'}],

            '沒': [{'GY Rhyme': '沒'}],
            '發': [{'GY Rhyme': '月'}],
            '室': [{'GY Rhyme': '質'}],
            '骨': [{'GY Rhyme': '沒'}],
            '佛': [{'GY Rhyme': '物'}],
            '別': [{'GY Rhyme': '薛'}, {'GY Rhyme': '薛'}],
            '曰': [{'GY Rhyme': '月'}],
        }
        communities = [{'深', '心', '金', '簪'},
                       {'沒', '發', '室', '骨', '佛', '別', '曰'}]

        self.assertEquals(
            Counter({'侵': 4, '沁': 1, '覃': 1}),
            community.get_community_rhyme_categories(communities[0], prons))
        self.assertEquals(
            Counter({'月': 2, '沒': 2, '質': 1, '薛': 1, '物': 1}),
            community.get_community_rhyme_categories(communities[1], prons))


class TestAlignCommunities(unittest.TestCase):
    def test_align_communities(self):
        corpus_a_comms = [Counter({'侵': 4, '沁': 1, '覃': 1}),
                          Counter({'沒': 2, '質': 1, '薛': 1}),
                          Counter(),  # empty communities are ignored
                          ]

        corpus_b_comms = [Counter({'侵': 4}),
                          Counter({'月': 2, '沒': 2, '質': 1, '薛': 1, '物': 1}),
                          Counter()]

        self.assertEquals(
            [(Counter({'侵': 4, '沁': 1, '覃': 1}),
              Counter({'侵': 4})),

             (Counter({'沒': 2, '質': 1, '薛': 1}),
              Counter({'月': 2, '沒': 2, '質': 1, '薛': 1, '物': 1}))],
            community.align_communities(corpus_a_comms, corpus_b_comms))

    def test_resolution_of_ambiguities(self):
        corpus_a_comms = [Counter({'侵': 4}),
                          Counter({'侵': 4, '沁': 1, '覃': 1}),
                          ]

        corpus_b_comms = [Counter({'侵': 4, '沁': 1})]

        self.assertEquals(
            [(Counter({'侵': 4, '沁': 1, '覃': 1}),
              Counter({'侵': 4, '沁': 1}))],
            community.align_communities(corpus_a_comms, corpus_b_comms))
