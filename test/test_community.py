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


class TestGetTopMissing(unittest.TestCase):
    def test_get_top_missing(self):
        comm_a = Counter({'庚': 72, '青': 69, '清': 52, '耕': 40, '映': 12,
                          '徑': 9, '勁': 7, '迥': 6})
        comm_b = Counter({'青': 12, '徑': 3, '迥': 2, '清': 2, '靜': 1, '支': 1,
                          '至': 1})
        # the last char of A that is in B is 迥, so we consider the entire A
        # of which several characters are missing in B
        self.assertEquals({'勁', '映', '耕', '庚'},
                          community.get_top_missing(comm_a, comm_b))
        # the last char of B that is in A is 清, so we consider up the first 4
        # of which no character is missing in A
        self.assertEquals(set(),
                          community.get_top_missing(comm_b, comm_a))
