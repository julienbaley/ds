import unittest
from collections import Counter

from ds import graph


class TestGraph(unittest.TestCase):
    def setUp(self):
        self.poem = ['國破山河在',
                     '城春草木深',
                     '感時花濺淚',
                     '恨別鳥驚心',
                     '峰火連三月',
                     '家書抵萬金',
                     '白頭搔更短',
                     '渾欲不勝簪']

    @staticmethod
    def grouping_fun(p):
        return [[line[-1] for line in p[1::2]]]  # all even lines rhyme

    def test_build_single_poem_graph(self):
        nodes, edges = graph.build_single_poem_graph(self.poem,
                                                     self.grouping_fun)

        self.assertEquals(Counter('深心金簪'), nodes)
        self.assertEquals(Counter({('簪', '金'): 1,
                                   ('心', '深'): 1,
                                   ('心', '簪'): 1,
                                   ('心', '金'): 1,
                                   ('深', '金'): 1,
                                   ('深', '簪'): 1}),
                          edges)

    def test_build_python_graph(self):
        p_nodes, p_edges = graph.build_single_poem_graph(self.poem,
                                                         self.grouping_fun)
        # we build a corpus of twice the same poem
        nodes, edges = graph.build_python_graph([self.poem, self.poem],
                                                self.grouping_fun)
        self.assertEquals(p_nodes + p_nodes, nodes)
        self.assertEquals(p_edges + p_edges, edges)

    def test_py2nx(self):
        nodes, edges = graph.build_single_poem_graph(self.poem,
                                                     self.grouping_fun)
        gph = graph.py2nx(nodes, edges)
        for node, data in gph.nodes(data=True):
            self.assertEquals(nodes[node], data['weight'])
        for a, b, data in gph.edges(data=True):
            self.assertEquals(edges[tuple(sorted((a, b)))], data['weight'])

        self.assertEquals(len(nodes), len(gph.nodes))
        self.assertEquals(len(edges), len(gph.edges))


class TestCommunities(unittest.TestCase):
    def setUp(self):
        self.nodes = {'a': 10, 'wa': 5, 'ia': 5, 'e': 10, 'ie': 5}
        self.edges = {('a', 'wa'): 4,
                      ('a', 'ia'): 4,
                      ('wa', 'ia'): 1,
                      ('e', 'ie'): 5,
                      # although there is a link, it is weak (weight=1) and
                      # only between 2 nodes of the 'a' and 'e' communities
                      ('a', 'e'): 1,
                      }

    def test_get_communities(self):
        nx = graph.py2nx(self.nodes, self.edges)
        comms = graph.get_communities(nx)
        self.assertEquals({frozenset({'a', 'wa', 'ia'}),
                           frozenset({'e', 'ie'})},
                          comms)

    def test_keep_only_communities(self):
        nx = graph.py2nx(self.nodes, self.edges)
        comms = graph.get_communities(nx)
        nx = graph.keep_only_communities(nx, comms)

        self.assertNotIn(('a', 'e'), nx.edges)
        for edge in set(self.edges.keys()) - {('a', 'e')}:
            self.assertIn(edge, nx.edges)

    def test_get_community_graph(self):
        nx = graph.py2nx(self.nodes, self.edges)
        comms = graph.get_communities(nx)

        for comm in comms:
            subgph = graph.get_community_graph(nx, comm)
            self.assertEquals(comm, set(subgph.nodes))
