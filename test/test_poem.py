import unittest

from ds import poem


class TestPoem(unittest.TestCase):
    def setUp(self):
        self.poem = [
            "國破山河在，城春草木深。",
            "感時花濺淚，恨別鳥驚心。",
            "烽火連三月，家書抵萬金。",
            "白頭搔更短，渾欲不勝簪。"
        ]
        self.prons = {
            '深': [{'GY Rhyme': '侵'}, {'GY Rhyme': '沁'}],
            '心': [{'GY Rhyme': '侵'}],
            '金': [{'GY Rhyme': '侵'}],
            '簪': [{'GY Rhyme': '侵'}, {'GY Rhyme': '覃'}],
        }

    def test_poem(self):
        p = poem.Poem(paragraphs=self.poem, author='杜甫', title='春望')
        self.assertEquals(self.poem, p['paragraphs'])
        self.assertEquals('杜甫', p['author'])
        self.assertEquals('春望', p['title'])

    def test_get_rhymes(self):
        p = poem.Poem(paragraphs=self.poem)
        self.assertEquals(['深', '心', '金', '簪'], p.get_rhymes())

    def test_get_rhyme_categories(self):
        p = poem.Poem(paragraphs=self.poem)
        self.assertEquals(['侵', '侵', '侵', '侵'],
                          p.get_rhyme_categories(self.prons))

    def test_find_rhyme_pairs(self):
        p = poem.Poem(paragraphs=['風雅不墜地，五言始君先。',  # 先
                                  '希微嘉會章，杳冥河梁篇。',  # 仙
                                  '理蔓語無枝，言一意則千。',  # 先
                                  '往來更後人，澆蕩醨前源。',  # 元
                                  ])
        prons = {
            '先': [{'GY Rhyme': '先'}],
            '篇': [{'GY Rhyme': '仙'}],
            '千': [{'GY Rhyme': '先'}],
            '源': [{'GY Rhyme': '元'}],
        }

        self.assertEquals({('元', '先'), },
                          p.find_rhyme_pairs(prons, ('仙先文', '元')))
