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

    def test_poem(self):
        p = poem.Poem(paragraphs=self.poem, author='杜甫', title='春望')
        self.assertEquals(self.poem, p['paragraphs'])
        self.assertEquals('杜甫', p['author'])
        self.assertEquals('春望', p['title'])

    def test_get_rhymes(self):
        p = poem.Poem(paragraphs=self.poem)
        self.assertEquals(['深', '心', '金', '簪'], p.get_rhymes())
